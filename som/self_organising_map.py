# MIT License
#
# Copyright (c) 2022 Niall McCarroll
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
try:
    # if cupy is available, use that in place of numpy to run on GPU
    import cupy as np
    import cupyx
    cupy_enabled = True
except:
    import numpy as np
    cupy_enabled = False

"""This module contains the code for training self-organising maps using numpy or cupy"""


def find_bmu(instances, weights):
    """
    Find the best matching units for a set of instances within the SOM network
    using cartesian distances

    Parameters
    ----------
    instances:
        2-dimensional array of instances organised by (case,instance-index)
    weights:
        ndarray describing the SOM network weights organised by (unit-index,instance-index)

    Returns
    -------
        1-dimensional array organised by (case,) providing the best matching unit for each case
    """
    sqdiffs = (instances[:, :, None] - np.transpose(weights)) ** 2
    sumsqdiffs = sqdiffs.sum(axis=1)
    return sumsqdiffs.argmin(axis=1)


def train_batch(instances, weights, learn_rate, neighbourhood_lookup):
    """
    Train a batch of instances, and update the network weights, modifying the weights array

    Parameters
    ----------
    instances:
        2-dimensional ndarray of instances organised by (case,instance-index)
    weights:
        2-dimensional ndarray describing the SOM network weights organised by (unit-index,instance-index)
    learn_rate:
        a fraction that controls how fast the network is modified
    neighbourhood_lookup:
        a 2-d ndarray mask organised by (unit-index,unit-index) where the value at (M,N)
        indicates if and by how much the unit at index N
        is considered to be a neighbour of the activated unit at index M
    """

    # winners(#instances) holds the index of the closest weight for each instance
    winners = find_bmu(instances, weights)
    # now find the neighbours of each winner that are also activated by each instance
    # nhoods(#activations,2) holds the instance index and the weight index for each activation
    nwinners = neighbourhood_lookup[winners, :]
    nhoods = np.argwhere(nwinners)

    # get the indices
    weight_indices = nhoods[:, 1]
    instance_indices = nhoods[:, 0]
    fractions = nwinners[instance_indices, weight_indices]

    # get the updates
    updates = -learn_rate * fractions[:, None] * (weights[weight_indices, :] - instances[instance_indices])

    # aggregate the updates for each weight
    numerator = np.zeros(shape=weights.shape)
    if cupy_enabled:
        # cupy does not support numpy.add.at but cupyx.scatter_add does what we need here
        cupyx.scatter_add(numerator, weight_indices, updates)
    else:
        np.add.at(numerator, weight_indices, updates)

    denominator = np.zeros(shape=weights.shape[:1])[:, None]
    if cupy_enabled:
        cupyx.scatter_add(denominator, weight_indices, 1)
    else:
        np.add.at(denominator, weight_indices, 1)
    denominator = np.where(numerator == 0, 1, denominator)  # fix annoying divide by zero warning
    weight_updates = numerator / denominator

    # update the weights
    weights += weight_updates


