"""Console script for covid19_outbreak_simulator."""
import argparse
import sys
import multiprocessing
import numpy as np
from io import StringIO
from tqdm import tqdm
from collections import defaultdict
from .simulator import Simulator
from .model import Params


def summarize_simulations(args):
    # write some summary information into standard output
    n_simulation = 0
    total_infection = 0
    total_infection_failed = 0
    total_infection_avoided = 0
    total_infection_ignored = 0
    total_show_symptom = 0
    total_removal = 0
    total_quarantine = 0
    total_reintegration = 0
    total_abort = 0
    #
    total_asym_infection = 0
    total_presym_infection = 0
    total_sym_infection = 0
    #
    n_no_outbreak = 0
    n_remaining_popsize = defaultdict(int)
    n_outbreak_duration = defaultdict(int)
    #
    n_num_infected_by_seed = defaultdict(int)
    n_first_infected_by_seed_on_day = defaultdict(int)
    n_seed_show_symptom_on_day = defaultdict(int)
    n_first_symptom_on_day = defaultdict(int)
    n_first_infection_on_day = defaultdict(int)
    #
    n_second_symptom_on_day = defaultdict(int)
    n_third_symptom_on_day = defaultdict(int)
    #
    with open(args.logfile) as lines:
        infection_from_seed_per_sim = defaultdict(int)
        infection_time_from_seed_per_sim = defaultdict(int)
        first_infection_day_per_sim = defaultdict(int)
        first_symptom_day_per_sim = defaultdict(int)
        second_symptom_per_sim = defaultdict(int)
        third_symptom_per_sim = defaultdict(int)

        if args.infectors:
            infectors = args.infectors
        else:
            infectors = ['0']

        total_popsize = sum(int(x.split('=')[-1]) for x in args.popsize)
        for line in lines:
            id, time, event, target, params = line.split('\t')
            if id == 'id':
                # skip header
                continue
            time = float(time)
            target = None if target == '.' else target
            params = params.split(',')
            #
            if event == 'INFECTION':
                total_infection += 1
                if any(x in params for x in [f'by={x}' for x in infectors]):
                    infection_from_seed_per_sim[id] += 1
                    if id not in infection_time_from_seed_per_sim:
                        infection_time_from_seed_per_sim[id] = time
                if time != 0 and id not in first_infection_day_per_sim:
                    first_infection_day_per_sim[id] = time
                for param in params:
                    if param.startswith('r_asym='):
                        total_asym_infection += int(param[7:])
                    elif param.startswith('r_presym='):
                        total_presym_infection += int(param[9:])
                    elif param.startswith('r_sym='):
                        total_sym_infection += int(param[6:])
            elif event == 'INFECTION_FAILED':
                total_infection_failed += 1
            elif event == 'INFECTION_AVOIDED':
                total_infection_avoided += 1
            elif event == 'INFECTION_IGNORED':
                total_infection_ignored += 1
            elif event == 'SHOW_SYMPTOM':
                total_show_symptom += 1
                if target in infectors:
                    n_seed_show_symptom_on_day[int(time) + 1] += 1
                if args.pre_quarantine and time < float(args.pre_quarantine[0]):
                    pass
                elif id not in first_symptom_day_per_sim:
                    first_symptom_day_per_sim[id] = time
                elif id not in second_symptom_per_sim:
                    second_symptom_per_sim[
                        id] = time - first_symptom_day_per_sim[id]
                elif id not in third_symptom_per_sim:
                    third_symptom_per_sim[
                        id] = time - second_symptom_per_sim[id]
            elif event == 'REMOVAL':
                total_removal += 1
            elif event == 'QUARANTINE':
                total_quarantine += 1
            elif event == 'REINTEGRATION':
                total_reintegration += 1
            elif event == 'ABORT':
                total_abort += 1
            elif event == 'END':
                n_simulation += 1
                n_remaining_popsize[target] += 1
                if not args.pre_quarantine:
                    n_outbreak_duration[0 if time == 0 else int(time) + 1] += 1
                else:
                    n_outbreak_duration[
                        0 if time <= float(args.pre_quarantine[0]) else
                        int(time - float(args.pre_quarantine[0])) + 1] += 1
                if target == total_popsize and id not in first_symptom_day_per_sim:
                    n_no_outbreak += 1
            else:
                raise ValueError(f'Unrecognized event {event}')
    # summarize
    for v in infection_from_seed_per_sim.values():
        n_num_infected_by_seed[v] += 1
    #
    for v in infection_time_from_seed_per_sim.values():
        if args.pre_quarantine:
            n_first_infected_by_seed_on_day[int(v -
                                                float(args.pre_quarantine[0])) +
                                            1] += 1
        else:
            n_first_infected_by_seed_on_day[int(v) + 1] += 1
    n_first_infected_by_seed_on_day[0] = n_simulation - sum(
        n_first_infected_by_seed_on_day.values())
    #
    for v in first_infection_day_per_sim.values():
        if args.pre_quarantine:
            n_first_infection_on_day[int(v - float(args.pre_quarantine[0])) +
                                     1] += 1
        else:
            n_first_infection_on_day[int(v) + 1] += 1
    n_first_infection_on_day[0] = n_simulation - sum(
        n_first_infection_on_day.values())
    #
    n_seed_show_symptom_on_day[0] = n_simulation - sum(
        n_seed_show_symptom_on_day.values())
    #
    for v in first_symptom_day_per_sim.values():
        if args.pre_quarantine:
            n_first_symptom_on_day[int(v - float(args.pre_quarantine[0])) +
                                   1] += 1
        else:
            n_first_symptom_on_day[int(v) + 1] += 1
    n_first_symptom = sum(n_first_symptom_on_day.values())
    #
    for v in second_symptom_per_sim.values():
        n_second_symptom_on_day[int(v) + 1] += 1
    n_second_symptom = sum(n_second_symptom_on_day.values())
    #
    for v in third_symptom_per_sim.values():
        n_third_symptom_on_day[int(v) + 1] += 1
    n_third_symptom = sum(n_third_symptom_on_day.values())
    #
    # print
    print(f'logfile\t{args.logfile}')
    print(f'popsize\t{" ".join(args.popsize)}')
    print(f'keep_symptomatic\t{"yes" if args.keep_symptomatic else "no"}')
    if args.symptomatic_r0:
        print(f'symptomatic_r0\t{" - ".join(args.symptomatic_r0)}')
    if args.asymptomatic_r0:
        print(f'asymptomatic_r0\t{" - ".join(args.asymptomatic_r0)}')
    if args.incubation_period:
        print(
            f'incubation_period\t{args.incubation_period[0]}({args.incubation_period[1]}, {args.incubation_period[2]}) '
            + ' '.join(args.incubation_period[3:]))
    if args.pre_quarantine is None:
        print(f'pre_quarantine\tno')
    else:
        print(f'pre_quarantine\t{" ".join(args.pre_quarantine)}')
    if args.interval == 1 / 24:
        print(f'interval\t1 hour')
    elif args.interval == 1:
        print(f'interval\t1 day')
    else:
        print(f'interval\t{args.interval:.2f} day')
    if args.prop_asym_carriers:
        if len(args.prop_asym_carriers) == 1:
            print(f'prop_asym_carriers\t{args.prop_asym_carriers[0]*100:.1f}%')
        else:
            print(
                f'prop_asym_carriers\t{args.prop_asym_carriers[0]*100:.1f}% to {args.prop_asym_carriers[1]*100:.1f}%'
            )
    else:
        print(f'prop_asym_carriers\t10% to 40%')
    print(f'allow_lead_time\t{"yes" if args.allow_lead_time else "no"}')
    print(f'n_simulation\t{n_simulation}')
    print(f'total_infection\t{total_infection}')
    print(f'total_infection_failed\t{total_infection_failed}')
    print(f'total_infection_avoided\t{total_infection_avoided}')
    print(f'total_infection_ignored\t{total_infection_ignored}')
    print(f'total_show_symptom\t{total_show_symptom}')
    print(f'total_removal\t{total_removal}')
    print(f'total_quarantine\t{total_quarantine}')
    print(f'total_reintegration\t{total_reintegration}')
    print(f'total_abort\t{total_abort}')
    print(f'total_asym_infection\t{total_asym_infection}')
    print(f'total_presym_infection\t{total_presym_infection}')
    print(f'total_sym_infection\t{total_sym_infection}')

    for num in sorted(n_remaining_popsize.keys()):
        print(f'n_remaining_popsize_{num}\t{n_remaining_popsize[num]}')
    # no outbreak is defined as final population size
    print(f'n_no_outbreak\t{n_no_outbreak}')
    for day in sorted(n_outbreak_duration.keys()):
        print(f'n_outbreak_duration_{day}\t{n_outbreak_duration[day]}')
    for num in sorted(n_num_infected_by_seed.keys()):
        print(f'n_num_infected_by_seed_{num}\t{n_num_infected_by_seed[num]}')
    for day in sorted(n_first_infected_by_seed_on_day.keys()):
        if day == 0:
            print(
                f'n_no_infected_by_seed\t{n_first_infected_by_seed_on_day[day]}'
            )
        else:
            print(
                f'n_first_infected_by_seed_on_day_{day}\t{n_first_infected_by_seed_on_day[day]}'
            )
    for day in sorted(n_seed_show_symptom_on_day.keys()):
        if day == 0:
            print(f'n_seed_show_no_symptom\t{n_seed_show_symptom_on_day[day]}')
        else:
            print(
                f'{day}_n_seed_show_symptom_on_day\t{n_seed_show_symptom_on_day[day]}'
            )
    for day in sorted(n_first_infection_on_day.keys()):
        if day == 0:
            print(f'n_no_first_infection\t{n_first_infection_on_day[day]}')
        else:
            print(
                f'n_first_infection_on_day_{day}\t{n_first_infection_on_day[day]}'
            )
    print(f'n_first_symptom\t{n_first_symptom}')
    for day in sorted(n_first_symptom_on_day.keys()):
        print(f'n_first_symptom_on_day_{day}\t{n_first_symptom_on_day[day]}')
    print(f'n_second_symptom\t{n_second_symptom}')
    for day in sorted(n_second_symptom_on_day.keys()):
        print(f'n_second_symptom_on_day_{day}\t{n_second_symptom_on_day[day]}')
    print(f'n_third_symptom\t{n_third_symptom}')
    for day in sorted(n_third_symptom_on_day.keys()):
        print(f'n_third_symptom_on_day_{day}\t{n_third_symptom_on_day[day]}')


