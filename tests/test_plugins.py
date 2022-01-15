import pytest
from covid19_outbreak_simulator.cli import parse_args, main


def test_option_base_plugin_help(clear_log):
    args = parse_args(['--plugin', '-h'])
    assert args.plugin == ['-h']


def test_option_plugin_help(clear_log):
    args = parse_args(['--plugin', 'sample', '-h'])
    assert args.plugin == ['sample', '-h']


def test_option_plugin_args(clear_log):
    args = parse_args(['--plugin', 'sample', '--sample-size', '100'])
    assert args.plugin == ['sample', '--sample-size', '100']


def test_plugin_no_module(clear_log):
    with pytest.raises(Exception):
        main([
            '--jobs', '1', '--repeats', '100', '--infectors', '1', '--plugin',
            'non-exist'
        ])


def test_plugin_no_module_1(clear_log):
    with pytest.raises(Exception):
        main([
            '--jobs', '1', '--repeats', '100', '--infectors', '1', '--plugin',
            'sample.non-exist'
        ])


def test_plugin_trigger(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--infectors', '1', '--plugin',
        'stat', '--trigger-by', 'INFECTION'
    ])


def test_plugin_quarantine(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine',
        '--duration', '7'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine', '1', '2',
        '--duration', '7'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=200',
        '--infector', 'A_2', 'A_7', '--plugin', 'quarantine', 'A_2', 'A_7',
        '--duration', '7'
    ])

    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine',
        '--duration', '7', '--proportion', '0.8'
    ])

    main([
        '--jobs', '1', '--popsize', 'A=100', 'B=200', '--repeats', '100',
        '--plugin', 'quarantine', '--duration', '7', '--proportion', 'A=1',
        'B=0', '--target', 'all'
    ])

    main([
        '--jobs', '1', '--popsize', 'A=100', 'B=200', '--infector', 'A_10',
        '--repeats', '100', '--plugin', 'quarantine', '--duration', '7',
        '--proportion', 'A=1', 'B=0', '--target', 'infected'
    ])

    main([
        '--jobs', '1', '--popsize', 'A=100', 'B=200', '--infector', 'A_10',
        '--repeats', '100', '--plugin', 'quarantine', '--duration', '7',
        '--proportion', 'A=1', 'B=0', '--target', 'uninfected'
    ])

    main([
        '--jobs', '1', '--popsize', 'A=100', 'B=200', '--infector', 'A_10',
        '--repeats', '100', '--plugin', 'quarantine', '--duration', '7',
        '--count', 'A=10', 'B=20', '--target', 'uninfected'
    ])


def test_plugin_quarantine_error(clear_log):
    with pytest.raises((Exception, SystemExit)):
        main([
            '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine', '1',
            '2a', '--duration', '7'
        ])

    with pytest.raises((Exception, SystemExit)):
        main([
            '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine', '1',
            '2', '--proportion', '0.5'
        ])

    with pytest.raises((Exception, SystemExit)):
        main([
            '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine',
            '--proportion', '0.5', '--target', 'somethingelse'
        ])


def test_plugin_stat(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'stat', '--interval', '1'
    ])


def test_plugin_stat_with_groups(clear_log):
    main([
        '--jobs', '1', '--popsize', 'A=200', 'B=100', '--repeats', '100',
        '--infectors', 'A_0', '--plugin', 'stat', '--interval', '1'
    ])


def test_plugin_init(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'init', '--at', '0',
        '--incidence-rate', '0.01'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=200',
        '--plugin', 'init', '--at', '0', '--incidence-rate', '1', 'A=0.01',
        'B=0.02', '--leadtime', 'any'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=200',
        '--plugin', 'init', '--at', '0', '--incidence-rate', '1', 'A=0.01',
        'B=0.02', '--seroprevalence', '1', 'A=0.02', 'B=0.04', '--leadtime',
        'asymptomatic'
    ])


def test_plugin_sample(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'sample', '--interval',
        '1', '--proportion', '0.8'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'sample', '--interval',
        '1', '--size', '20'
    ])


