import os
import pytest
from covid19_outbreak_simulator.cli import parse_args, main
from covid19_outbreak_simulator.model import Params


def test_option_base_plugin_help():
    args = parse_args(['--plugin', '-h'])
    assert args.plugin == ['-h']


def test_option_plugin_help():
    args = parse_args(['--plugin', 'sample', '-h'])
    assert args.plugin == ['sample', '-h']


def test_option_plugin_args():
    args = parse_args(['--plugin', 'sample', '--sample-size', '100'])
    assert args.plugin == ['sample', '--sample-size', '100']


def test_plugin_no_module():
    with pytest.raises(Exception):
        main([
            '--jobs', '1', '--repeats', '100', '--infectors', '1', '--plugin',
            'non-exist'
        ])


def test_plugin_no_module():
    with pytest.raises(Exception):
        main([
            '--jobs', '1', '--repeats', '100', '--infectors', '1', '--plugin',
            'sample.non-exist'
        ])


def test_plugin_trigger():
    main([
        '--jobs', '1', '--repeats', '100', '--infectors', '1', '--plugin',
        'stat', '--trigger-by', 'INFECTION'
    ])


def test_plugin_pre_quarantine():
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
        '--infector', 'A2', 'A7', '--plugin', 'quarantine', 'A2', 'A7',
        '--duration', '7'
    ])


def test_plugin_pre_quarantine_with_proportion():
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine', '1', '2',
        '--duration', '7', '--proportion', '0.8'
    ])


def test_plugin_pre_quarantine_error():
    with pytest.raises((Exception, SystemExit)):
        main([
            '--jobs', '1', '--repeats', '100', '--plugin', 'quarantine', '1',
            '2a', '--duration', '7'
        ])


def test_plugin_stat():
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'stat', '--interval', '1'
    ])


def test_plugin_stat_with_groups():
    main([
        '--jobs', '1', '--popsize', 'A=200', 'B=100', '--repeats', '100',
        '--infectors', 'A0', '--plugin', 'stat', '--interval', '1'
    ])


def test_plugin_sample():
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'sample', '--interval',
        '1', '--proportion', '0.8'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'sample', '--interval',
        '1', '--size', '20'
    ])


def test_plugin_sample_error():
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


def test_plugin_setparam():
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'setparam', '--at', '1',
        '--symptomatic-r0', '0.2'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--plugin', 'setparam', '--at', '1',
        '--asymptomatic-r0', '0.4'
    ])


def test_plugin_insert():
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--plugin',
        'insert', '2', '--at', '1'
    ])
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--plugin',
        'insert', '2', '--interval', '1'
    ])


def test_plugin_insert_hetero_pop():
    main([
        '--jobs', '1', '--repeats', '100', '--stop-if', 't>10', '--popsize',
        'A=100', 'B=100', '--stop-if', 't>10', '--plugin', 'insert', 'A=2',
        '--interval', '1'
    ])


def test_plugin_pcrtest():
    main(['--jobs', '1', '--repeats', '100', '--plugin', 'pcrtest'])
    main(['--jobs', '1', '--repeats', '100', '--plugin', 'pcrtest', '1', '2'])
    main([
        '--jobs', '1', '--repeats', '100', '--popsize', 'A=100', 'B=200',
        '--infector', 'A2', 'A7', '--plugin', 'pcrtest', 'A2', 'A7',
        '--handle-positive', 'quarantine_7'
    ])
