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

import unittest
import logging

from test.test_patterns import TestPatterns
from som.plot.pysvg import SvgDoc, Rectangle, Hexagon, Text
from som.som_plotter import SomPlot
from som.som_runner import SomRunner

logging.basicConfig(level=logging.INFO)


"""This module implements unit tests for the som package"""


class TestPlot(unittest.TestCase):

    def test_basic(self):
        """Check that basic shapes can be plotted"""
        doc = SvgDoc(100,100,"px",100,100)
        doc.add(Rectangle(10,10,20,20,fill="rgb(255,0,0)",stroke="rgb(0,0,0)",stroke_width=1))
        doc.add(Text(50,50,"Hello",font_height=10))
        doc.add(Hexagon(70,70,10,fill="rgb(0,255,0)",stroke="rgb(0,0,0)",stroke_width=1))
        with open("plot.svg","w") as f:
            f.write(doc.render())

    def test_hexagonal_plot(self):
        ds = TestPatterns.generate_pattern1(nr_cases=1000, case_length=50, noise_weight=0.5)
        grid_width, grid_height = 10, 10
        iterations = 50

        runner = SomRunner(iterations=iterations, grid_width=grid_width,
                               grid_height=grid_height, hexagonal=True)
        runner.fit_transform(ds,reduce_dimensions=["i"],input_variable_names=["pattern_input"])

        plt = SomPlot(ds, color_name="pattern_input")
        plt.plot("test_hexagonal.svg")

    def test_square_plot(self):
        ds = TestPatterns.generate_pattern1(nr_cases=1000, case_length=50, noise_weight=0.5)
        grid_width, grid_height = 10, 10
        iterations = 50

        runner = SomRunner(iterations=iterations, grid_width=grid_width,
                           grid_height=grid_height, hexagonal=False)
        runner.fit_transform(ds, reduce_dimensions=["i"], input_variable_names=["pattern_input"])

        plt = SomPlot(ds, color_name="pattern_input")
        plt.plot("test_square.svg")


if __name__ == '__main__':
    unittest.main()
