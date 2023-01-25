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

import tempfile
import os
import unittest
import logging

from test.test_patterns import TestPatterns

logging.basicConfig(level=logging.INFO)

"""This module implements unit tests for the som package"""

class TestCmdLine(unittest.TestCase):

    def test_run(self):
        """Check that SOM can be invoked from the command line"""
        try:
            fn = TestPatterns.generate_pattern1_to_file(nr_cases=1000, case_length=50, noise_weight=0.5)
            out_fn = tempfile.NamedTemporaryFile(suffix="_test.nc").name
            retcode = os.system(f"python -m som.som_runner {fn} {out_fn} --input-variables pattern_input --som-variable som_assignments --iterations 100 --grid-layout=hexagonal --grid-width 8 --grid-height 8 --reduce-dimensions i")
            self.assertEqual(retcode,0)
            self.assertTrue(os.path.exists(out_fn))
            out_svg_fn = tempfile.NamedTemporaryFile(suffix="_test.svg").name
            retcode = os.system(f"python -m som.som_plotter {out_fn} {out_svg_fn} --som-variable som_assignments")
            self.assertEqual(retcode, 0)
            self.assertTrue(os.path.exists(out_svg_fn))
        finally:
            os.remove(fn)
            os.remove(out_fn)
            os.remove(out_svg_fn)

