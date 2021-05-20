"""Console script for covid19_outbreak_simulator."""
import argparse
import multiprocessing
import sys
from io import StringIO
import os
from datetime import datetime
import subprocess

import numpy as np
from tqdm import tqdm

from .model import Params, summarize_model
from .simulator import Simulator, load_plugins
from .report import summarize_simulations


def parse_args(args=None):
    parser = argparse.ArgumentParser('outbreak_simulator')
    parser.add_argument(
        '--popsize',
        default=['64'],
        nargs='+',
        help='''Size of the population, including the infector that
        will be introduced at the beginning of the simulation. It should be specified
        as a single number, or a serial of name=size values for different groups. For
        example "--popsize nurse=10 patient=100". The names will be used for setting
        group specific parameters. The IDs of these individuals will be nurse0, nurse1
        etc. ''')
    parser.add_argument(
        '--track-events',
        nargs='+',
        help='''List events to track, default to track all events. Event START and ERROR
        will always be tracked.'''
    )
    parser.add_argument(
        '--vicinity',
        nargs='*',
        help='''Number of "neighbors" from group "B" for individuals in
        aubpopulation "A", specified as "A-B=n". For example, "A-A=0" avoids infection
        within group "A", "A-A=10 A-B=5" will make infections twiece as likely
        to happen within group A then to group B, regardless of size of
        groups A and B. As specifial cases, 'A=10` etc refers to cases when
        infection happens from outside of the simulated population (community
        infection), and "*", "?" and "[]" (range) can be used to refer to multiple
        groups using the same rules as filename expansion, and !name as "not".'''
    )
    parser.add_argument(
        '--susceptibility',
        nargs='+',
        help='''Probability of being infected if an infection event happens, default to 1.
            With options such as "--susceptibility nurse=0.8 patients=1" you can model a scenario
            when nurses are better prepared and protected than patients.''')
    parser.add_argument(
        '--symptomatic-r0',
        nargs='+',
        help='''Production number of symptomatic infectors, should be specified as a single
            fixed number, or 2.5%% and 97.5%% quantile of a normal distribution from which individual
            production number will be drawn. Multipliers are allowed to adjust impact of social
            distancing or mask for each group. This parameter reflects the infectivity of virus
            carrier measured by the average number of individuals one infected individual "would"
            infect if infectivity is not blocked by for example quarantine and susceptibility of
            infectees. Note that viral loads are only affected by baseline R0, not multipliers.'''
    )
    parser.add_argument(
        '--asymptomatic-r0',
        nargs='+',
        help='''Production number of asymptomatic infectors, should be specified as a single
            fixed number or or 2.5%% and 97.5%% quantile of a normal distribution from which individual
            production number will be drawn. Multipliers are allowed to specify asymptomatic r0 for
            each group.''')
    parser.add_argument(
        '--symptomatic-transmissibility-model',
        nargs='+',
        default=['piecewise'],
        help='''Model used for asymptomatic cases with parameters. The default model
            normal has a duration of 8 days after incubation, and a peak happens at 2/3 of
            incubation. An alternative piece wise model has a stage of no infectivity, a stage
            for increasing and a stage for decreasing infectivity. The proportion of stages
            and time after incubation period are controlled by a lognormal distribution.
            Parameters to this model could be specified but not recommended.
        '''
    )
    parser.add_argument(
        '--asymptomatic-transmissibility-model',
        nargs='+',
        default=['piecewise'],
        help='''Model used for asymptomatic cases with parameters. The default model
            normal has a duration of 12 and peaks at 4.8 day. The piecewise model has
            a stage of no infectivity, a stage for increasing and a stage for decreasing
            infectivity. The proportion of stages and the overall duration are controlled
            by a lognormal distribution. Parameters to this model could be specified but
            not recommended.
        '''
    )

    parser.add_argument(
        '--incubation-period',
        nargs='+',
        help='''Incubation period period, should be specified as "lognormal" followed by two
            numbers as mean and sigma, or "normal" followed by mean and sd. Multipliers are
            allowed to specify incubation period for each group. Default to
            "lognormal 1.621 0.418"'''
    )
    parser.add_argument(
        '--repeats',
        default=100,
        type=int,
        help='''Number of replicates to simulate. An ID starting from
              1 will be assinged to each replicate and as the first columns
              in the log file.''')
    parser.add_argument(
        '--resume',
        action='store_true',
        help='''If true, resume from last interrupted simulations. Existing logfile will not
            be erased if exists. Note that this option does not check if the previous simulations
            use the same options, or if they have corrected completed.''')
    parser.add_argument(
        '--handle-symptomatic',
        nargs='*',
        help='''How to handle individuals who show symptom, which should be "keep" (stay in
            population), "remove" (remove from population), "replace" (reset its infection status
            so that the individual is susceptible again), and "quarantine" (put aside until
            it recovers). all options can be followed by a "proportion", and quarantine can
            be specified as "quarantine_7" etc to specify duration of quarantine. Default to
            "remove", meaning all symptomatic cases will be removed from population.'''
    )
    parser.add_argument(
        '--infectors',
        nargs='*',
        help='''Infectees to introduce to the population. If you
            would like to introduce multiple infectees to the population, or if
            you have named groups, you will have to specify the IDs of carrier
            such as --infectors nurse_1 nurse_2.''')
    parser.add_argument(
        '--interval',
        default=1 / 24,
        help='Interval of simulation, default to 1/24, by hour')
    parser.add_argument('--logfile', default='simulation.log', help='logfile')

    parser.add_argument(
        '--prop-asym-carriers',
        nargs='*',
        help='''Proportion of asymptomatic cases. You can specify a fix number, or two
        numbers as the lower and higher CI (95%%) of the proportion. Default to 0.10 to 0.40.
        Multipliers can be specified to set proportion of asymptomatic carriers
        for particular groups.''')
    parser.add_argument(
        '--stop-if',
        nargs='*',
        help='''Condition at which the simulation will end. By default the simulation
            stops when all individuals are affected or all infected individuals
            are removed. Current you can specify a time after which the simulation
            will stop in the format of `--stop-if "t>10"' (for 10 days).''')
    parser.add_argument(
        '--leadtime',
        help='''With "leadtime" infections are assumed to happen before the simulation.
            This option can be a fixed positive number `t` when the infection happens
            `t` days before current time. If can also be set to 'any' for which the
            carrier can be any time during its course of infection, or `asymptomatic`
            for which the leadtime is adjust so that the carrier does not show any
            symptom at the time point (in incubation period for symptomatic case).
            All events triggered before current time are ignored.''')
    parser.add_argument(
        '--plugin',
        nargs=argparse.REMAINDER,
        help='''One or more of "--plugin MODULE.PLUGIN [args]" to specify one or more
            plugins. FLUGIN will be assumed to be MODULE name if left unspecified. Each
            plugin has its own parser and can parse its own args.''')
    parser.add_argument(
        '-j',
        '--jobs',
        type=int,
        help='Number of process to use for simulation. Default to number of CPU cores.'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='Print version information'
    )
    parser.add_argument(
        '--summarize-model',
        action='store_true',
        help='''If specified, output key statistics calculated such as mean serial interval directly
            from model parameters. No simulation will actually be executed if this parameter is
            specified.'''
    )
    parser.add_argument(
        '--summary-report',
        help='''Generate a summary report and write to the specified file,
          which can be "-" for standard output.'''
    )
    parser.add_argument(
        '--sensitivity',
        nargs='+',
        type=float,
        default=[1.0],
        help=argparse.SUPPRESS
    )
    return parser.parse_args(args)

