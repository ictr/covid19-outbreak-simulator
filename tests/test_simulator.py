import os
import pytest
from covid19_outbreak_simulator.cli import parse_args, main
from covid19_outbreak_simulator.model import Params


def test_option_popsize():
    args = parse_args(["--popsize", "500"])
    params = Params(args)
    assert list(params.groups.keys()) == [""]

    args = parse_args(["--popsize", "A=500", "B=300"])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ["A", "B"]

    args = parse_args(["--popsize", "A=500", "B=300"])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ["A", "B"]

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "500", "300"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "50A"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "all=100"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "500", "A=300", "A=200"])
        params = Params(args)


def test_option_susceptibility():
    args = parse_args(
        ["--popsize", "A=500", "B=300", "--susceptibility", "A=0.8"])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ["A", "B"]

    assert params.susceptibility_multiplier_A == 0.8
    with pytest.raises(AttributeError):
        params.susceptibility_multiplier_B

    # group does not exist
    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=500", "B=300", "--susceptibility", "C=0.8"])
        params = Params(args)

    # not float
    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=500", "B=300", "--susceptibility", "A=1f"])
        params = Params(args)

    args = parse_args(
        ["--popsize", "A=500", "B=300", "--susceptibility", "0.8"])
    params = Params(args)


def test_option_symptomatic_r0():
    args = parse_args(["--symptomatic-r0", "1.0"])
    params = Params(args)
    assert params.symptomatic_r0_loc == 1.0
    assert params.symptomatic_r0_scale == 0

    args = parse_args(["--symptomatic-r0", "1.2", "2.0"])
    params = Params(args)
    assert params.symptomatic_r0_loc == (1.2 + 2.0) / 2

    args = parse_args(
        ["--popsize", "A=500", "B=300", "--symptomatic-r0", "1.5", "A=0.8"])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ["A", "B"]
    assert params.symptomatic_r0_loc == 1.5
    assert params.symptomatic_r0_scale == 0
    assert params.symptomatic_r0_multiplier_A == 0.8

    # not float number
    with pytest.raises(ValueError):
        args = parse_args(["--symptomatic-r0", "1.0f"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--symptomatic-r0", "0.8a", "1.0"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--symptomatic-r0", "0.8", "1.0f"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "A=200", "--symptomatic-r0", "A=8b"])
        params = Params(args)

    # more numbers
    with pytest.raises(ValueError):
        args = parse_args(["--symptomatic-r0", "0.8", "1.0", "2.0"])
        params = Params(args)


def test_option_asymptomatic_r0():
    args = parse_args(["--asymptomatic-r0", "1.0"])
    params = Params(args)
    assert params.asymptomatic_r0_loc == 1.0
    assert params.asymptomatic_r0_scale == 0

    args = parse_args(["--asymptomatic-r0", "1.2", "2.0"])
    params = Params(args)
    assert params.asymptomatic_r0_loc == (1.2 + 2.0) / 2

    args = parse_args(
        ["--popsize", "A=500", "B=300", "--asymptomatic-r0", "1.5", "A=0.8"])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ["A", "B"]
    assert params.asymptomatic_r0_loc == 1.5
    assert params.asymptomatic_r0_scale == 0
    assert params.asymptomatic_r0_multiplier_A == 0.8

    # not float number
    with pytest.raises(ValueError):
        args = parse_args(["--asymptomatic-r0", "1.0f"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--asymptomatic-r0", "0.8a", "1.0"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--asymptomatic-r0", "0.8", "1.0f"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "A=200", "--asymptomatic-r0", "A=8b"])
        params = Params(args)

    # more numbers
    with pytest.raises(ValueError):
        args = parse_args(["--asymptomatic-r0", "0.8", "1.0", "2.0"])
        params = Params(args)


