# MIT License
#
# Copyright (c) 2022-2023 Niall McCarroll
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
import numpy as np
import time
import logging
import re

from som.self_organising_map import SelfOrganisingMap, cupy_enabled
from som.progress import Progress

"""This module contains a main program and high level interface to the SOM algorithm"""


class SomRunner:

    def __init__(self, grid_width=10, grid_height=None, hexagonal=False, minibatch_size=1000, iterations=100, verbose=True):
        """
        Train a Self Organising Map (SOM) with cells arranged in a 2-dimensional rectangular layout

        A high level interface to the SOM algorithm

        Keyword Parameters
        ------------------
        grid_width : int
            the width of the SOM grid in cells
        grid_height : int
            the height of the SOM grid in cells
        hexagonal : bool
            whether to use a hexagonal grid
        minibatch_size : int
            divide input data into mini batches and only update weights after each batch
        iterations : int
            the number of training iterations to use when training the SOM
        verbose : bool
            whether to print progress messages to the console
        """
        self.grid_width = grid_width
        self.grid_height = grid_height if grid_height else grid_width
        self.hexagonal = hexagonal
        self.minibatch_size = minibatch_size
        self.iterations = iterations
        self.verbose = verbose
        self.logger = logging.getLogger(SomRunner.__qualname__)
        self.cell_centres = None

    def fit_transform(self, dataset, reduce_dimensions, input_variable_names, output_variable_name="som_assignments",
                      output_variable_xcoords_name="cell_centres_x", output_variable_ycoords_name="cell_centres_y"):
        """
        Fit a SOM model on some input data, and then return the cell assignments for each training case

        Parameters
        ----------
        dataset: xarray.Dataset
            The xarray dataset containing the input data variables to be modelled, and to which the SOM assignments are to be written
        reduce_dimensions: list[str]
            The name(s) of the dimension(s) in the input data to reduce to the SOM assignment.
        input_variable_names: list[str]
            The name(s) of the input variable(s) in the dataset to model
        output_variable_name: str
            The name of the output variable to create with the SOM assignments
        output_variable_xcoords_name: str
            The name of an ancillary variable to create in the dataset, storing the x-coordinates of each cell centre
        output_variable_ycoords_name: str
            The name of an ancillary variable to create in the dataset, storing the y-coordinates of each cell centre

        Returns
        -------
        xarray.DataArray
            Output data containing the original dimensions apart from the along_dimension being replaced with the som_axis dimension of size 2, containing
            the x- and y- locations of the assignments made by the fitted SOM
        """
        progress = None
        progress_callback = None
        self.logger.info("Calling fit_transform, cupy_enabled=%s" % str(cupy_enabled))
        if self.verbose:
            progress = Progress("SOM")

            def progress_callback(m, frac):
                progress.report(m, frac)

        input_sources = []
        for input_variable_name in input_variable_names:
            m = re.match(r"([^\(]+)\(([^\)]+)\)",input_variable_name)
            if m:
                input_sources.append((m.group(2),m.group(1)))
            else:
                input_sources.append((input_variable_name,""))

        def adjust(da,fn):
            if fn:
                if fn == "log10":
                    return np.log10(da)
                elif fn == "log":
                    return np.log(da)
                elif fn == "sqrt":
                    return np.sqrt(da)
                else:
                    raise ValueError(f"Unable to apply unrecognised function {fn}")
            return da

        data_arrays = [adjust(dataset[input_variable_name],fn) for (input_variable_name,fn) in input_sources]
        da = data_arrays[0]
        # work out which dimensions in the input data will be collapsed and replaced
        # with the som_axis dimension (of size 2)

        preserve_dimensions = [dim for dim in da.dims if dim not in reduce_dimensions]
        # the other dimensions will be kept, but stack them into one dimension for running SOM
        # (they will be restored later)
        stack_dims = tuple(preserve_dimensions)
        stack_sizes = tuple([da.shape[da.dims.index(dim)] for dim in preserve_dimensions])

        flattened_arrays = []
        for da in data_arrays:
            mean = da.mean()
            sdev = da.std()
            da = (da - mean) / sdev
            # reduce to a 2D array (case,values)
            da = da.stack(case=stack_dims)
            da = da.transpose("case",*reduce_dimensions)
            da = da.stack(values=tuple(reduce_dimensions))
            flattened_arrays.append(da.values)
        instances = np.concatenate(flattened_arrays,axis=1)

        # run SOM
        som = SelfOrganisingMap(grid_width=self.grid_width, grid_height=self.grid_height, hexagonal=self.hexagonal,
                                iterations=self.iterations, seed=1, verbose=True,
                                minibatch_size=self.minibatch_size, progress_callback=progress_callback)

        # store the coordinates of each cell centre
        cell_centres_x = xr.DataArray(data=som.cell_centres[0,:,:],dims=("grid_x", "grid_y"))
        cell_centres_y = xr.DataArray(data=som.cell_centres[1,:,:], dims=("grid_x", "grid_y"))

        scores = som.fit_transform(instances)
        if progress:
            progress.complete("Fit-Transform completed")

        # restore preserved dimensions and added som_axis
        a = scores.reshape(stack_sizes + (2,))
        new_dims = stack_dims + ("som_axis",)
        self.logger.info("Called fit_transform")
        result_da = xr.DataArray(data=a, dims=new_dims, attrs={
            "grid_width": self.grid_width,
            "grid_height": self.grid_width,
            "iterations": self.iterations,
            "minibatch_size": self.minibatch_size,
            "based_on": ",".join(input_variable_names),
            "layout": "hexagonal" if self.hexagonal else "square"
        })

        # xarray datasets can lose dimension attributes when new dataarrays are assigned.
        # back them up now to be restored later...

        preserve_attrs = {dim: dataset[dim].attrs for dim in preserve_dimensions if dim in dataset}

        # assign the SOM allocated cell coordinates for each input case
        dataset[output_variable_name] = result_da

        # and assign the cell centre x- and y-coordinates to arrays
        if output_variable_xcoords_name:
            dataset[output_variable_xcoords_name] = cell_centres_x
        if output_variable_ycoords_name:
            dataset[output_variable_ycoords_name] = cell_centres_y

        # restore dimension attributes
        for (dim, attrs) in preserve_attrs.items():
            dataset[dim].attrs = attrs



