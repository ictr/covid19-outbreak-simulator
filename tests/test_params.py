#!/usr/bin/env python
"""Tests for `covid19_outbreak_simulator` package."""

import pytest
import math
from scipy.stats import norm

from covid19_outbreak_simulator.model import Params


def test_params_set_mean():
    params = Params()

    params.set('proportion_of_asymptomatic_carriers', 'loc', 0.3)
    assert params.proportion_of_asymptomatic_carriers_loc == 0.3


def test_proportion_of_asymptomatic_carriers():
    params = Params()

    params.set('proportion_of_asymptomatic_carriers', prop='loc', value=0.25)
    params.set('proportion_of_asymptomatic_carriers', prop='quantile_2.5', value=0.1)

    dist = norm(
        loc=params.proportion_of_asymptomatic_carriers_loc,
        scale=params.proportion_of_asymptomatic_carriers_scale)

    assert math.fabs(dist.cdf(0.1) - 0.025) < 0.001
    assert math.fabs(dist.cdf(0.4) - 0.975) < 0.001


def test_symptomatic_r0():
    params = Params()

    params.set('symptomatic_r0', prop='low', value=1.4)
    params.set('symptomatic_r0', prop='high', value=2.8)

    assert params.symptomatic_r0_low == 1.4
    assert params.symptomatic_r0_high == 2.8

def test_asymptomatic_r0():
    params = Params()

    params.set('asymptomatic_r0', prop='low', value=0.14)
    params.set('asymptomatic_r0', prop='high', value=0.28)

    assert params.asymptomatic_r0_low == 0.14
    assert params.asymptomatic_r0_high == 0.28