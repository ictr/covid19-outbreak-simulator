"""Console script for covid19_outbreak_simulator."""
import argparse
import sys
from tqdm import tqdm

from .model import get_default_params
from .simulator import Simulator


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
        '--proportion-of-asymptomatic-carriers',
        nargs='*',
        type=float,
        help='''Proportion of asymptomatic cases. You can specify a fix number, or two
        numbers as the lower and higher CI (95%) of the proportion. Default to 0.10 to 0.40.'''
    )
    args = parser.parse_args()

    params = get_default_params(interval=args.interval)
    if args.proportion_of_asymptomatic_carriers:
        if len(args.proportion_of_asymptomatic_carriers) == 1:
            params.set('proportion_of_asymptomatic_carriers', 'loc',
                       args.proportion_of_asymptomatic_carriers[0])
            params.set('proportion_of_asymptomatic_carriers', 'scale', 0)
        elif len(args.proportion_of_asymptomatic_carriers) == 2:
            if args.proportion_of_asymptomatic_carriers[
                    0] > args.proportion_of_asymptomatic_carriers[1]:
                raise ValueError(
                    f'Proportions for parameter proportion-of-asymptomatic-carriers should be incremental.'
                )
            params.set('proportion_of_asymptomatic_carriers', 'loc',
                       (args.proportion_of_asymptomatic_carriers[0] +
                        args.proportion_of_asymptomatic_carriers[1]) / 2)
            params.set('proportion_of_asymptomatic_carriers_scale',
                       'quantile_2.5',
                       args.proportion_of_asymptomatic_carriers[0])
        else:
            raise ValueError(
                f'Parameter proportion-of-asymptomatic-carriers accepts one or two numbers.'
            )

    with open(args.logfile, 'w') as logger:
        simu = Simulator(params=params, logger=logger, simu_args=args)
        logger.write('id\ttime\tevent\ttarget\tparams\n')
        for i in tqdm(range(args.repeat)):
            simu.simulate(i + 1)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
