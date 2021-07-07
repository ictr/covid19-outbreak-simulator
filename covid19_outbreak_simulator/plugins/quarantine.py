from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import (parse_param_with_multiplier,
                                              select_individuals)


class quarantine(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = '--plugin quarantine'
        parser.description = '''Quarantine specified or all infected individuals
            for specified durations.'''
        parser.add_argument(
            'IDs', nargs='*', help='IDs of individuals to quarantine.')
        parser.add_argument(
            '--proportion',
            nargs='*',
            help='''Proportion of individuals to quarantine. Default to
            all (1.0), but can be set to a lower value to indicate incomplete quarantine.
            This option does not apply to cases when IDs are explicitly specified.
            Multipliers are allowed to specify proportions for each subpopulation.''',
        )
        parser.add_argument(
            '--count',
            nargs='*',
            help='''Number of individuals to quarantine. Default to 1 but multipliers
            are expected to set number of individuals from each subpopulation.''',
        )
        parser.add_argument(
            '--target',
            default=['infected'],
            nargs='*',
            choices=[
                "infected", "uninfected", "quarantined", "recovered",
                "vaccinated", "unvaccinated", "all"
            ],
            help='''One or more types of individuals to be quarantined, can be "infected",
                "uninfected", "quarantined", "recovered", "vaccinated", "unvaccinated", or
                "all". Individuals will be selected based on conditions until --count or
                --proportion is satisfied''',
        )
        parser.add_argument(
            '--duration', type=float, default=14, help='''Days of quarantine''')
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
            if args.target:
                IDs = select_individuals(population, IDs, args.target)

        else:
            if args.count:
                counts = parse_param_with_multiplier(
                    args.count,
                    subpops=population.group_sizes.keys(),
                    default=1)
            else:
                proportions = parse_param_with_multiplier(
                    args.proportion,
                    subpops=population.group_sizes.keys(),
                    default=1.0)
                counts = {}
                for name, sz in population.group_sizes.items():
                    prop = proportions.get(name if name in proportions else '',
                                           1.0)
                    counts[name] = int(sz * prop) if prop < 1 else sz

            IDs = []
            for name, sz in population.group_sizes.items():
                count = int(counts.get(name if name in counts else '1'))
                if count == 0:
                    continue

                spIDs = [
                    x.id
                    for x in population.individuals.values()
                    if name in ('', x.group)
                ]
                IDs = select_individuals(population, spIDs, args.target, count)

        events = []
        for ID in IDs:
            events.append(
                Event(
                    time,
                    EventType.QUARANTINE,
                    target=population[ID],
                    logger=self.logger,
                    till=time + args.duration,
                    reason='mandatory'))

        quarantined_list = f',Quarantined={",".join(IDs)}' if args.verbosity > 1 else ''
        if args.verbosity > 0:
            self.logger.write(
                f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=quarantine,n_quarantined={len(IDs)}{quarantined_list}\n'
            )

        return events