def test_plugin_sample_error(clear_log):
    with pytest.raises((Exception, SystemExit)):
        main([
            '--jobs', '1', '--repeats', '100', '--plugin', 'sample',
            '--interval', '1'
        ])

    with pytest.raises((Exception, SystemExit)):
        main([
            '--jobs', '1', '--repeats', '100', '--plugin', 'sample',
            '--interval', '1', '--proportion', 'a'
        ])

    with pytest.raises((Exception, SystemExit)):
        main([
            '--jobs', '1', '--repeats', '100', '--plugin', 'sample',
            '--interval', '1', '--size', '20', '--proportion', '0.5'
        ])


def test_plugin_setparam(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'setparam', '--at', '1',
        '--symptomatic-r0', '0.2'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'setparam', '--at', '1',
        '--asymptomatic-r0', '0.4'
    ])


def test_plugin_insert(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--plugin',
        'insert', '2', '--at', '1'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--plugin',
        'insert', '2', '--interval', '1'
    ])


def test_plugin_remove(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--plugin',
        'remove', '--count', '2', '--at', '1', '--target', 'all'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=100',
        '--stop-if', 't>10', '--plugin', 'remove', '--count', 'A=2', '--interval', '1', '--target', 'all'
    ])


def test_plugin_replace(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--plugin',
        'replace', '--count', '2', '--at', '1', '--target', 'all', '--keep', 'vaccinated'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=100',
        '--stop-if', 't>10', '--plugin', 'replace', '--count', 'A=2', '--interval', '1', '--target', 'all'
    ])

def test_plugin_community_infection(clear_log):
    main([
        '--jobs', '1', '--repeats', '10', '--stop-if', 't>4', '--plugin',
        'community_infection', '--probability', '0.0001', '--interval', '1'
    ])
    main([
        '--jobs', '1', '--repeats', '10', '--popsize', 'A=100', 'B=200',
        '--stop-if', 't>4', '--plugin', 'community_infection', '--probability',
        '1', 'A=0.0001', '--interval', '1'
    ])
    main([
        '--jobs', '1', '--repeats', '10', '--popsize', 'A=100', 'B=200',
        '--stop-if', 't>4', '--plugin', 'community_infection', '--probability',
        '1', 'A=0.0001', '--probability', '0.5', 'A=0.0001', '--at', '1', '2'
    ])

def test_plugin_insert_hetero_pop(clear_log):
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--popsize',
        'A=100', 'B=100', '--stop-if', 't>10', '--plugin', 'insert', 'A=2',
        '--interval', '1'
    ])


def test_plugin_testing_error(clear_log):
    with pytest.raises(Exception):
        main(['--jobs', '1', '--repeats', '100', '--plugin', 'testing'])

def test_plugin_testing(clear_log):
    main(['--jobs', '1', '--repeats', '100', '--plugin', 'testing', '--target', 'all'])

    main(['--jobs', '1', '--repeats', '100', '--plugin', 'testing', '1', '2'])

    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=200',
        '--infector', 'A_2', 'A_7', '--handle-symptomatic', 'keep', '--plugin', 'testing', 'A_2', 'A_7',
        '--at', '3', '--handle-positive', 'quarantine@duration=14'
    ])

    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'testing', '1', '2',
        '--turnaround-time', '2'
    ])

    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'testing', '1', '2',
        '--turnaround-time', '2', '--target', 'infected'
    ])


def test_plugin_vaccinate(clear_log):
    main(['--jobs', '1', '--repeats', '100', '--plugin', 'vaccinate'])

    main(['--jobs', '1', '--repeats', '100', '--plugin', 'vaccinate', '1', '2'])

    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=200',
        '--infector', 'A_2', 'A_7', '--plugin', 'vaccinate', 'A_2', 'A_7',
        '--infectivity', '0.5'
    ])

    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'vaccinate', '1', '2',
        '--immunity', '0.7'
    ])
