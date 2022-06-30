# som

A prototype implementation of Teuvo Kohonen's Self Organising Maps [(wikipedia page)](https://en.wikipedia.org/wiki/Self-organizing_map)  in python based on numpy

## LICENSE

This code is released under the [MIT license](LICENSE)

## Acknowledgements

Nicola Martin contributed code to use the CUPY library to run this code on GPU

## Installation

Clone this repo and install it into a new conda environment (requires conda or miniconda)

```
$ git clone https://github.com/niallmcc/som.git
$ cd som
$ conda env create -f environment.yml
$ conda activate som_env
$ pip install .
```

To run faster on GPUs, consider installing the [CuPy library](https://cupy.dev/).  If CuPy is installed 
See [CuPy Requirements and Installation](https://docs.cupy.dev/en/stable/install.html) for more information.


## Running via the command line tool `somrun`

Run SOM on some simple (synthetic) provided test data, and write the results to a netcdf4 file `test_results.nc` 

```
$ somrun test/synthetic_test_data.nc pattern_input test_results.nc som_assignments --iterations=50 --preserve-dimensions j
```

A full list of options is shown by running `somrun --help`

```
$ somrun --help
usage: somrun [-h] --preserve-dimensions PRESERVE_DIMENSIONS
              [PRESERVE_DIMENSIONS ...] [--grid-width GRID_WIDTH]
              [--grid-height GRID_HEIGHT] [--iterations ITERATIONS]
              [--minibatch_size MINIBATCH_SIZE]
              input_path input_variable output_path output_variable

positional arguments:
  input_path            the path to an input xarray dataset (in netcdf4
                        format) containing the data to load
  input_variable        the name of an input variable to select (within an
                        input dataset)
  output_path           the path to an output xarray dataset to write the
                        original data+som output to
  output_variable       the name of the output variable to add

options:
  -h, --help            show this help message and exit
  --preserve-dimensions PRESERVE_DIMENSIONS [PRESERVE_DIMENSIONS ...]
                        the name of dimension(s) in the input data to
                        preserve. The other dimensions will be replaced by the
                        som_axis dimension with size 2.
  --grid-width GRID_WIDTH
                        the width of the map grid
  --grid-height GRID_HEIGHT
                        the height of the map grid, defaults to the same as
                        the width if not specified
  --iterations ITERATIONS
                        sets the number of iterations to run (in each
                        iteration, all of the input data is used to train the
                        som network)
  --minibatch_size MINIBATCH_SIZE
                        sets the number of input data items passed
```

## Train SOMs using high or low level APIs

The higher level API in [som.som_runner.SomRunner](som/som_runner.py) processes xarray Datasets

The lower level API in [som.self_organisng_map.SelfOrganisingMap](som/self_organising_map.py) operates on numpy arrays
and offers more fine grained control of some training options

See the docstrings in these APIs for more information