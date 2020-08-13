import random
import numpy as np

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin


class community_spread(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(community_spread, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(community_spread, self).get_parser()
        parser.prog = '--plugin community_spread'
        parser.description = 'Community infection that infect everyone in the population randomly.'
        parser.add_argument(
            '--probability',
            type=float,
            default=0.005,
            help='''The probability of anyone to be affected at a given
            interval, which is usually per day (with option --interval 1).
            If individuals have different susceptibility specified by option
            --susceptibility, the probability will be multiplied by the
            susceptibility multipliers, The infection events do not have to
            cause actual infection because the individual might be in quarantine,
            or has been infected. The default value of this parameter is 0.005.''')
        return parser

    def apply(self, time, population, args=None):

        if population.uneven_susceptibility:
            # drawning random number one by one
            events = [
                Event(
                    time,
                    EventType.INFECTION,
                    target=id,
                    logger=self.logger,
                    priority=True,
                    by=None,
                    leadtime=0,
                    handle_symptomatic=self.simulator.simu_args
                    .handle_symptomatic)
                for id, ind in population.individuals.items()
                if np.random.binomial(1, min(1, args.probability *
                                      ind.susceptibility), 1)[0]
            ]
        else:
            # drawing random numbers all at once
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
                    handle_symptomatic=self.simulator.simu_args
                    .handle_symptomatic)
                for idx, aff in enumerate(
                    np.random.binomial(1, args.probability, len(population)))
                if aff
            ]
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=community_spread,n_infected={len(events)}\n'
        )
        return events
