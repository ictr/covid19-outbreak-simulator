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

    args = parser.parse_args()

    params = get_default_params(interval=args.interval)

    with open(args.logfile, 'w') as logger:
        simu = Simulator(params=params, logger=logger, args=args)
        logger.write('id\ttime\tevent\ttarget\tparams\n')
        for i in tqdm(range(args.repeat)):
            simu.simulate(i + 1)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
