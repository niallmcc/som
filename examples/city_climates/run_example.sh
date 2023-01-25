#!/bin/bash

# run Self-Organising Maps, 10x10 hexagonal grid, cluster cities by monthly mean temperature patterns
# output the original data plus som assignments to city_som_hex.nc

somrun city_climatologies.nc city_som_hex.nc \
  --input-variables t2m --som-variable som_assignment --minibatch-size 200 --iterations 5000 \
  --grid-layout=hexagonal --grid-width 10 --grid-height 10 --reduce-dimensions month

# plot SOM map assignments to SVG, and generate a CSV file with SOM assignments and temperature values

somplot city_som_hex.nc city_som_hex_t2m.svg \
  --csv city_som_hex_t2m.csv --som-variable som_assignment --svg-plot-color-variable t2m \
  --svg-plot-color-variable-min 5 --svg-plot-color-variable-max 26 --svg-plot-colors=lightblue,red \
  --svg-plot-label-variable city_name --svg-plot-default-color white
