import random
import numpy as np

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier


class vaccinate(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(vaccinate, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(vaccinate, self).get_parser()
        parser.prog = '--plugin vaccinate'
        parser.description = '''Vaccine all or selected individual, which will reduce
            the chance that he or she gets infected (susceptibility), the duration of
            the infection, and the probability that he or she infect others (R).'''
        parser.add_argument(
            'IDs',
            nargs='*',
            help='''IDs of individuals to test. Parameter "proportion"
            will be ignored with specified IDs for testing''')
        parser.add_argument(
            '--proportion',
            nargs='+',
            help='''The proportion of individuals to be vaccinated, which can be
            to the entire population or varying from subpopulation to subpopulation.
            ''')
        parser.add_argument(
            '--immunity',
            type=float,
            default=0.95,
            help='''The probability to resist an infection event, essentially 1 - susceptibility.
            The default susceptibility is 1, meaning all infection event will cause an infection,
            if immunity == 0.85, susceptibility will be set to 0.15 so that only 15% of infection
            events will succeed.''')
        parser.add_argument(
            '--infectivity',
            type=float,
            default=0.05,
            help='''The reduction of infectivity, which will be simulated as a reduction
            of R0.
            ''')

        return parser

    def apply(self, time, population, args=None):

        if args.IDs:
            IDs = args.IDs
            if args.proportion:
                raise ValueError(
                    'Proportion is now allowed if specific IDs to quarantine is specified.'
                )
            if any(x not in population for x in IDs):
                raise ValueError('Invalid or non-existant ID to quarantine.')
        else:
            proportions = parse_param_with_multiplier(
                args.proportion,
                subpops=population.group_sizes.keys(),
                default=1.0)
            IDs = []
            for name, sz in population.group_sizes.items():
                prop = proportions.get(name if name in proportions else '', 1.0)

                if prop < 0 or prop > 1:
                    raise ValueError(f'Disallowed proportion {prop}')

                spIDs = [
                    x.id
                    for x in population.individuals.values()
                    if (name == '' or x.group == name) and x.vaccinated is False
                ]

                if prop < 1:
                    random.shuffle(spIDs)
                    IDs.extend(spIDs[:int(sz * prop)])
                else:
                    IDs.extend(spIDs)

        events = []
        for ID in IDs:
            events.append(
                Event(
                    time,
                    EventType.VACCINATION,
                    target=ID,
                    priority=True,
                    immunity=args.immunity,
                    infectivity=args.infectivity,
                    logger=self.logger))

        vaccinated_list = f',vaccinated={",".join(IDs)}' if args.verbosity > 1 else ''
        if args.verbosity > 0:
            self.logger.write(
                f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=vaccine,proportion={args.proportion},immunity={args.immunity},infectivity={args.infectivity},n_vaccinated={len(IDs)}{vaccinated_list}\n'
            )

        return events
