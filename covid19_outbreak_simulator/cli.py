"""Console script for covid19_outbreak_simulator."""
import argparse
import sys
from tqdm import tqdm
from collections import defaultdict
from .model import get_default_params
from .simulator import Simulator


def summarize_simulations(args):
    # write some summary information into standard output
    n_simulation = 0
    n_infection = 0
    n_infection_failed = 0
    n_infection_avoided = 0
    n_infection_ignored = 0
    n_show_symptom = 0
    n_removal = 0
    n_quarantine = 0
    n_reintegration = 0
    n_abort = 0
    #
    n_asym_infection = 0
    n_presym_infection = 0
    n_sym_infection = 0
    #
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

        for line in lines:
            id, time, event, target, params = line.split('\t')
            if id == 'id':
                # skip header
                continue
            time = float(time)
            target = None if target == '.' else int(target)
            params = params.split(',')
            #
            if event == 'INFECTION':
                n_infection += 1
                if 'by=0' in params:
                    infection_from_seed_per_sim[id] += 1
                    if id not in infection_time_from_seed_per_sim:
                        infection_time_from_seed_per_sim[id] = time
                if time != 0 and id not in first_infection_day_per_sim:
                    first_infection_day_per_sim[id] = time
                for param in params:
                    if param.startswith('r_asym='):
                        n_asym_infection += int(param[7:])
                    elif param.startswith('r_presym='):
                        n_presym_infection += int(param[9:])
                    elif param.startswith('r_sym='):
                        n_sym_infection += int(param[6:])
            elif event == 'INFECTION_FAILED':
                n_infection_failed += 1
            elif event == 'INFECTION_AVOIDED':
                n_infection_avoided += 1
            elif event == 'INFECTION_IGNORED':
                n_infection_ignored += 1
            elif event == 'SHOW_SYMPTOM':
                n_show_symptom += 1
                if target == 0:
                    n_seed_show_symptom_on_day[int(time) + 1] += 1
                if id not in first_symptom_day_per_sim:
                    first_symptom_day_per_sim[id] = time
                elif id not in second_symptom_per_sim:
                    second_symptom_per_sim[
                        id] = time - first_symptom_day_per_sim[id]
                elif id not in third_symptom_per_sim:
                    third_symptom_per_sim[
                        id] = time - second_symptom_per_sim[id]
            elif event == 'REMOVAL':
                n_removal += 1
            elif event == 'QUARANTINE':
                n_quarantine += 1
            elif event == 'REINTEGRATION':
                n_reintegration += 1
            elif event == 'ABORT':
                n_abort += 1
            elif event == 'END':
                n_simulation += 1
                n_remaining_popsize[target] += 1
                n_outbreak_duration[0 if time == 0 else int(time) + 1] += 1
            else:
                raise ValueError(f'Unrecognized event {event}')
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
    n_first_symptom_on_day[0] = n_simulation - sum(
        n_first_symptom_on_day.values())
    #
    for v in second_symptom_per_sim.values():
        n_second_symptom_on_day[int(v) + 1] += 1
    n_second_symptom_on_day[0] = n_simulation - n_first_symptom_on_day[0] - sum(
        n_second_symptom_on_day.values())
    #
    for v in third_symptom_per_sim.values():
        n_third_symptom_on_day[int(v) + 1] += 1
    n_third_symptom_on_day[0] = n_simulation - n_first_symptom_on_day[
        0] - n_second_symptom_on_day[0] - sum(n_third_symptom_on_day.values())
    #
    # print
    print(f'logfile\t{args.logfile}')
    print(f'popsize\t{args.popsize}')
    print(f'keep_symptomatic\t{"yes" if args.keep_symptomatic else "no"}')
    if args.pre_quarantine is None:
        print(f'pre_quarantine\tno')
    else:
        print(f'pre_quarantine\t{args.pre_quarantine} days')
    if args.interval == 1 / 24:
        print(f'interval\t1 hour')
    elif args.interval == 1:
        print(f'interval\t1 day')
    else:
        print(f'interval\t{args.interval:.2f} day')
    if args.prop_asym_carriers:
        if len(args.prop_asym_carriers) == 1:
            print(f'prop_asy_carriers\t{args.prop_asym_carriers[0]*100:.1f}%')
        else:
            print(
                f'prop_asy_carriers\t{args.prop_asym_carriers[0]*100:.1f}% to {args.prop_asym_carriers[1]*100:.1f}%'
            )
    else:
        print(f'prop_asy_carriers\t10% to 40%')

    print(f'n_simulation\t{n_simulation}')
    print(f'n_infection\t{n_infection}')
    print(f'n_infection_failed\t{n_infection_failed}')
    print(f'n_infection_avoided\t{n_infection_avoided}')
    print(f'n_infection_ignored\t{n_infection_ignored}')
    print(f'n_show_symptom\t{n_show_symptom}')
    print(f'n_removal\t{n_removal}')
    print(f'n_quarantine\t{n_quarantine}')
    print(f'n_reintegration\t{n_reintegration}')
    print(f'n_abort\t{n_abort}')
    print(f'n_asym_infection\t{n_asym_infection}')
    print(f'n_presym_infection\t{n_presym_infection}')
    print(f'n_sym_infection\t{n_sym_infection}')

    for num in sorted(n_remaining_popsize.keys()):
        print(f'n_remaining_popsize_{num}\t{n_remaining_popsize[num]}')
    for day in sorted(n_outbreak_duration.keys()):
        if day == 0:
            print(f'n_no_outbreak\t{n_outbreak_duration[day]}')
        else:
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
    for day in sorted(n_first_symptom_on_day.keys()):
        if day == 0:
            print(f'n_no_first_symptom\t{n_first_symptom_on_day[day]}')
        else:
            print(
                f'n_first_symptom_on_day_{day}\t{n_first_symptom_on_day[day]}')
    for day in sorted(n_second_symptom_on_day.keys()):
        if day == 0:
            print(f'n_no_second_symptom\t{n_second_symptom_on_day[day]}')
        else:
            print(
                f'n_second_symptom_on_day_{day}\t{n_second_symptom_on_day[day]}'
            )
    for day in sorted(n_third_symptom_on_day.keys()):
        if day == 0:
            print(f'n_no_third_symptom\t{n_third_symptom_on_day[day]}')
        else:
            print(
                f'n_third_symptom_on_day_{day}\t{n_third_symptom_on_day[day]}')


