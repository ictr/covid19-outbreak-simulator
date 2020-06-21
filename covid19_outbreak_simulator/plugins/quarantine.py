import argparse
import random

from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.simulator import Event, EventType


class quarantine(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(quarantine, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(quarantine, self).get_parser()
        parser.prog = '--plugin quarantine'
        parser.description = '''Quarantine specified or all infected individuals
            for specified durations.'''
        parser.add_argument(
            'IDs', nargs='*', help='IDs of individuals to quarantine.')
        parser.add_argument(
            '--duration', type=float, help='''Days of quarantine''')
        return parser

    def apply(self, time, population, args=None, simu_args=None):
        print(f'RAISE {args}')

        IDs = args.IDs if args.IDs else [
            x for x, y in population.items() if isinstance(y.infected, float)
        ]
        events = []

        for ID in IDs:
            if ID not in population:
                raise ValueError(f'Invalid ID to quanrantine {ID}')
            events.append(
                Event(
                    time,
                    EventType.QUARANTINE,
                    population[ID],
                    logger=self.logger,
                    till=time + args.duration))
        return events