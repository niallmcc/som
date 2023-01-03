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
import logging

from som.self_organising_map import SelfOrganisingMap, cupy_enabled
from som.progress import Progress
from som.plot.plot import Plot

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
            the x- and y- locations of the assignments made by the fitted SOM
        """
        progress = None
        progress_callback = None
        self.logger.info("Calling fit_transform, cupy_enabled=%s" % str(cupy_enabled))
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

        # run SOM
        som = SelfOrganisingMap(grid_width=self.grid_width, grid_height=self.grid_height, hexagonal=self.hexagonal,
                                iterations=self.iterations, seed=1, verbose=True,
                                minibatch_size=self.minibatch_size, progress_callback=progress_callback)

        # store the coordinates of each cell centre
        print(som.cell_centres.shape)
        self.cell_centres_x = xr.DataArray(data=som.cell_centres[0,:,:],dims=("grid_x", "grid_y"))
        self.cell_centres_y = xr.DataArray(data=som.cell_centres[1,:,:], dims=("grid_x", "grid_y"))

        scores = som.fit_transform(instances)
        if progress:
            progress.complete("Fit-Transform completed")

        # restore preserved dimensions and added som_axis
        a = scores.reshape(stack_sizes + (2,))
        new_dims = stack_dims + ("som_axis",)
        self.logger.info("Called fit_transform")
        return xr.DataArray(data=a, dims=new_dims, attrs={
            "grid_width": self.grid_width,
            "grid_height": self.grid_width,
            "iterations": self.iterations,
            "minibatch_size": self.minibatch_size,
            "layout": "hexagonal" if self.hexagonal else "square"
        })

    def get_cell_centres(self):
        """
        Get an xarray.DataArrays containing the x- and y-coordinates of each cell centre respectively
        :return: (cell-centre-x-coords, cell-centre-y-coords)
        """
        return (self.cell_centres_x, self.cell_centres_y)


def main():
    # SOM training parameters
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
    parser.add_argument("--hexagonal", action="store_true",
                        help="whether to use a hexagonal grid, offsetting the centers of each cell in odd numbered rows",
                        default=None)
    parser.add_argument("--iterations", type=int,
                        help="sets the number of iterations to run "
                             "(in each iteration, all of the input data is used to train the som network)",
                        default=100)
    parser.add_argument("--minibatch-size", type=int,
                        help="sets the number of input data items passed",
                        default=100)

    # plotting related options
    parser.add_argument("--svg-plot-path", type=str,
                        help="plot the SOM assignments to a SVG file",
                        default="")
    parser.add_argument("--svg-plot-color-variable", type=str,
                        help="the name of a variable to use to color the plotted cells, or 'freq'",
                        default="freq")
    parser.add_argument("--svg-plot-color-variable-min", type=float,
                        help="minimum value for the cell color variable",
                        default=None)
    parser.add_argument("--svg-plot-color-variable-max", type=float,
                        help="maximum value for the cell color variable",
                        default=None)
    parser.add_argument("--svg-plot-label-variable", type=str,
                       help="the name of a variable to use to plot cases on the map",
                       default="")
    parser.add_argument("--svg-plot-colors", type=str,
                        help="comma separated list of colors",
                        default="blue,red")
    parser.add_argument("--svg-plot-default-color", type=str,
                        help="color to use for empty cells",
                        default="#A0A0A0")

    args = parser.parse_args()
    logging.info("Reading input data from %s" % args.input_path)
    ds = xr.open_dataset(args.input_path)
    input_da = ds[args.input_variable]

    start_time = time.time()
    sr = SomRunner(grid_width=args.grid_width,
                   grid_height=args.grid_height, hexagonal=args.hexagonal,
                   minibatch_size=args.minibatch_size,
                   iterations=args.iterations,verbose=True)
    result_da = sr.fit_transform(tuple(args.preserve_dimensions), input_da)
    end_time = time.time()

    # xarray datasets can lose dimension attributes when new dataarrays are assigned.
    # back them up now to be restored later...
    preserve_attrs = {dim: ds[dim].attrs for dim in args.preserve_dimensions if dim in ds}

    # assign the SOM allocated cell coordinates for each input case
    ds[args.output_variable] = result_da

    # and assign the cell centres
    (cell_x, cell_y) = sr.get_cell_centres()
    ds["cell_centres_x"] = cell_x
    ds["cell_centres_y"] = cell_y

    # restore dimension attributes
    for (dim, attrs) in preserve_attrs.items():
        ds[dim].attrs = attrs

    logging.info("Elapsed time: %d seconds" % (int(end_time - start_time)))
    ds.to_netcdf(args.output_path)
    logging.info("Written output data to %s" % args.output_path)

    if args.svg_plot_path:
        plt = Plot(ds,
                   label_name=args.svg_plot_label_variable,
                   som_name=args.output_variable,
                   cell_x_name="cell_centres_x",
                   cell_y_name="cell_centres_y",
                   color_name=args.svg_plot_color_variable,
                   colors=args.svg_plot_colors.split(","),
                   color_value_min=args.svg_plot_color_variable_min,
                   color_value_max=args.svg_plot_color_variable_max,
                   default_color=args.svg_plot_default_color)
        plt.plot(args.svg_plot_path)
        logging.info("Written output plot to %s" % args.svg_plot_path)



if __name__ == '__main__':
    main()
