import argparse
import random

from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.simulator import Event, EventType


#
# This plugin take random samples from the population during evolution.
#
class quarantine(BasePlugin):

    # events that will trigger this plugin
    events = set()

    def __init__(self, *args, **kwargs):
        # this will set self.population, self.simualtor, self.logger
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

    def apply(self, time, args=None):
        if not super(quarantine, self).can_apply(time, args):
            return []

        IDs = args.IDs if args.IDs else [
            x for x, y in self.population.items()
            if y.infected not in (None, False)
        ]
        events = []

        for ID in IDs:
            print(f"quarantine {ID}")
            if ID not in self.population:
                raise ValueError(f'Invalid ID to quanrantine {ID}')
            events.append(
                Event(
                    time,
                    EventType.QUARANTINE,
                    self.population[ID],
                    logger=self.logger,
                    till=time + args.duration))
        return events