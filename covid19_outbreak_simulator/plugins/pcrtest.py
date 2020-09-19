from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier

class pcrtest(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(pcrtest, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(pcrtest, self).get_parser()
        parser.prog = '--plugin pcrtest'
        parser.description = '''PCR-based test that can pick out all active cases.'''
        parser.add_argument(
            'IDs', nargs='*', help='''IDs of individuals to test. Parameter "proportion"
            will be ignored with specified IDs for testing''')
        parser.add_argument(
            '--proportion',
            nargs='+',
            default=1.0,
            help='''Proportion of individuals to test. Individuals who are tested
            positive will by default be quarantined. Multipliers are allowed to specify
            proportion of tests for each subpopulation.''',
        )
        parser.add_argument(
            '--sensitivity',
            type=float,
            default=1.0,
            help='''Sensitibity of the test. Individuals who carry the virus will have this
            probability to be detected.''',
        )
        parser.add_argument(
            '--specificity',
            type=float,
            default=1.0,
            help='''Specificity of the test. Individuals who do not carry the virus will have
            this probability to be tested negative.''',
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
        def select(ind, counts=None):
            if counts:
                if counts[ind.group] > 0:
                    counts[ind.group] -= 1
                else:
                    return False
            affected = isinstance(ind.infected, float) and not isinstance(ind.recovered, float)
            if affected:
                return args.sensitivity == 1 or args.sensitivity > numpy.random.uniform()
            else:
                return args.specificity != 1 and args.specificity <= numpy.random.uniform()

        if args.IDs:
            #
            IDs = [x for x in args.IDs if select(population[x])]
        else:
            proportions = parse_param_with_multiplier(args.proportion,
                subpops=population.subpop_sizes.keys())
            counts = {name:int(size*proportions[name]) for name,size in population.subpop_sizes.items()}

            IDs = [
                x for x, y in population.items()
                if select(y, counts)
            ]

        #print(f'SELECT {" ".join(IDs)}')
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
            f'{self.logger.id}\t{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=pcrtest,n_detected={len(IDs)},detected={",".join(IDs)}\n'
        )
        return events
