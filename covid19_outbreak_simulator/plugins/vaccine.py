import random
import numpy as np

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier


class vaccine(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(community_infection, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(community_infection, self).get_parser()
        parser.prog = '--plugin vaccine'
        parser.description = '''Vaccine all or selected individual, which will reduce
            the chance that he or she gets infected (susceptibility), the duration of
            the infection, and the probability that he or she infect others (R).'''
        parser.add_argument(
            '--proportion',
            nargs='+',
            default=[0],
            help='''The proportion of individuals to be vaccinated, which can be
            to the entire population or varying from subpopulation to subpopulation.
            ''')
        parser.add_argument(
            '--immunity',
            nargs='+',
            default=[0],
            help='''The probability to resist an infection event, essentially 1 - susceptibility.
        ''')            
        parser.add_argument(
            '--protection',
            nargs='+',
            default=[0],
            help='''The reduction of R0 to the individuals who were vaccinated.
            ''')
        parser.add_argument(
            '--infectivity',
            nargs='+',
            default=[0],
            help='''The reduction of infectivity, namely probability to infect others.
            ''')
        
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

        if args.verbosity > 0:
            self.logger.write(
                f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=community_infection,n_infected={len(events)}{ID_list}\n'
            )
        return events
