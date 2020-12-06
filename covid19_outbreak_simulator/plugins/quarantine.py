from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier

import random

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
            '--proportion',
            nargs='*',
            help='''Proportion of individuals or active cases (parameter --who) to quarantine. Default to
            all, but can be set to a lower value to indicate incomplete quarantine.
            This option does not apply to cases when IDs are explicitly specified.
            Multipliers are allowed to specify proportions for each subpopulation.''',
        )
        parser.add_argument(
            '--target',
            default='infected',
            choices=["infected", "all"],
            help='''Who to quarantine, which can be "infected" (default) which are people who are
            currently infected and not recovered, and "all" which are all people specified.''',
        )
        parser.add_argument(
            '--duration', type=float, default=14, help='''Days of quarantine''')
        return parser

    def apply(self, time, population, args=None):
        if args.IDs:
            IDs = args.IDs
            if args.proportion:
                raise ValueError('Proportion is now allowed if specific IDs to quarantine is specified.')
            if any(x not in population for x in IDs):
                raise ValueError('Invalid or non-existant ID to quarantine.')
            if args.target == 'infected':
                IDs = [x for x in IDs if isinstance(population[x].infected, float) and
                    not isinstance(population[x].recovered, float)]
        else:
            proportions = parse_param_with_multiplier(args.proportion,
                subpops=population.group_sizes.keys(), default=1.0)

            IDs = []
            for name, sz in population.group_sizes.items():
                prop = proportions.get(name if name in proportions else '', 1.0)

                if args.target == 'all':
                    spIDs = [x.id for x in population.individuals.values() if name == '' or x.group == name]
                else:
                    spIDs = [x.id for x in population.individuals.values() if (name == '' or x.group == name) and
                        isinstance(x.infected, float) and not isinstance(x.recovered, float)]

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
                    EventType.QUARANTINE,
                    target=ID,
                    logger=self.logger,
                    till=time + args.duration))
        quarantined_list = f',Quarantined={",".join(IDs)}' if args.verbosity > 1 else ''
        if args.verbosity > 0:
            self.logger.write(f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=quarantine,n_quarantined={len(IDs)}{quarantined_list}\n')

        return events
