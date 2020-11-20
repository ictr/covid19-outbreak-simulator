#!/usr/bin/env python
"""Tests for `covid19_outbreak_simulator` package."""

import pytest
import math
from scipy.stats import norm
import numpy as np
from covid19_outbreak_simulator.utils import parse_param_with_multiplier

def test_multiplier():
    res = parse_param_with_multiplier(['2', 'A=1.2', 'B=0.8'], subpops=['A', 'B'])
    assert res['A'] == 2*1.2
    assert res['B'] == 2*0.8
    assert len(res) == 2

    res = parse_param_with_multiplier(['2', '3', 'A=1.2', 'B=0.8'], subpops=['A', 'B'])
    assert res['A'] == [2*1.2, 3*1.2]
    assert res['B'] == [2*0.8, 3*0.8]
    assert len(res) == 2

    res = parse_param_with_multiplier(['2', 'A=1.2'], subpops=['A', 'B'])
    assert res['A'] == 2*1.2
    assert res['B'] == 2
    assert len(res) == 2

    res = parse_param_with_multiplier(['2', '=1.2'], subpops=[''])
    assert res[''] == 2*1.2
    assert len(res) == 1

    res = parse_param_with_multiplier(['2', 'all=1.2'], subpops=[''])
    assert res[''] == 2*1.2
    assert len(res) == 1

    res = parse_param_with_multiplier(['2'])
    assert res[''] == 2
    assert len(res) == 1

    res = parse_param_with_multiplier(['2'], subpops=['A', 'B'])
    assert res['A'] == 2
    assert res['B'] == 2
    assert len(res) == 2

    res = parse_param_with_multiplier(['A=1.2', 'B=0.8'], subpops=['A', 'B'], default=2)
    assert res['A'] == 2*1.2
    assert res['B'] == 2*0.8
    assert len(res) == 2

    with pytest.raises(ValueError):
        parse_param_with_multiplier(['112b'], subpops=['A', 'B'])

    with pytest.raises(ValueError):
        parse_param_with_multiplier(['A=1.2', 'B=0.8'], subpops=['A', 'B'])

    with pytest.raises(ValueError):
        parse_param_with_multiplier(['1', 'A=1.2e'], subpops=['A', 'B'])


def test_unknown_param(params):
    with pytest.raises(ValueError):
        params.set('unknown', 'value', '0.3')

    with pytest.raises(ValueError):
        params.set('prop_asym_carriers', 'unknown', '0.3')


def test_params_set_mean(params):
    params.set('prop_asym_carriers', 'loc', 0.3)
    assert params.prop_asym_carriers_loc == 0.3


def test_prop_asym_carriers(params):
    params.set('prop_asym_carriers', prop='loc', value=0.25)
    params.set('prop_asym_carriers', prop='quantile_2.5', value=0.1)

    dist = norm(
        loc=params.prop_asym_carriers_loc,
        scale=params.prop_asym_carriers_scale)

    assert math.fabs(dist.cdf(0.1) - 0.025) < 0.001
    assert math.fabs(dist.cdf(0.4) - 0.975) < 0.001


def test_symptomatic_r0(params):
    params.set('symptomatic_r0', prop='loc', value=2.1)
    params.set('symptomatic_r0', prop='quantile_2.5', value=1.4)

    assert params.symptomatic_r0_loc == 2.1


def test_asymptomatic_r0(params):
    params.set('asymptomatic_r0', prop='loc', value=0.21)
    params.set('asymptomatic_r0', prop='quantile_2.5', value=0.14)

    assert params.asymptomatic_r0_loc == 0.21


def test_draw_prop_asym_carriers(default_model):
    props = []
    for i in range(1000):
        props.append(default_model.draw_prop_asym_carriers())

    assert math.fabs(
        sum(props) / 1000 - default_model.params.prop_asym_carriers_loc) < 0.05


def test_drawn_is_asymptomatic(default_model):
    prop = default_model.draw_prop_asym_carriers()
    is_asymp = []
    for i in range(1000):
        is_asymp.append(default_model.draw_is_asymptomatic())

    assert math.fabs(sum(is_asymp) / 1000) - prop < 0.05


def test_drawn_random_r0(default_model):
    symp_r0 = []
    N = 10000
    for i in range(N):
        symp_r0.append(default_model.draw_random_r0(symptomatic=True))
    #
    assert math.fabs(sum(symp_r0) /
                     N) - default_model.params.symptomatic_r0_loc < 0.005

    asymp_r0 = []
    for i in range(N):
        asymp_r0.append(default_model.draw_random_r0(symptomatic=False))
    #
    assert math.fabs(sum(asymp_r0) / N) - default_model.params.asymptomatic_r0_loc < 0.005


def draw_random_incubation_period(default_model):
    symp_r0 = []
    N = 10000
    for i in range(N):
        symp_r0.append(default_model.draw_random_incubation_period())
    #
    assert math.fabs(sum(symp_r0) / N) - scipy.stats.lognorm.mean(
        s=1,
        loc=default_model.params.incubation_period_mean,
        scale=default_model.params.incubation_period_sigma) < 0.001


def test_get_normal_symptomatic_transmission_probability(default_model):

    incu = default_model.draw_random_incubation_period()
    R0 = default_model.draw_random_r0(symptomatic=True)

    N = 10000
    r = []
    for i in range(N):
        x_grid, prob = default_model.get_symptomatic_transmission_probability(
            incu, R0, default_model.draw_infection_params(symptomatic=True))
        infected = np.random.binomial(1, prob, len(x_grid))
        r.append(sum(infected))
    #
    assert math.fabs(sum(r) / N) - R0 < 0.05


def test_get_normal_asymptomatic_transmission_probability(default_model):

    R0 = default_model.draw_random_r0(symptomatic=False)

    N = 10000
    r = []
    for i in range(N):
        x_grid, prob = default_model.get_asymptomatic_transmission_probability(
            R0, default_model.draw_infection_params(symptomatic=False))
        infected = np.random.binomial(1, prob, len(x_grid))
        r.append(sum(infected))
    #
    assert math.fabs(sum(r) / N) - R0 < 0.05



def test_get_piecewise_symptomatic_transmission_probability(default_model):

    default_model.params.set_symptomatic_transmissibility_model(
        ['piecewise']
    )

    incu = default_model.draw_random_incubation_period()
    R0 = default_model.draw_random_r0(symptomatic=True)

    N = 10000
    r = []
    for i in range(N):
        x_grid, prob = default_model.get_symptomatic_transmission_probability(
            incu, R0, default_model.draw_infection_params(symptomatic=True))
        infected = np.random.binomial(1, prob, len(x_grid))
        r.append(sum(infected))
    #
    assert math.fabs(sum(r) / N) - R0 < 0.05


def test_get_piecewise_asymptomatic_transmission_probability(default_model):

    default_model.params.set_asymptomatic_transmissibility_model(
        ['piecewise']
    )

    R0 = default_model.draw_random_r0(symptomatic=False)

    N = 10000
    r = []
    for i in range(N):
        x_grid, prob = default_model.get_asymptomatic_transmission_probability(
            R0, default_model.draw_infection_params(symptomatic=False))
        infected = np.random.binomial(1, prob, len(x_grid))
        r.append(sum(infected))
    #
    assert math.fabs(sum(r) / N) - R0 < 0.05