class FilteredStringIO(StringIO):
    def __init__(self, track_events=None):
        super(FilteredStringIO, self).__init__()
        self._track_events = track_events
        if self._track_events is not None:
            self._track_events = set(self._track_events)
            for evt in ('START', 'ERROR', 'END'):
                if evt not in self._track_events:
                    self._track_events.add(evt)


    def write(self, text):
        if not self._track_events or text.split('\t')[1] in self._track_events:
            super(FilteredStringIO, self).write(text)

class Worker(multiprocessing.Process):

    def __init__(self, task_queue, result_queue, args, cmd):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.params = Params(args)
        self.simu_args = args
        self.cmd = cmd

    def run(self):
        # set random seed to a random number
        np.random.seed()

        while True:
            id = self.task_queue.get()
            if id is None:
                self.task_queue.task_done()
                break
            with FilteredStringIO(track_events = self.simu_args.track_events) as logger:
                simu = Simulator(
                    params=self.params,
                    logger=logger,
                    simu_args=self.simu_args,
                    cmd=self.cmd)
                try:
                    simu.simulate(id)
                except (SystemExit, Exception) as e:
                    msg = repr(e).replace('\n',
                                          ' ').replace('\t',
                                                       ' ').replace(',', ' ')
                    logger.write(f'0.00\tERROR\t.\texception={msg}\n')
                    self.task_queue.task_done()
                    self.result_queue.put(logger.getvalue())
                    raise e
                self.task_queue.task_done()
                self.result_queue.put(logger.getvalue())


