from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier
import numpy

class testing(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(testing, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(testing, self).get_parser()
        parser.prog = '--plugin testing'
        parser.description = '''PCR-based test that can pick out all active cases.'''
        parser.add_argument(
            'IDs', nargs='*', help='''IDs of individuals to test. Parameter "proportion"
            will be ignored with specified IDs for testing''')
        parser.add_argument(
            '--proportion',
            nargs='+',
            help='''Proportion of individuals to test. Individuals who are tested
            positive will by default be quarantined. Multipliers are allowed to specify
            proportion of tests for each group.''',
        )
        parser.add_argument(
            '--sensitivity',
            nargs='+',
            type=float,
            default=[1.0, 0.0],
            help='''Sensitibity of the test. Individuals who carry the virus will have this
            probability to be detected. If a second paramter is set, it is intepreted
            as a Limit of Detection value in terms of transmissibility probability.
            The overall sensibility will be lower with a positive LOD value so it is
            advised to perform a test run to obtain the true sensitivity.''',
        )
        parser.add_argument(
            '--specificity',
            type=float,
            default=1.0,
            help='''Specificity of the test. Individuals who do not carry the virus will have
            this probability to be tested negative.''',
        )
        parser.add_argument(
            '--turnaround-time',
            type=float,
            default=0,
            help='''Time interval from the time of submission of process to the time of the
                completion of the process.''',
        )
        parser.add_argument(
            '--handle-positive',
            default='remove',
            help='''How to handle individuals who are tested positive, which should be
                "keep" (do not do anything), "remove" (remove from population), and "quarantine"
                (put aside until it recovers). Quarantine can be specified as "quarantine_7" etc
                to specify  duration of quarantine. Individuals that are already in quarantine
                will continue to be quarantined. Default to "remove", meaning all symptomatic cases
                will be removed from population.''')
        return parser

    def apply(self, time, population, args=None):
        n_false_positive = 0
        n_false_negative = 0
        n_tested = 0
        n_lod_false_negative = 0

        def select(ind, counts=None):
            nonlocal n_tested
            nonlocal n_false_positive
            nonlocal n_false_negative
            nonlocal n_lod_false_negative
            if counts:
                if counts[ind.group] > 0:
                    counts[ind.group] -= 1
                else:
                    return False
            n_tested += 1
            affected = isinstance(ind.infected, float) and not isinstance(ind.recovered, float)
            if affected:
                if len(args.sensitivity) == 2:
                    if ind.viral_load(time) <= args.sensitivity[1]:
                        n_lod_false_negative += 1
                        return False

                res = args.sensitivity[0] == 1 or float(args.sensitivity[0]) > numpy.random.uniform()
                if not res:
                    n_false_negative += 1
                return res
            else:
                res = args.specificity != 1 and args.specificity <= numpy.random.uniform()
                if res:
                    n_false_positive += 1
                return res

        if args.IDs:
            IDs = [x for x in args.IDs if select(population[x])]
        else:
            proportions = parse_param_with_multiplier(args.proportion,
                subpops=population.group_sizes.keys(), default=1.0)
            counts = {name:int(size*proportions[name]) for name,size in population.group_sizes.items()}

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
                        time + args.turnaround_time, EventType.REMOVAL, target=ID, logger=self.logger))
            elif args.handle_positive.startswith('quarantine'):
                if args.handle_positive == 'quarantine':
                    duration = 14
                else:
                    duration = int(args.handle_positive.split('_', 1)[1])
                if not population[ID].quarantined:
                    events.append(
                        Event(
                            time + args.turnaround_time,
                            EventType.QUARANTINE,
                            target=ID,
                            logger=self.logger,
                            till=time + duration))
            elif args.handle_positive != 'keep':
                raise ValueError(
                    'Unsupported action for patients who test positive.')

        detected_IDs = f',detected={",".join(IDs)}' if IDs else ''
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=testing,n_tesetd={n_tested},n_detected={len(IDs)},n_false_positive={n_false_positive},n_false_negative={n_false_negative},n_lod_false_negative={n_lod_false_negative}{detected_IDs}\n'
        )
        return events
