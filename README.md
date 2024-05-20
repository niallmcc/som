# som

A prototype implementation of Teuvo Kohonen's Self Organising Maps [(wikipedia page)](https://en.wikipedia.org/wiki/Self-organizing_map)  in python based on numpy

## LICENSE

This code is released under the [MIT license](LICENSE)

## Acknowledgements

Nicola Martin contributed code to use the CUPY library to run this code on GPU

## Quick Example

This tool can make some nice plots - if you like hexagons:

From this [Blog Post](https://blogs.reading.ac.uk/weather-and-climate-at-reading/2023/from-urumqi-to-minneapolis-clustering-city-climates-with-self-organising-maps/):

![image](https://github.com/niallmcc/som/assets/58978249/9af43e1a-00d5-4a9a-9748-76d39f403e33)

## Installation

Clone this repo and install it into a new conda environment (requires conda or miniconda)

```
$ git clone https://github.com/niallmcc/som.git
$ cd som
$ conda env create -f environment.yml
$ conda activate som_env
$ pip install .
```

To run faster on GPUs, consider installing the [CuPy library](https://cupy.dev/).  
See [CuPy Requirements and Installation](https://docs.cupy.dev/en/stable/install.html) for more information.

## Examples

* City Climates Example [examples/city_climates](examples/city_climates/README.md)

## Running via the command line tool `somrun`, use `--help` to list options

```
$ somrun --help
usage: somrun [-h] --input-variables INPUT_VARIABLES [INPUT_VARIABLES ...]
              [--output-variable OUTPUT_VARIABLE]
              [--reduce-dimensions REDUCE_DIMENSIONS [REDUCE_DIMENSIONS ...]]
              [--grid-width GRID_WIDTH] [--grid-height GRID_HEIGHT]
              [--hexagonal] [--iterations ITERATIONS]
              [--minibatch-size MINIBATCH_SIZE]
              input_path output_path

positional arguments:
  input_path            the path to an input dataset (in netcdf4 format)
                        containing the data to load
  output_path           the path to an output dataset to write the original
                        data+som output to

optional arguments:
  -h, --help            show this help message and exit
  --input-variables INPUT_VARIABLES [INPUT_VARIABLES ...]
                        the names of input variable(s) to use (within an input
                        dataset)
  --output-variable OUTPUT_VARIABLE
                        the name of the output variable to add
  --reduce-dimensions REDUCE_DIMENSIONS [REDUCE_DIMENSIONS ...]
                        the name(s) of dimension(s) in the input data to
                        reduce and replace with the som axis.
  --grid-width GRID_WIDTH
                        the width of the map grid
  --grid-height GRID_HEIGHT
                        the height of the map grid, defaults to the same as
                        the width if not specified
  --hexagonal           whether to use a hexagonal grid, offsetting the
                        centers of each cell in odd numbered rows
  --iterations ITERATIONS
                        sets the number of iterations to run (in each
                        iteration, all of the input data is used to train the
                        som network)
  --minibatch-size MINIBATCH_SIZE
                        sets the number of input data items passed
```

## Plotting SOM assignments output from somrun using somplot, use `--help` to list options

```
$ somplot --help
usage: somplot [-h] [--csv-path CSV_PATH] [--som-variable SOM_VARIABLE] [--svg-plot-color-variable SVG_PLOT_COLOR_VARIABLE]
               [--svg-plot-color-variable-min SVG_PLOT_COLOR_VARIABLE_MIN] [--svg-plot-color-variable-max SVG_PLOT_COLOR_VARIABLE_MAX]
               [--svg-plot-label-variable SVG_PLOT_LABEL_VARIABLE] [--svg-plot-colors SVG_PLOT_COLORS] [--svg-plot-default-color SVG_PLOT_DEFAULT_COLOR]
               input_path svg_plot_path

positional arguments:
  input_path            the path to an input xarray dataset (in netcdf4 format) containing the data to load
  svg_plot_path         plot the SOM assignments to a SVG file

optional arguments:
  -h, --help            show this help message and exit
  --csv-path CSV_PATH   Record CSV to accompany plot
  --som-variable SOM_VARIABLE
                        the name of the variable containing th som assignments
  --svg-plot-color-variable SVG_PLOT_COLOR_VARIABLE
                        the name of a variable to use to color the plotted cells, or 'freq'
  --svg-plot-color-variable-min SVG_PLOT_COLOR_VARIABLE_MIN
                        minimum value for the cell color variable
  --svg-plot-color-variable-max SVG_PLOT_COLOR_VARIABLE_MAX
                        maximum value for the cell color variable
  --svg-plot-label-variable SVG_PLOT_LABEL_VARIABLE
                        the name of a variable to use to plot cases on the map
  --svg-plot-colors SVG_PLOT_COLORS
                        comma separated list of colors
  --svg-plot-default-color SVG_PLOT_DEFAULT_COLOR
                        color to use for empty cells
```

## Train SOMs using high or low level APIs

The higher level API in [som.som_runner.SomRunner](som/som_runner.py) processes xarray Datasets

The lower level API in [som.self_organisng_map.SelfOrganisingMap](som/self_organising_map.py) operates on numpy arrays
and offers more fine-grained control of some training options

See the docstrings in these APIs for more information