def main(argv=None):
    """Console script for covid19_outbreak_simulator."""
    args = parse_args(argv)
    if args.version:
        from . import __version__
        print(f'COVID10 Outbreak Simulator version {__version__}')
        sys.exit(0)
    if args.summarize_model:
        summarize_model(Params(args), args)
        sys.exit(0)

    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    if args.plugin:
        if args.plugin[0] == '-h':
            # list all plugins
            from covid19_outbreak_simulator.plugin import BasePlugin
            bp = BasePlugin(simulator=None, population=None)
            parser = bp.get_parser()
            parser.parse_args(['-h'])
        # load the plugins just to check if the parameters are ok
        load_plugins(args.plugin)

    if not args.jobs:
        args.jobs = multiprocessing.cpu_count()

    if args.stop_if is not None:
        if args.stop_if[0].startswith('t>'):
            #
            try:
                float(args.stop_if[0][2:])
            except Exception as e:
                raise ValueError(
                    f'Invalid value for option --stop-if "{args.stop_if[0]}": {e}'
                )
        else:
            raise ValueError(
                f'Option --stop-if currently only supports t>TIME to stop after certain time point.'
            )

    completed_ids = 0

    # check the last line
    if os.path.isfile(args.logfile):
        last_line = ''
        try:
            with open(args.logfile, 'rb') as f:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
                last_line = f.readline().decode()
        except:
            pass
        if not last_line:
            completed_ids = 0
        else:
            fields = last_line.split('\t')
            if len(fields) != 5:
                raise ValueError(f'Existing file is corrupeted. Please fix before continue: "{last_line.strip()}" does not have five fields.')
            if fields[2] != 'END':
                raise ValueError(f'Last record of replicate ends with line "{last_line.strip()}" is not an "END" event. Please fix before continue.')
            completed_ids = int(fields[0])

    if args.resume:
        if completed_ids == args.repeats:
            print(f'All simulations have been performed. Remove {args.logfile} if you would like to rerun.')
            return 0
        if completed_ids > args.repeats:
            print(f'More than requested {args.repeats} replicates exists in {args.logfile}. Remove the logfile if you would like to rerun.')
            return 0
        if completed_ids != 0:
            print(f'Resuming from {completed_ids} completed records in {args.logfile}')
    elif completed_ids != 0:
        print(f'Overwriting {completed_ids} completed records in {args.logfile}')
        completed_ids = 0

    if os.path.isfile(args.logfile + '.lock'):
        raise RuntimeError(f'The output logfile {args.logfile} is locked. Please remove {args.logfile}.lock manually if you are certain that no other process is writing to the logfile')

    submitted = 0
    try:
        with open(args.logfile + '.lock', 'w') as lock:
            lock.write(f'START: {datetime.now().strftime("%m/%d/%Y-%H:%M:%S")}\n')
            lock.write(f'CMD: {subprocess.list2cmdline(sys.argv)}')

        workers = [
            Worker(tasks, results, args, cmd=argv if argv else sys.argv[1:])
            for i in range(min(args.jobs, args.repeats))
        ]
        for worker in workers:
            worker.start()

        with open(args.logfile, 'a' if completed_ids > 0 else 'w') as logger:
            if completed_ids == 0:
                logger.write('id\ttime\tevent\ttarget\tparams\n')
            for i in range(args.repeats):
                if i+1 > completed_ids:
                    submitted += 1
                    tasks.put(i + 1)
            for i in range(args.jobs):
                tasks.put(None)
            #
            for i in tqdm(range(completed_ids, args.repeats),
                total=args.repeats, initial=completed_ids):
                result = results.get()
                lines = result.splitlines()
                first_fields = lines[0].split('\t')
                if len(first_fields) != 4 or first_fields[1] != 'START':
                    raise ValueError(f'Wrong starting record reported: {lines[0]}')
                last_fields = lines[-1].split('\t')
                if len(last_fields) != 4 or last_fields[1] not in ('END', 'ERROR'):
                    raise ValueError(f'Wrong last record reported: {lines[-1]} ')
                logger.write(''.join(f'{i+1}\t{line}\n' for line in lines))
                if last_fields[1] == 'ERROR':
                    break
                if i % 1000 == 999:
                    logger.flush()
    finally:
        os.remove(args.logfile + '.lock')

    for worker in workers:
        # wait for workers to complete
        worker.join()

    summarize_simulations(args.logfile, args.summary_report)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
