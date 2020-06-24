from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin


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
            type=float,
            default=1.0,
            help='''Proportion of active cases to quarantine. Default to
            all, but can be set to a lower value to indicate incomplete quarantine.
            This option does not apply to cases when IDs are explicitly specified.''',
        )
        parser.add_argument(
            '--duration', type=float, default=14, help='''Days of quarantine''')
        return parser

    def apply(self, time, population, args=None):
        if args.IDs:
            IDs = args.IDs
        else:
            IDs = [
                x for x, y in population.items()
                if isinstance(y.infected, float) and
                not isinstance(y.recovered, float)
            ]
            if args.proportion != 1.0:
                IDs = IDs[:int(len(IDs) * args.proportion)]

        events = []

        for ID in IDs:
            if ID not in population:
                raise ValueError(f'Invalid ID to quanrantine {ID}')
            events.append(
                Event(
                    time,
                    EventType.QUARANTINE,
                    target=ID,
                    logger=self.logger,
                    till=time + args.duration))
        return events
