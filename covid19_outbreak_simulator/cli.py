"""Console script for covid19_outbreak_simulator."""
import argparse
import multiprocessing
import sys
from io import StringIO

import numpy as np
from tqdm import tqdm

from .model import Params
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
            fixed number, or a range. Multipliers are allowed to specify symptomatic r0 for
            each group. This parameter reflects the infectivity of virus carrier measured
            by the average number of individuals one infected individual "would" infect if
            infectivity is not blocked by for example quarantine and susceptibility of
            infectees.'''
    )
    parser.add_argument(
        '--asymptomatic-r0',
        nargs='+',
        help='''Production number of asymptomatic infectors, should be specified as a single
            fixed number or a range. Multipliers are allowed to specify asymptomatic r0 for
            each group.''')
    parser.add_argument(
        '--symptomatic-transmissibility-model',
        nargs='+',
        help='''Model used for asymptomatic cases with parameters. The default model
            normal has a duration of 8 days after incubation, and a peak happens at 2/3 of
            incubation. The piece wise model has a proportion for the start of infection
            (relative to incubation period), a proportion for the peak of infectivity (
            relative to incubation period), and a range of days after the
            onset of symptoms. The models should be specified as "normal" (no parameter is
            allowed), or model name with parameters such as "piecewise 0.1 0.3 7 9".
        '''
    )
    parser.add_argument(
        '--asymptomatic-transmissibility-model',
        nargs='+',
        help='''Model used for asymptomatic cases with parameters. The default model
            normal has a duration of 12 and peaks at 4.8 day. The piecewise model has
            a proportion for the start of infection,  a proportion for the peak of
            infectivity, and a range of days after the infection (no incubation period
            when compared to the symptomatic case). The models should be specified as "normal"
            (no parameter is allowed), or model name with parameters such as
            "piecewise 0.1 0.3 5 7".
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
        '--handle-symptomatic',
        nargs='*',
        help='''How to handle individuals who show symptom, which should be "keep" (stay in
            population), "remove" (remove from population), and "quarantine" (put aside until
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
    return parser.parse_args(args)

class FilteredStringIO(StringIO):
    def __init__(self, id, track_events=None):
        super(FilteredStringIO, self).__init__()
        self.id = id
        self._track_events = track_events
        if self._track_events is not None:
            self._track_events = set(self._track_events)
            for evt in ('START', 'ERRPR'):
                if evt not in self._track_events:
                    self._track_events.add(evt)


    def write(self, text):
        if not self._track_events or text.split('\t')[2] in self._track_events:
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
            with FilteredStringIO(id, track_events = self.simu_args.track_events) as logger:
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
                    logger.write(f'{id}\t0.00\tERROR\t.\texception={msg}\n')
                    self.task_queue.task_done()
                    self.result_queue.put(logger.getvalue())
                    raise e
                self.task_queue.task_done()
                self.result_queue.put(logger.getvalue())


def main(argv=None):
    """Console script for covid19_outbreak_simulator."""
    args = parse_args(argv)
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

    workers = [
        Worker(tasks, results, args, cmd=argv if argv else sys.argv[1:])
        for i in range(min(args.jobs, args.repeats))
    ]
    for worker in workers:
        worker.start()

    with open(args.logfile, 'w') as logger:
        logger.write('id\ttime\tevent\ttarget\tparams\n')
        for i in range(args.repeats):
            tasks.put(i + 1)
        for i in range(args.jobs):
            tasks.put(None)
        #
        for i in tqdm(range(args.repeats)):
            result = results.get()
            logger.write(result)
            if 'ERROR' in result:
                break

    summarize_simulations(args.logfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
