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
            'IDs',
            nargs='*',
            help='''IDs of individuals to test. Parameter "proportion"
            will be ignored with specified IDs for testing''')
        parser.add_argument(
            '--proportion',
            nargs='+',
            help='''Proportion of individuals to test. Individuals who are tested
            positive will by default be quarantined. Multipliers are allowed to specify
            proportion of tests for each group.''',
        )
        parser.add_argument(
            '--ignore-vaccinated',
            action='store_true',
            help='''Do not test people who are vaccinated.''',
        )
        parser.add_argument(
            '--sensitivity',
            nargs='+',
            type=float,
            default=[1.0],
            help='''Sensitibity of the test. Individuals who carry the virus will have this
            probability to be detected. If a second paramter is set, it is intepreted
            as a Limit of Detection value in terms of log10 CP/ML (e.g. 3 for 1000 cp/ML).
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
                "keep" (do not do anything), "replace" (remove from population), "recover"
                (instant recover, to model constant workforce size), and "quarantine"
                (put aside until it recovers). Quarantine can be specified as "quarantine_7" etc
                to specify  duration of quarantine. Individuals that are already in quarantine
                will continue to be quarantined. Default to "remove", meaning all symptomatic cases
                will be removed from population.''')
        return parser

    def apply(self, time, population, args=None):
        n_infected = 0
        n_uninfected = 0
        n_ignore_infected = 0
        n_ignore_uninfected = 0
        n_recovered = 0
        n_false_positive = 0
        n_false_negative = 0
        n_false_negative_in_recovered = 0
        n_tested = 0
        n_false_negative_lod = 0

        def select(ind, counts=None):
            nonlocal n_tested
            nonlocal n_infected
            nonlocal n_uninfected
            nonlocal n_ignore_infected
            nonlocal n_ignore_uninfected
            nonlocal n_recovered
            nonlocal n_false_positive
            nonlocal n_false_negative
            nonlocal n_false_negative_in_recovered
            nonlocal n_false_negative_lod

            if counts:
                if counts[ind.group] > 0:
                    counts[ind.group] -= 1
                else:
                    return False

            affected = isinstance(ind.infected, float)
            if ind.vaccinated is not False and args.ignore_vaccinated:
                if affected:
                    n_ignore_infected += 1
                else:
                    n_ignore_uninfected += 1
                return False

            n_tested += 1
            if affected:
                test_lod = args.sensitivity[1] if len(
                    args.sensitivity) == 2 else 0
                lod_sensitivity = ind.test_sensitivity(time, test_lod)
                #
                sensitivity = lod_sensitivity * args.sensitivity[0]
                res = sensitivity == 1 or sensitivity > numpy.random.uniform()

                if isinstance(ind.recovered, float):
                    n_recovered += 1
                    if not res:
                        n_false_negative_in_recovered += 1
                else:
                    n_infected += 1
                    if not res:
                        n_false_negative += 1
                        if lod_sensitivity < 1:
                            n_false_negative_lod += 1
                return res
            else:
                n_uninfected += 1

                res = args.specificity != 1 and args.specificity <= numpy.random.uniform(
                )
                if res:
                    n_false_positive += 1
                return res

        if args.IDs:
            IDs = [x for x in args.IDs if select(population[x])]
        else:
            proportions = parse_param_with_multiplier(
                args.proportion,
                subpops=population.group_sizes.keys(),
                default=1.0)
            counts = {
                name: int(size * proportions[name])
                for name, size in population.group_sizes.items()
            }

            IDs = [x for x, y in population.items() if select(y, counts)]

        #print(f'SELECT {" ".join(IDs)}')
        events = []

        for ID in IDs:
            if ID not in population:
                raise ValueError(f'Invalid ID to quanrantine {ID}')
            if args.handle_positive == 'remove':
                events.append(
                    Event(
                        time + args.turnaround_time,
                        EventType.REMOVAL,
                        target=ID,
                        logger=self.logger))
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
            elif args.handle_positive == 'replace':
                events.append(
                    Event(
                        time + args.turnaround_time,
                        EventType.REPLACEMENT,
                        reason='detected',
                        keep=['vaccinated'],
                        target=ID,
                        logger=self.logger))
            elif args.handle_positive != 'keep':
                raise ValueError(
                    'Unsupported action for patients who test positive.')

        res = dict(
            n_tested=n_tested,
            n_infected=n_infected,
            n_uninfected=n_uninfected,
            n_ignore_infected=n_ignore_infected,
            n_ignore_uninfected=n_ignore_uninfected,
            n_recovered=n_recovered,
            n_detected=len(IDs),
            n_false_positive=n_false_positive,
            n_false_negative=n_false_negative,
            n_false_negative_lod=n_false_negative_lod,
            n_false_negative_in_recovered=n_false_negative_in_recovered)
        if IDs and args.verbosity > 1:
            res['detected_IDs'] = ",".join(IDs)
        res_str = ','.join(f'{k}={v}' for k, v in res.items())
        if args.verbosity > 0:
            self.logger.write(
                f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=testing,{res_str}\n'
            )
        return events