def test_option_inclubation_period():
    with pytest.raises(ValueError):
        args = parse_args(["--incubation-period", "1.0"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--incubation-period", "1.0", "2.0"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--incubation-period", "uniform", "1.0", "2.0"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=100", "B=200", "--incubation-period", "C=0.8"])
        params = Params(args)

    args = parse_args(["--incubation-period", "normal", "1.2", "2.0"])
    params = Params(args)
    assert params.incubation_period_loc == 1.2
    assert params.incubation_period_scale == 2.0

    args = parse_args(["--incubation-period", "lognormal", "1.", "2.5"])
    params = Params(args)
    assert params.incubation_period_mean == 1.0
    assert params.incubation_period_sigma == 2.5

    args = parse_args(
        ["--popsize", "A=500", "B=300", "--incubation-period", "A=0.8"])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ["A", "B"]
    assert params.incubation_period_multiplier_A == 0.8

    args = parse_args([
        "--popsize",
        "A=500",
        "B=300",
        "--incubation-period",
        "normal",
        "5",
        "2",
        "B=0.95",
        "A=1.13",
    ])
    params = Params(args)
    assert sorted(list(params.groups.keys())) == ["A", "B"]
    assert params.incubation_period_loc == 5.0
    assert params.incubation_period_scale == 2.0
    assert params.incubation_period_multiplier_A == 1.13
    assert params.incubation_period_multiplier_B == 0.95

    with pytest.raises(ValueError):
        args = parse_args([
            "--popsize",
            "A=500",
            "B=300",
            "--incubation-period",
            "normal",
            "5",
            "2.3p",
        ])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args([
            "--popsize",
            "A=500",
            "B=300",
            "--incubation-period",
            "normal",
            "5",
            "2.3p",
            "A=1.4p",
        ])
        params = Params(args)

    # negative multiplier
    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=500", "B=300", "--incubation-period", "A=-1"])
        params = Params(args)

    # non-float multiplier
    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=500", "B=300", "--incubation-period", "A=1f"])
        params = Params(args)


def test_option_infectors():
    args = parse_args(["--infectors", "10"])
    params = Params(args)

    args = parse_args(
        ["--popsize", "A=10", "B=10", "--infectors", "A_1", "B_2"])
    params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "A=10", "B=10", "--infectors", "1"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=10", "B=10", "--infectors", "C_1", "C_2"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(["--popsize", "A=10", "B=10", "--infectors", "A_10"])
        params = Params(args)


def test_option_prop_asym_carriers():
    args = parse_args(["--prop-asym-carriers", "0.1"])
    params = Params(args)
    assert params.prop_asym_carriers_loc == 0.1
    assert params.prop_asym_carriers_scale == 0.0

    args = parse_args(["--prop-asym-carriers", "0.1", "0.3"])
    params = Params(args)
    assert params.prop_asym_carriers_loc == 0.2

    # not a float number
    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=10", "B=10", "--prop-asym-carriers", "1.2f"])
        params = Params(args)

    # not incremental
    with pytest.raises(ValueError):
        args = parse_args([
            "--popsize", "A=10", "B=10", "--prop-asym-carriers", "1.5", "0.5"
        ])
        params = Params(args)

    # more numbers
    with pytest.raises(ValueError):
        args = parse_args([
            "--popsize", "A=10", "B=10", "--prop-asym-carriers", "1.5", "2.5",
            "3.5"
        ])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=10", "B=10", "--prop-asym-carriers", "C=1.2"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=10", "B=10", "--prop-asym-carriers", "A=-1.2"])
        params = Params(args)

    with pytest.raises(ValueError):
        args = parse_args(
            ["--popsize", "A=10", "B=10", "--prop-asym-carriers", "A=1.2f"])
        params = Params(args)

    args = parse_args(
        ["--popsize", "A=10", "B=10", "--prop-asym-carriers", "A=1.2"])
    params = Params(args)
    assert params.prop_asym_carriers_multiplier_A == 1.2


def test_main_default():
    main(["--jobs", "1", "--repeats", "100"])
    main(["--jobs", "1", "--repeats", "100", "--logfile", "test.out"])
    assert os.path.isfile("test.out")
    main(["--logfile", "test.out"])


def test_main_symptomatic():
    main(["--jobs", "1", "--repeats", "100", "--symptomatic-r0", "1.0"])
    main(["--jobs", "1", "--repeats", "100", "--symptomatic-r0", "1.0", "2.0"])


def test_main_asymptomatic():
    main(["--jobs", "1", "--repeats", "100", "--asymptomatic-r0", "0.5"])
    main(
        ["--jobs", "1", "--repeats", "100", "--asymptomatic-r0", "0.5", "1.5"])
    main([
        "--jobs",
        "1",
        "--repeats",
        "100",
        "--popsize",
        "A=100",
        "B=50",
        "--asymptomatic-r0",
        "0.5",
        "1.5",
        "A=1.2",
        "--infector",
        "A_0",
    ])


def test_main_incubation_period():
    main([
        "--jobs",
        "1",
        "--repeats",
        "100",
        "--incubation-period",
        "lognormal",
        "1",
        "0.2",
    ])
    main([
        "--jobs", "1", "--repeats", "100", "--incubation-period", "normal",
        "1", "2"
    ])


def test_main_susceptibility():
    main([
        "--jobs",
        "1",
        "--repeats",
        "10",
        "--popsize",
        "A=100",
        "B=200",
        "--susceptibility",
        "A=0.08",
        "B=1",
        "--infectors",
        "B_1",
        "B_2",
    ])


def test_main_stop_if():
    main(["--jobs", "1", "--repeats", "100", "--stop-if", "t>1"])


def test_main_stop_if_error():
    with pytest.raises(Exception):
        main(["--jobs", "1", "--repeats", "100", "--stop-if", "st>1"])


def test_symptomatic_transmissibility_model(clear_log):
    with pytest.raises(Exception):
        main([
            "--jobs",
            "1",
            "--repeats",
            "100",
            "--symptomatic-transmissibility-model",
            "unknown",
        ])

    with pytest.raises(Exception):
        main([
            "--jobs",
            "1",
            "--repeats",
            "100",
            "--symptomatic-transmissibility-model",
            "piecewise",
            "0.1",
        ])

    main([
        "--jobs",
        "1",
        "--repeats",
        "100",
        "--symptomatic-transmissibility-model",
        "piecewise",
        "0.2",
        "0.7",
        "3",
        "0.59",
        "1.14",
    ])


def test_asymptomatic_transmissibility_model(clear_log):
    with pytest.raises(Exception):
        main([
            "--jobs",
            "1",
            "--repeats",
            "100",
            "--asymptomatic-transmissibility-model",
            "unknown",
        ])

    with pytest.raises(Exception):
        main([
            "--jobs",
            "1",
            "--repeats",
            "100",
            "--asymptomatic-transmissibility-model",
            "piecewise",
            "0.1",
        ])

    main([
        "--jobs",
        "1",
        "--repeats",
        "100",
        "--asymptomatic-transmissibility-model",
        "piecewise",
        "0.1",
        "0.3",
        "3",
        "0.5",
        "1.147",
    ])
