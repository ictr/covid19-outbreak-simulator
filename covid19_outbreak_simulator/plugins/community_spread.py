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
            nargs='+',
            default=[0.005],
            help='''The probability of anyone to be affected at a given
            interval, which is usually per day (with option --interval 1).
            The value of this parameter can be a single probability, or subpopulation
            specific probabilities specified in the format of 'value name=multiplier`.
            If individuals have different susceptibility specified by option
            --susceptibility, the probability will be multiplied by the
            susceptibility multipliers, The infection events do not have to
            cause actual infection because the individual might be in quarantine,
            or has been infected. The default value of this parameter is 0.005.''')
        return parser

    def apply(self, time, population, args=None):
        events = []

        default_p = 0.0

        for prob in args.probability:
            try:
                if '=' in prob:
                    subpop, p = prob.split('=')
                    if default_p == 0:
                        raise ValueError('Multiplier applied to default value 0.')
                    p = float(p) * default_p
                else:
                    subpop = ''
                    p = float(prob)
                    default_p = p
            except Exception as e:
                raise ValueError(f'Invalid parameter --probability for plugin community_spread: {prob}: {e}')
            # drawning random number one by one
            events += [
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
                if population.in_subpop(id, subpop) and np.random.binomial(1,
                    min(1, p *
                    ind.susceptibility), 1)[0]
            ]

        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=community_spread,n_infected={len(events)}\n'
        )
        return events
