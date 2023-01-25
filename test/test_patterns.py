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
import logging
import tempfile

logging.basicConfig(level=logging.INFO)

"""This module supports unit tests for the som package"""

class TestPatterns:

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
        labels = []
        rng = random.Random(seed)
        offsets = [2 * math.pi * pattern / nr_patterns for pattern in range(nr_patterns)]
        amps = [1 + 0.5 * rng.random() for _ in range(nr_patterns)]
        for i in range(nr_cases):
            labels.append(f"case{i}")
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
        ds["pattern_label"] = xr.DataArray(data=np.array(labels),dims=("j",))
        ds["mean_pattern_input"] = ds["pattern_input"].mean(dim=("i",))
        return ds

    def generate_pattern1_to_file(nr_cases=1000, case_length=50, noise_weight=0.5):
        ds = TestPatterns.generate_pattern1(nr_cases=nr_cases, case_length=case_length, noise_weight=noise_weight)
        tf = tempfile.NamedTemporaryFile(suffix="_test.nc", delete=False)
        ds.to_netcdf(tf.name)
        return tf.name