def main():
    # SOM training parameters
    logging.basicConfig(level=logging.INFO)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path",
                        help="the path to an input dataset (in netcdf4 format) containing the data to load")
    parser.add_argument("output_path",
                        help="the path to an output dataset to write the original data+som output to")
    parser.add_argument("--input-variables", nargs="+",
                        help="the names of input variable(s) to use (within an input dataset)",required=True)
    parser.add_argument("--som-variable", help="the name of the output variable to add", default="som_assignments")
    parser.add_argument("--reduce-dimensions", nargs="+",
                        help="the name(s) of dimension(s) in the input data to reduce and replace with the som axis.",
                        default=[])
    parser.add_argument("--grid-width", type=int,
                        help="the width of the map grid", default=10)
    parser.add_argument("--grid-height", type=int,
                        help="the height of the map grid, defaults to the same as the width if not specified",
                        default=None)
    parser.add_argument("--grid-layout",
                        help="set the grid layout to hexagonal or square",
                        default="hexagonal")
    parser.add_argument("--iterations", type=int,
                        help="sets the number of iterations to run "
                             "(in each iteration, all of the input data is used to train the som network)",
                        default=100)
    parser.add_argument("--minibatch-size", type=int,
                        help="sets the number of input data items passed",
                        default=100)

    args = parser.parse_args()
    logging.info("Reading input data from %s" % args.input_path)
    ds = xr.open_dataset(args.input_path)

    input_variables = args.input_variables

    start_time = time.time()
    sr = SomRunner(grid_width=args.grid_width,
                   grid_height=args.grid_height,
                   hexagonal=(args.grid_layout == "hexagonal"),
                   minibatch_size=args.minibatch_size,
                   iterations=args.iterations,verbose=True)
    sr.fit_transform(ds, args.reduce_dimensions, input_variable_names=input_variables,
                     output_variable_name=args.som_variable)
    end_time = time.time()

    logging.info("Elapsed time: %d seconds" % (int(end_time - start_time)))
    ds.to_netcdf(args.output_path)
    logging.info("Written output data to %s" % args.output_path)


if __name__ == '__main__':
    main()
