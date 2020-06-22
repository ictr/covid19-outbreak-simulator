"""Console script for covid19_outbreak_simulator."""
import argparse
import sys
import shlex
import subprocess
import multiprocessing
import numpy as np
from io import StringIO
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime
from importlib import import_module

from .simulator import Simulator
from .model import Params


def summarize_simulations(logfile):
    # write some summary information into standard output
    n_simulation = 0
    total_infection = 0
    total_infection_failed = 0
    total_infection_avoided = 0
    total_infection_ignored = 0
    total_show_symptom = 0
    total_removal = 0
    total_recover = 0
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
    timed_stats = defaultdict(dict)
    customized_stats = defaultdict(dict)
    #
    with open(logfile) as lines:
        infection_from_seed_per_sim = defaultdict(int)
        infection_time_from_seed_per_sim = defaultdict(int)
        first_infection_day_per_sim = defaultdict(int)
        first_symptom_day_per_sim = defaultdict(int)
        second_symptom_per_sim = defaultdict(int)
        third_symptom_per_sim = defaultdict(int)

        total_popsize = 0
        infectors = []
        args = None

        for line in lines:
            if line.startswith('#'):
                if line.startswith('# CMD:'):
                    args = parse_args(shlex.split(line[6:])[1:])
                    if args.infectors:
                        infectors = args.infectors
                    total_popsize = sum(
                        int(x.split('=')[-1]) for x in args.popsize)
                continue
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
                n_outbreak_duration[0 if time == 0 else int(time) + 1] += 1
                if target == total_popsize and id not in first_symptom_day_per_sim:
                    n_no_outbreak += 1
            elif event == 'RECOVER':
                total_recover += 1
            elif event == 'STAT':
                id, time, event, target, params = line.split('\t')
                params = params.split(',')
                for param in params:
                    try:
                        key, value = param.split('=')
                        if time in timed_stats[key]:
                            timed_stats[key][time] += ', ' + value.strip()
                        else:
                            timed_stats[key][time] = value.strip()
                    except Exception:
                        pass
            elif event == 'ERROR':
                # an error has happened
                # params = line.split('\t')[-1]
                # err = eval(params.split('=', 1)[-1])
                sys.exit(f'Simulator exists with error')

            else:
                # customized events
                id, time, event, target, params = line.split('\t')
                params = params.split(',')
                for param in params:
                    try:
                        key, value = param.split('=')
                        if time in customized_stats[f'{event.lower()}_{key}']:
                            customized_stats[f'{event.lower()}_{key}'][
                                time] += ', ' + value.strip()
                        else:
                            customized_stats[f'{event.lower()}_{key}'][
                                time] = value.strip()
                    except Exception:
                        pass

    # summarize
    for v in infection_from_seed_per_sim.values():
        n_num_infected_by_seed[v] += 1
    #
    for v in infection_time_from_seed_per_sim.values():
        n_first_infected_by_seed_on_day[int(v) + 1] += 1
    n_first_infected_by_seed_on_day[0] = n_simulation - sum(
        n_first_infected_by_seed_on_day.values())
    #
    for v in first_infection_day_per_sim.values():
        n_first_infection_on_day[int(v) + 1] += 1
    n_first_infection_on_day[0] = n_simulation - sum(
        n_first_infection_on_day.values())
    #
    n_seed_show_symptom_on_day[0] = n_simulation - sum(
        n_seed_show_symptom_on_day.values())
    #
    for v in first_symptom_day_per_sim.values():
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
    print(f'handle_symptomatic\t{" ".join(args.handle_symptomatic)}')
    if args.symptomatic_r0:
        print(f'symptomatic_r0\t{" - ".join(args.symptomatic_r0)}')
    if args.asymptomatic_r0:
        print(f'asymptomatic_r0\t{" - ".join(args.asymptomatic_r0)}')
    if args.incubation_period:
        print(
            f'incubation_period\t{args.incubation_period[0]}({args.incubation_period[1]}, {args.incubation_period[2]}) '
            + ' '.join(args.incubation_period[3:]))
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
    print(f'total_recover\t{total_recover}')
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
    for item, timed_value in timed_stats.items():
        for time, value in timed_value.items():
            values = [x.strip() for x in value.split(',')]
            if len(set(values)) == 1:
                value = f'[{values[0]}] * {len(values)}'
                print(f'{item}_{time}\t{value}')
            else:
                print(f'{item}_{time}\t{value.strip()}')
        for time, value in timed_value.items():
            try:
                value = eval(value)
                if len(value) > 1:
                    value = '{:.3f}'.format(sum(value) / len(value))
                    print(f'avg_{item}_{time}\t{value}')
            except:
                pass
    for item, timed_value in customized_stats.items():
        for time, value in timed_value.items():
            values = [x.strip() for x in value.split(',')]
            if len(set(values)) == 1:
                value = f'[{values[0]}] * {len(values)}'
                print(f'{item}_{time}\t{value}')
            else:
                print(f'{item}_{time}\t{value.strip()}')
        for time, value in timed_value.items():
            try:
                value = eval(value)
                if len(value) > 1:
                    value = '{:.3f}'.format(sum(value) / len(value))
                    print(f'avg_{item}_{time}\t{value}')
            except:
                pass


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
        '--handle-symptomatic',
        nargs='*',
        default=['remove'],
        help='''How to handle individuals who show symptom, which should be "keep" (stay in
            population), "remove" (remove from population), and "quarantine" (put aside until
            it recovers). all options can be followed by a "proportion", and quarantine can
            be specified as "quarantine_7" etc to specify duration of quarantine.'''
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
        '--allow-lead-time',
        action='store_true',
        help='''The seed carrier will be asumptomatic but always be at the beginning
            of incurbation time. If allow lead time is set to True, the carrier will
            be anywhere in his or her incubation period.''')
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
        elif args.plugin[0].startswith('-'):
            # it has to be -h
            raise ValueError(
                f'Plugin name should not start with a dash (-): "{args.plugin[0]}" provided.'
            )
        else:
            plugin = args.plugin[0]
            if '.' not in plugin:
                module_name, plugin_name = plugin, plugin.replace('-', '_')
            else:
                module_name, plugin_name = plugin.rsplit('.', 1)
            try:
                mod = import_module(
                    f'covid19_outbreak_simulator.plugins.{module_name}')
            except Exception as e:
                try:
                    mod = import_module(module_name)
                except Exception as e:
                    raise ValueError(
                        f'Failed to import module {module_name}: {e}')
            try:
                obj = getattr(mod, plugin_name)(simulator=None, population=None)
            except Exception as e:
                raise ValueError(
                    f'Failed to retrieve plugin {plugin_name} from module {module_name}: {e}'
                )
            # if there is a parser
            parser = obj.get_parser()
            if '-h' in args.plugin:
                parser.parse_args(['-h'])

    if not args.jobs:
        args.jobs = multiprocessing.cpu_count()

    if args.stop_if is not None:
        if args.stop_if[0].startswith('t>'):
            #
            try:
                st = float(args.stop_if[0][2:])
            except Exception:
                raise ValueError(
                    f'Invalid value for option --stop-if "{args.stop_if[0]}": {e}'
                )
        else:
            raise ValueError(
                f'Option --stop-if currently only supports t>TIME to stop after certain time point.'
            )

    workers = [
        Worker(tasks, results, args)
        for i in range(min(args.jobs, args.repeats))
    ]
    for worker in workers:
        worker.start()

    with open(args.logfile, 'w') as logger:
        logger.write(
            f'# CMD: outbreak_simulator {subprocess.list2cmdline(argv if argv else sys.argv[1:])}\n'
        )
        logger.write(
            f'# START: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}\n')
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
        logger.write(
            f'# START: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}\n')

    summarize_simulations(args.logfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
