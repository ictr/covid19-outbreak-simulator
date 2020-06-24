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
        '--susceptibility',
        nargs='+',
        help='''Weight of susceptibility. The default value is 1, meaning everyone is
            equally susceptible. With options such as
            "--susceptibility nurse=1.2 patients=0.8" you can give weights to different
            groups of people so that they have higher or lower probabilities to be
            infected.''')
    parser.add_argument(
        '--symptomatic-r0',
        nargs='+',
        help='''Production number of symptomatic infectors, should be specified as a single
            fixed number, or a range, and/or multipliers for different groups such as
            A=1.2. For example "--symptomatic-r0 1.4 2.8 nurse=1.2" means a general R0
            ranging from 1.4 to 2.8, while nursed has a range from 1.4*1.2 and 2.8*1.2.'''
    )
    parser.add_argument(
        '--asymptomatic-r0',
        nargs='+',
        help='''Production number of asymptomatic infectors, should be specified as a single
            fixed number, or a range and/or multipliers for different groups''')
    parser.add_argument(
        '--incubation-period',
        nargs='+',
        help='''Incubation period period, should be specified as "lognormal" followed by two
            numbers as mean and sigma, or "normal" followed by mean and sd, and/or
            multipliers for different groups. Default to "lognormal 1.621 0.418"'''
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
            such as --infectors nurse1 nurse2.''')
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
            with StringIO() as logger:
                logger.id = id
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