def main():
    """Console script for covid19_outbreak_simulator."""
    parser = argparse.ArgumentParser('COVID Simulator')
    parser.add_argument(
        '--popsize',
        default=64,
        type=int,
        help='''Size of the population, including the infector that
        will be introduced at the beginning of the simulation''')
    parser.add_argument(
        '--repeat',
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
        type=float,
        help='''Days of self-quarantine before introducing infector to the group.
            The simulation will be aborted if the infector shows symptom before
            introduction.''')
    parser.add_argument(
        '--interval',
        default=1 / 24,
        help='Interval of simulation, default to 1/24, by hour')
    parser.add_argument('--logfile', default='simulation.log', help='logfile')

    parser.add_argument(
        '--prop-asym-carriers',
        nargs='*',
        type=float,
        help='''Proportion of asymptomatic cases. You can specify a fix number, or two
        numbers as the lower and higher CI (95%%) of the proportion. Default to 0.10 to 0.40.'''
    )

    parser.add_argument(
        '--analyze-existing-logfile',
        action='store_true',
        help='''Analyze an existing logfile, useful for updating the summarization
            procedure or uncaptured output.''')
    args = parser.parse_args()

    params = get_default_params(interval=args.interval)
    if args.prop_asym_carriers:
        if len(args.prop_asym_carriers) == 1:
            params.set('prop_asym_carriers', 'loc', args.prop_asym_carriers[0])
            params.set('prop_asym_carriers', 'scale', 0)
        elif len(args.prop_asym_carriers) == 2:
            if args.prop_asym_carriers[0] > args.prop_asym_carriers[1]:
                raise ValueError(
                    f'Proportions for parameter prop-asym-carriers should be incremental.'
                )
            params.set(
                'prop_asym_carriers', 'loc',
                (args.prop_asym_carriers[0] + args.prop_asym_carriers[1]) / 2)
            params.set('prop_asym_carriers', 'quantile_2.5',
                       args.prop_asym_carriers[0])
        else:
            raise ValueError(
                f'Parameter prop-asym-carriers accepts one or two numbers.')

    if not args.analyze_existing_logfile:
        with open(args.logfile, 'w') as logger:
            simu = Simulator(params=params, logger=logger, simu_args=args)
            logger.write('id\ttime\tevent\ttarget\tparams\n')
            for i in tqdm(range(args.repeat)):
                simu.simulate(i + 1)

    summarize_simulations(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
