import random
import numpy as np

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin


class community(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(community, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(community, self).get_parser()
        parser.prog = '--plugin community'
        parser.description = 'Community infection that infect everyone in the population randomly.'
        parser.add_argument(
            '--probability',
            type=float,
            default=0.005,
            help='''The probability of anyone to be affected at a given
            interval, which is usually per day. Default to 0.005.''')
        return parser

    def apply(self, time, population, args=None):

        ids = list(population.ids)
        events = [
            Event(
                time,
                EventType.INFECTION,
                target=ids[idx],
                logger=self.logger,
                priority=True,
                by=None,
                leadtime=0,
                handle_symptomatic=self.simulator.simu_args.handle_symptomatic)
            for idx, aff in enumerate(
                np.random.binomial(1, args.probability, len(population)))
            if aff
        ]

        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=community,n_infected={len(events)}\n'
        )
        return events