class Worker(multiprocessing.Process):

    def __init__(self, task_queue, result_queue, args):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.params = Params(args)
        self.simu_args = args

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
                    params=self.params, logger=logger, simu_args=self.simu_args)
                simu.simulate(id)
                self.task_queue.task_done()
                self.result_queue.put(logger.getvalue())


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
        default=10000,
        type=int,
        help='''Number of replicates to simulate. An ID starting from
              1 will be assinged to each replicate and as the first columns
              in the log file.''')
    parser.add_argument(
        '--keep-symptomatic',
        action='store_true',
        help='Keep affected individuals in the population')
    parser.add_argument(
        '--pre-quarantine',
        nargs='*',
        help='''Days of self-quarantine before introducing infector to the group.
            The simulation will be aborted if the infector shows symptom before
            introduction. If you quarantine multiple people or specified named
            groups, you will need to append the IDs to the parameter (e.g.
            --pre-quarantine day nurse1 nurse2''')
    parser.add_argument(
        '--infectors',
        nargs='*',
        help='''Infectees to introduce to the population, default to '0'. If you
            would like to introduce multiple infectees to the population, or if
            you have named groups, you will have to specify the IDs of carrier
            such as --infectors nurse1 nurse2''')
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
        '--allow-lead-time',
        action='store_true',
        help='''The seed carrier will be asumptomatic but always be at the beginning
            of incurbation time. If allow lead time is set to True, the carrier will
            be anywhere in his or her incubation period.''')
    parser.add_argument(
        '--analyze-existing-logfile',
        action='store_true',
        help='''Analyze an existing logfile, useful for updating the summarization
            procedure or uncaptured output. ''')
    parser.add_argument(
        '-j',
        '--jobs',
        type=int,
        help='Number of process to use for simulation. Default to number of CPU cores.'
    )
    return parser.parse_args(args)


def main(args=None):
    """Console script for covid19_outbreak_simulator."""
    args = parse_args(args)
    if not args.analyze_existing_logfile:
        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        if not args.jobs:
            args.jobs = multiprocessing.cpu_count()

        workers = [Worker(tasks, results, args) for i in range(args.jobs)]
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

    summarize_simulations(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