def compute_scores(instances, weights, grid_width, minibatch_size):
    """
    Computes the scores for a set of instances

    Parameters
    ----------
    instances:
        2-dimensional ndarray of instances organised by (case,instance-index)
    weights:
        2-dimensional ndarray describing the SOM network weights organised by (unit-index,instance-index)
    grid_width:
        the width of the SOM network
    minibatch_size:
        the number of instances to score in a single call

    Returns
    -------
    ndarray orgainsed by (case,2) where the second dimension holds the
    """
    index = 0
    nr_instances = instances.shape[0]
    batch_size = nr_instances if not minibatch_size else minibatch_size
    bmus = np.zeros(shape=(nr_instances,), dtype=int)
    while index < nr_instances:
        last_index = min(index + batch_size, nr_instances)
        bmus[index:last_index] = find_bmu(instances[index:last_index], weights)
        index += batch_size
    scores = np.vstack([bmus % grid_width, bmus // grid_width])
    return np.transpose(scores)


class SelfOrganisingMap(object):
    """
    Train a Self Organising Map (SOM) with cells arranged in a 2-dimensional rectangular layout

    A lower-level (numpy-based) interface to the SOM algorithm

    Keyword Parameters
    ------------------
    iterations : int
        the number of training iterations to use when training the SOM
    grid_width : int
        the width of the SOM grid in cells
    grid_height : int
        the height of the SOM grid in cells
    initial_neighbourhood : int
        the initial neighbourhood size as a radius in terms of numbers of cells.  Defaults to grid_width/2 if not given.
    verbose : bool
        whether to print progress messages
    seed : int
        random seed - set to produce repeatable results
    minibatch_size : int
        divide input data into mini batches and only update weights after each batch
    progress_callback: function
        a callback that takes string, float parameters, called when each iteration completes
    """

    def __init__(self, grid_width=10, grid_height=10, iterations=100, initial_neighbourhood=None, verbose=False,
                 seed=None,
                 minibatch_size=None, progress_callback=None):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.minibatch_size = minibatch_size
        self.nr_outputs = self.grid_width * self.grid_height
        self.iterations = iterations
        self.minibatch_size = minibatch_size
        self.progress_callback = progress_callback

        self.initial_neighbourhood = initial_neighbourhood if initial_neighbourhood else int(self.grid_width / 2)
        self.verbose = verbose
        self.seed = seed
        self.rng = random.Random()
        if seed:
            self.rng.seed(seed)

        self.learn_rate_initial = 0.01
        self.learn_rate_final = 0.001
        self.neighbourhood_lookup = np.zeros(shape=(self.initial_neighbourhood + 1, self.nr_outputs, self.nr_outputs))

        # for each neighbourhood size 0,1,...initial_neighbourhood
        # build a lookup table where the fraction at neighbourhood_lookup[n,o1,o2]
        # indicates if (and how much) weight at index o2 is a neighbour of the weight
        # at index o1 in neighbourhood size n
        # use 1 and 0 for a binary mask, or between -1.0 and 1.0 for a varying mask

        for neighbourhood in range(0, self.initial_neighbourhood + 1):
            nsq = neighbourhood ** 2
            indices = np.indices((self.grid_width, self.grid_height))
            x_coords = indices[0].flatten()
            y_coords = indices[1].flatten()
            x_combinations = np.meshgrid(x_coords, x_coords)
            y_combinations = np.meshgrid(y_coords, y_coords)
            x_diffs = np.diff(x_combinations, axis=0)
            y_diffs = np.diff(y_combinations, axis=0)
            sqdists = x_diffs ** 2 + y_diffs ** 2
            self.neighbourhood_lookup[neighbourhood, :, :] = np.where(sqdists <= nsq, 1, 0)

    def report_progress(self, message, fraction_complete):
        if self.progress_callback:
            self.progress_callback(message, fraction_complete)

    def fit_transform(self, original_instances):
        """
        Train the SOM network on input data

        Arguments
        ---------
        original_instances: numpy.ndarray(nr-cases,case-length)
            The input data cases for training the network

        Returns
        -------
        numpy.ndarray(cases,2)
            The x- and y- locations in the trained SOM best matching each training case
        """


        if cupy_enabled:
            original_instances = np.asarray(original_instances)
            if self.seed:
                np.random.seed(self.seed)
        # mask out instances containing NaNs and remove them
        instance_mask = ~np.any(np.isnan(original_instances), axis=1)
        nr_original_instances = original_instances.shape[0]
        valid_instances = original_instances[instance_mask, :]

        # randomly re-shuffle the remaining instances.
        # TODO consider reshuffling after every iteration?
        instances = np.copy(valid_instances)
        np.random.shuffle(instances)

        nr_inputs = instances.shape[1]
        nr_instances = instances.shape[0]

        weights = np.zeros((self.nr_outputs, nr_inputs))
        for output_idx in range(0, self.nr_outputs):
            weights[output_idx, :] = instances[self.rng.choice(range(0, nr_instances)), :]

        progress_frac = 0.0
        self.report_progress("Starting", progress_frac)

        for iteration in range(self.iterations):
            # reduce the learning rate and neighbourhood size linearly as training progresses
            learn_rate = self.learn_rate_initial - (self.learn_rate_initial - self.learn_rate_final) * (
                    (iteration + 1) / self.iterations)
            neighbour_limit = round(self.initial_neighbourhood * (1 - (iteration + 1) / self.iterations))
            neighbourhood_mask = self.neighbourhood_lookup[neighbour_limit, :, :]
            batch_size = nr_instances if not self.minibatch_size else self.minibatch_size

            index = 0
            while index < nr_instances:
                last_index = min(index + batch_size, nr_instances)
                train_batch(instances[index:last_index, :], weights, learn_rate, neighbourhood_mask)
                index += batch_size

            progress_frac = iteration / self.iterations
            self.report_progress("Training neighbourhood=%d" % neighbour_limit, progress_frac)

        # compute final scores from the trained weights
        valid_scores = compute_scores(valid_instances, weights, self.grid_width, self.minibatch_size)

        # restore the results into the same order as the input array
        scores = np.zeros(shape=(nr_original_instances, 2))
        scores[:, :] = np.nan
        scores[instance_mask, :] = valid_scores
        return np.asnumpy(scores) if cupy_enabled else scores
