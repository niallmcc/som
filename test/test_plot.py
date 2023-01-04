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
import logging

logging.basicConfig(level=logging.INFO)

from som.plot.svgdoc import SvgDoc
from som.plot.rectangle import Rectangle
from som.plot.hexagon import Hexagon
from som.plot.text import Text
from som.plot.som_plot import SomPlot

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
        ds = xr.open_dataset("test_hexagonal.nc")
        # plt = Plot(ds,color_name="mean_pattern_input")
        plt = SomPlot(ds, color_name="pattern_class")
        plt.plot("test_hexagonal.svg")

    def test_square_plot(self):
        ds = xr.open_dataset("test_square.nc")
        plt = SomPlot(ds, color_name="mean_pattern_input")
        plt.plot("test_square.svg")


