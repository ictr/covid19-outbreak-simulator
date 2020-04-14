
import os
import pytest
from covid19_outbreak_simulator.cli import parse_args, main
from covid19_outbreak_simulator.model import Params

def test_option_popsize():
    args = parse_args(['--popsize', '500'])
    params = Params(args)
    assert list(params.groups.keys()) == ['']

    args = parse_args(['--popsize', 'A=500', 'B=300'])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ['A', 'B']

    args = parse_args(['--popsize', 'A=500', 'B=300'])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ['A', 'B']

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', '500', '300'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', '50A'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', '500', 'A=300', 'A=200'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', '500', 'A6=300'])
        params = Params(args)

def test_option_susceptibility():
    args = parse_args(['--popsize', 'A=500', 'B=300', '--susceptibility', 'A=0.8'])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ['A', 'B']

    assert params.susceptibility_multiplier_A == 0.8
    with pytest.raises(AttributeError):
        params.susceptibility_multiplier_B

    # group does not exist
    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=500', 'B=300', '--susceptibility', 'C=0.8'])
        params = Params(args)

def test_option_symptomatic_r0():
    args = parse_args(['--symptomatic-r0', '1.0'])
    params = Params(args)
    assert params.symptomatic_r0_low == 1.0
    assert params.symptomatic_r0_high == 1.0

    args = parse_args(['--symptomatic-r0', '1.2', '2.0'])
    params = Params(args)
    assert params.symptomatic_r0_low == 1.2
    assert params.symptomatic_r0_high == 2.0

    args = parse_args(['--popsize', 'A=500', 'B=300',
         '--symptomatic-r0', '1.5', 'A=0.8'])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ['A', 'B']
    assert params.symptomatic_r0_low == 1.5
    assert params.symptomatic_r0_high == 1.5
    assert params.symptomatic_r0_multiplier_A == 0.8

def test_option_asymptomatic_r0():
    args = parse_args(['--asymptomatic-r0', '1.0'])
    params = Params(args)
    assert params.asymptomatic_r0_low == 1.0
    assert params.asymptomatic_r0_high == 1.0

    args = parse_args(['--asymptomatic-r0', '1.2', '2.0'])
    params = Params(args)
    assert params.asymptomatic_r0_low == 1.2
    assert params.asymptomatic_r0_high == 2.0

    args = parse_args(['--popsize', 'A=500', 'B=300',
         '--asymptomatic-r0', '1.5', 'A=0.8'])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ['A', 'B']
    assert params.asymptomatic_r0_low == 1.5
    assert params.asymptomatic_r0_high == 1.5
    assert params.asymptomatic_r0_multiplier_A == 0.8

def test_option_inclubation_period():
    with pytest.raises(ValueError):
        args = parse_args(['--incubation-period', '1.0'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--incubation-period', '1.0', '2.0'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--incubation-period', 'uniform', '1.0', '2.0'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=100', 'B=200',
            '--incubation-period', 'C=0.8'])
        params = Params(args)

    args = parse_args(['--incubation-period', 'normal', '1.2', '2.0'])
    params = Params(args)
    assert params.incubation_period_loc == 1.2
    assert params.incubation_period_scale == 2.0

    args = parse_args(['--incubation-period', 'lognormal', '1.', '2.5'])
    params = Params(args)
    assert params.incubation_period_mean == 1.
    assert params.incubation_period_sigma == 2.5

    args = parse_args(['--popsize', 'A=500', 'B=300',
         '--incubation-period', 'A=0.8'])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ['A', 'B']
    assert params.incubation_period_multiplier_A == 0.8

    args = parse_args(['--popsize', 'A=500', 'B=300',
        '--incubation-period', 'normal', '5', '2', 'B=0.95', 'A=1.13'])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ['A', 'B']
    assert params.incubation_period_loc == 5.0
    assert params.incubation_period_scale == 2.0
    assert params.incubation_period_multiplier_A == 1.13
    assert params.incubation_period_multiplier_B == 0.95

def test_option_pre_quarantine():
    args = parse_args(['--pre-quarantine', '10'])
    params = Params(args)

    args = parse_args(['--popsize', 'A=10', 'B=10',
         '--pre-quarantine', '10', 'A1', 'B2'])
    params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=10', 'B=10',
             '--pre-quarantine', '10', '1'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=10', 'B=10',
             '--pre-quarantine', '10', 'C1', 'C2'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=10', 'B=10',
             '--pre-quarantine', '10', 'A10'])
        params = Params(args)

def test_option_infectors():
    args = parse_args(['--infectors', '10'])
    params = Params(args)

    args = parse_args(['--popsize', 'A=10', 'B=10',
         '--infectors', 'A1', 'B2'])
    params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=10', 'B=10',
             '--infectors', '1'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=10', 'B=10',
             '--infectors', 'C1', 'C2'])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(['--popsize', 'A=10', 'B=10',
             '--infectors', 'A10'])
        params = Params(args)

def test_main_default():
    main(['--jobs', '1', '--repeats', '100'])
    main(['--jobs', '1', '--repeats', '100', '--logfile', 'test.out'])
    assert os.path.isfile('test.out')
    main(['--analyze-existing-logfile', '--logfile', 'test.out'])

def test_main_symptomatic():
    main(['--jobs', '1', '--repeats', '100', '--symptomatic-r0', '1.0'])
    main(['--jobs', '1', '--repeats', '100', '--symptomatic-r0', '1.0', '2.0'])

def test_main_asymptomatic():
    main(['--jobs', '1', '--repeats', '100', '--asymptomatic-r0', '0.5'])
    main(['--jobs', '1', '--repeats', '100', '--asymptomatic-r0', '0.5', '1.5'])
    main(['--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=50',
        '--asymptomatic-r0', '0.5', '1.5', 'A=1.2', '--infector', 'A0'])

def test_main_pre_quarantine():
    main(['--jobs', '1', '--repeats', '100', '--pre-quarantine', '7'])
    main(['--jobs', '1', '--repeats', '100', '--pre-quarantine', '7', '1', '2'])
    main(['--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=200',
        '--pre-quarantine', '7', 'A2', 'A7',  '--infector', 'A2', 'A7'])

def test_main_incubation_period():
    main(['--jobs', '1', '--repeats', '100', '--incubation-period', 'lognormal', '1', '0.2'])
    main(['--jobs', '1', '--repeats', '100', '--incubation-period', 'normal', '1', '2'])

