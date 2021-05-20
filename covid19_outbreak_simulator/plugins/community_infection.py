import random
import numpy as np

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier


class community_infection(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(community_infection, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(community_infection, self).get_parser()
        parser.prog = '--plugin community_infection'
        parser.description = '''Community infection that infect everyone in the population randomly.
            IDs of list of infected will be output with -v 2.'''
        parser.add_argument(
            '--probability',
            nargs='+',
            default=[0.005],
            help='''The probability of anyone to be affected at a given
            interval, which is usually per day (with option --interval 1).
            Multipliers are allowed to specify probability for each group.
            If individuals have different susceptibility specified by option
            --susceptibility, the probability will be multiplied by the
            susceptibility multipliers, The infection events do not have to
            cause actual infection because the individual might be in quarantine,
            or has been infected. The default value of this parameter is 0.005.
            Note that individuals currently in quarantine will not be affected
            by community infection.''')
        return parser

    def apply(self, time, population, args=None):
        events = []

        probability = parse_param_with_multiplier(args.probability,
            subpops=population.group_sizes.keys())

        for subpop, prob in probability.items():
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
                if population[id].group == subpop and not population[id].quarantined and np.random.binomial(1,
                    min(1, prob * ind.susceptibility), 1)[0]
            ]
        IDs = [x.target for x in events]
        ID_list = f',infected={",".join(IDs)}' if IDs and args.verbosity > 1 else ''

        if args.verbosity > 0 and IDs:
            self.logger.write(
                f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=community_infection,n_infected={len(events)}{ID_list}\n'
            )
        return events
