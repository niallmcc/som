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


import xarray as xr
import time

from som.self_organising_map import SelfOrganisingMap
from som.progress import Progress

"""This module contains a main program and high level interface to the SOM algorithm"""


class SomRunner:

    def __init__(self, grid_width=10, grid_height=None, minibatch_size=1000, iterations=100, verbose=True):
        """
        Train a Self Organising Map (SOM) with cells arranged in a 2-dimensional rectangular layout

        A high level interface to the SOM algorithm

        Keyword Parameters
        ------------------
        grid_width : int
            the width of the SOM grid in cells
        grid_height : int
            the height of the SOM grid in cells
        minibatch_size : int
            divide input data into mini batches and only update weights after each batch
        iterations : int
            the number of training iterations to use when training the SOM
        verbose : bool
            whether to print progress messages to the console
        """
        self.grid_width = grid_width
        self.grid_height = grid_height if grid_height else grid_width
        self.minibatch_size = minibatch_size
        self.iterations = iterations
        self.verbose = verbose

    def fit_transform(self, preserve_dimensions, da):
        """
        Fit a SOM model on some input data, and then return the cell assignments for each training case

        Parameters
        ----------
        preserve_dimensions: tuple or list
            The names of the dimensions in the input data to preserve.  Must contain at least one dimension.
        da: xarray.DataArray
            The input data

        Returns
        -------
        xarray.DataArray
            Output data containing the preserved dimensions plus a new som_axis dimension of size 2, containing
            the x- and y- locations of the assigments made by the fitted SOM
        """
        progress = None
        progress_callback = None
        if self.verbose:
            progress = Progress("SOM")

            def progress_callback(m, frac):
                progress.report(m, frac)

        # work out which dimensions in the input data will be collapsed and replaced
        # with the som_axis dimension (of size 2)
        collapse_dimensions = [dim for dim in da.dims if dim not in preserve_dimensions]
        # the other dimensions will be kept, but stack them into one dimension for running SOM
        # (they will be restored later)
        stack_dims = tuple(preserve_dimensions)
        stack_sizes = tuple([da.shape[da.dims.index(dim)] for dim in preserve_dimensions])

        instances = da.stack(case=stack_dims).transpose("case", *collapse_dimensions).values

        # run SOM to reduce time dimension from 12 to 2
        som = SelfOrganisingMap(grid_width=self.grid_width, grid_height=self.grid_height,
                                iterations=self.iterations, seed=1, verbose=True,
                                minibatch_size=self.minibatch_size, progress_callback=progress_callback)

        scores = som.fit_transform(instances)
        if progress:
            progress.complete("Fit-Transform completed")

        # restore preserved dimensions and added som_axis
        a = scores.reshape(stack_sizes + (2,))
        new_dims = stack_dims + ("som_axis",)
        return xr.DataArray(data=a, dims=new_dims)


def main():
    # SOM training parameters
    import logging
    logging.basicConfig(level=logging.INFO)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path",
                        help="the path to an input xarray dataset (in netcdf4 format) containing the data to load")
    parser.add_argument("input_variable", help="the name of an input variable to select (within an input dataset)")
    parser.add_argument("output_path",
                        help="the path to an output xarray dataset to write the original data+som output to")
    parser.add_argument("output_variable", help="the name of the output variable to add")
    parser.add_argument("--preserve-dimensions", nargs='+',
                        help="the name of dimension(s) in the input data to preserve.  "
                             "The other dimensions will be replaced by the som_axis dimension with size 2.",
                        required=True)
    parser.add_argument("--grid-width", type=int,
                        help="the width of the map grid", default=10)
    parser.add_argument("--grid-height", type=int,
                        help="the height of the map grid, defaults to the same as the width if not specified",
                        default=None)
    parser.add_argument("--iterations", type=int,
                        help="sets the number of iterations to run "
                             "(in each iteration, all of the input data is used to train the som network)",
                        default=100)
    parser.add_argument("--minibatch_size", type=int,
                        help="sets the number of input data items passed",
                        default=100)

    args = parser.parse_args()
    logging.info("Reading input data from %s" % args.input_path)
    input_ds = xr.open_dataset(args.input_path)
    input_da = input_ds[args.input_variable]

    start_time = time.time()
    sr = SomRunner(grid_width=args.grid_width,
                   grid_height=args.grid_height, minibatch_size=args.minibatch_size,
                   iterations=args.iterations,verbose=True)
    result_da = sr.fit_transform(tuple(args.preserve_dimensions), input_da)

    preserve_attrs = {dim: input_ds[dim].attrs for dim in args.preserve_dimensions if dim in input_ds}
    input_ds[args.output_variable] = result_da
    for (dim, attrs) in preserve_attrs.items():
        input_ds[dim].attrs = attrs
    end_time = time.time()
    logging.info("Elapsed time: %d seconds" % (int(end_time - start_time)))
    input_ds.to_netcdf(args.output_path)
    logging.info("Written outptut data to %s" % args.output_path)



if __name__ == '__main__':
    main()
