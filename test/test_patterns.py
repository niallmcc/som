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

import numpy as np
import xarray as xr
import math
import random
import unittest

from som.som_runner import SomRunner

"""This module implements unit tests for the som package"""


class TestPatterns(unittest.TestCase):

    @staticmethod
    def generate_pattern1(seed=1, nr_patterns=5, nr_cases=1000, case_length=100, noise_weight=0.1):
        """
        Generate set of cases based on a number of distinct sinusoidal patterns with equal periods
        but a different phase and amplitude

        Arguments
        ---------
        seed: int
            seed to intitialise a random number generator
        nr_patterns: int
            the number of different patterns to generate
        nr_cases: int
            the number of distributions to generate
        case_length: int
            the length of each case
        noise_weight: float
            weight of random noise to inject into each data point

        Returns
        -------
        xarray.Dataset
            an xarray dataset, with "pattern_input" holding the distributions organised by (nr_cases,case_length)
        """
        arr = np.zeros(shape=(nr_cases, case_length))
        pat = np.zeros(shape=(nr_cases,))
        rng = random.Random(seed)
        offsets = [2 * math.pi * pattern / nr_patterns for pattern in range(nr_patterns)]
        amps = [1 + 0.5 * rng.random() for _ in range(nr_patterns)]
        for i in range(nr_cases):
            pattern = rng.choice(range(nr_patterns))
            noise = np.array([rng.random() * noise_weight for _ in range(case_length)])
            arr[i, :] = np.array(
                [amps[pattern] * math.cos(offsets[pattern] + j / case_length * 2 * math.pi) for j in
                 range(case_length)])
            arr[i, :] += noise
            pat[i] = pattern
        ds = xr.Dataset()
        ds["pattern_input"] = xr.DataArray(data=arr, dims=("j", "i"))
        ds["pattern_class"] = xr.DataArray(data=pat, dims=("j",))
        return ds

    def test_data_generation(self):
        ds = TestPatterns.generate_pattern1(nr_cases=1000, case_length=50, noise_weight=0.5)
        ds.to_netcdf("synthetic_test_data.nc")

    def test_separation_basic(self):
        """Check that SOM can separate classes, given some distinct distributions"""
        ds = TestPatterns.generate_pattern1(nr_cases=1000, case_length=50, noise_weight=0.5)
        grid_width, grid_height = 10, 10
        runner = SomRunner(iterations=100, grid_width=grid_width,
                           grid_height=grid_height)
        cluster_da = runner.fit_transform(["j"], ds["pattern_input"])
        assignments = self.__get_class_assignments(ds, cluster_da)
        non_separations, summary_text = self.__summarise_class_assignments(assignments, grid_width, grid_height)
        print(summary_text)
        self.assertTrue(non_separations == 0)

    @staticmethod
    def __get_class_assignments(input_ds, output_da):
        """
        From the DataArray output from fit_transform, extract a dict
        mapping from (x,y) locations on the SOM grid to a dict recording class frequencies
        of the cases assigned to that location
        """
        assignments = {}
        for i in range(0, 100):
            xy = output_da.values[i, :]
            x = int(xy[0])
            y = int(xy[1])
            cls = int(input_ds["pattern_class"].values[i])
            if (x, y) not in assignments:
                assignments[(x, y)] = {}
            if cls not in assignments[(x, y)]:
                assignments[(x, y)][cls] = 0
            assignments[(x, y)][cls] += 1
        return assignments

    @staticmethod
    def __summarise_class_assignments(assignments, grid_width, grid_height):
        """Analyse a dictionary returned by __get_class_assignments, return the number of
        grid cells where multiple input classes were matched (non-separations) and a text
        summary of the grid showing which (if any) class was matched to each grid cell"""
        summary_text = ""
        non_separations = 0
        for x in range(grid_width):
            row = ""
            for y in range(grid_height):
                if (x, y) not in assignments:
                    row += "."
                else:
                    classes = assignments[(x, y)]
                    if len(classes) > 2:
                        row += "?"
                        non_separations += 1
                    else:
                        cls = list(classes.keys())[0]
                        row += str(cls)
            summary_text += row + "\n"
        return non_separations, summary_text
