from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin


class pcrtest(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(pcrtest, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(pcrtest, self).get_parser()
        parser.prog = '--plugin pcrtest'
        parser.description = '''PCR-based test that can pick out all active cases.'''
        parser.add_argument(
            'IDs', nargs='*', help='IDs of individuals to test.')
        parser.add_argument(
            '--proportion',
            type=float,
            default=1.0,
            help='''Proportion of individuals to test. Individuals who are tested
            positive will by default be quarantined.''',
        )
        parser.add_argument(
            '--handle-positive',
            default='remove',
            help='''How to handle individuals who are tested positive, which should be
                "remove" (remove from population), and "quarantine" (put aside until
                it recovers). Quarantine can be specified as "quarantine_7" etc to specify
                duration of quarantine. Default to "remove", meaning all symptomatic cases
                will be removed from population.''')
        return parser

    def apply(self, time, population, args=None):
        if args.IDs:
            IDs = [
                x for x in args.IDs
                if isinstance(population[x].infected, float) and
                not isinstance(population[x].recovered, float)
            ]
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
            if args.handle_positive == 'remove':
                events.append(
                    Event(
                        time, EventType.REMOVAL, target=ID, logger=self.logger))
            elif args.handle_positive.startswith('quarantine'):
                if args.handle_positive == 'quarantine':
                    duration = 14
                else:
                    duration = int(args.handle_positive.split('_', 1)[1])
                events.append(
                    Event(
                        time,
                        EventType.QUARANTINE,
                        target=ID,
                        logger=self.logger,
                        till=time + duration))
            else:
                raise ValueError(
                    'Unsupported action for patients who test positive.')
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=pcrtest,n_detected={len(IDs)}\n'
        )
        return events
