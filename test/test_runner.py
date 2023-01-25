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
import sys

import numpy as np
import xarray as xr
import math
import random
import unittest
import logging

from test.test_patterns import TestPatterns

logging.basicConfig(level=logging.INFO)

from som.som_runner import SomRunner

"""This module implements unit tests for the som package"""

class TestRunner(unittest.TestCase):

    def test_separation_basic(self):
        """Check that SOM can separate classes, given some distinct distributions"""
        ds = TestPatterns.generate_pattern1(nr_cases=1000, case_length=50, noise_weight=0.5)
        grid_width, grid_height = 10, 10
        iterations = 50

        for hexagonal in [False,True]:
            runner = SomRunner(iterations=iterations, grid_width=grid_width,
                               grid_height=grid_height, hexagonal=hexagonal)
            runner.fit_transform(ds,reduce_dimensions=["i"],input_variable_names=["pattern_input"])
            assignments = self.__get_class_assignments(ds)
            non_separations, summary_text = self.__summarise_class_assignments(assignments, grid_width, grid_height, hexagonal)
            print(summary_text)
            self.assertTrue(non_separations == 0)

    @staticmethod
    def __get_class_assignments(ds):
        """
        From the Dataset output from fit_transform, extract a dict
        mapping from (x,y) locations on the SOM grid to a dict recording class frequencies
        of the cases assigned to that location
        """
        da = ds["som_assignments"]
        assignments = {}
        for i in range(0, 100):
            xy = da.values[i, :]
            x = int(xy[0])
            y = int(xy[1])
            cls = int(ds["pattern_class"].values[i])
            if (x, y) not in assignments:
                assignments[(x, y)] = {}
            if cls not in assignments[(x, y)]:
                assignments[(x, y)][cls] = 0
            assignments[(x, y)][cls] += 1
        return assignments

    @staticmethod
    def __summarise_class_assignments(assignments, grid_width, grid_height, hexagonal):
        """Analyse a dictionary returned by __get_class_assignments, return the number of
        grid cells where multiple input classes were matched (non-separations) and a text
        summary of the grid showing which (if any) class was matched to each grid cell"""
        summary_text = ""
        non_separations = 0
        for y in range(grid_height):
            row = ""
            if hexagonal and y % 2 == 1:
                row += " "
            for x in range(grid_width):
                if (x, y) not in assignments:
                    row += ". "
                else:
                    classes = assignments[(x, y)]
                    if len(classes) > 2:
                        row += "? "
                        non_separations += 1
                    else:
                        cls = list(classes.keys())[0]
                        row += str(cls)+" "
            summary_text += row + "\n"
        return non_separations, summary_text
