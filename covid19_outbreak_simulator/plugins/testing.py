import os

import numpy as np
import pandas as pd

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.model import Model, Params
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.population import Individual
from covid19_outbreak_simulator.utils import (parse_handle_symptomatic_options,
                                              parse_param_with_multiplier,
                                              select_individuals)


class testing(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
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
            '--target',
            nargs='*',
            choices=[
                "infected", "uninfected", "quarantined", "recovered",
                "vaccinated", "unvaccinated", "all"
            ],
            help='''Type of individuals to be tested, can be "infected", "uninfected",
            "quarantined", "recovered", "vaccinated", "unvaccinated", or "all". If
            count is not specified, all matching individuals will be removed, otherwise
            count number will be moved, following the order of types. Default to "all".'''
        )
        parser.add_argument(
            '--ignore-vaccinated',
            action='store_true',
            help='Ignore vaccinated, replaced by --target unvaccinated',
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
            nargs='*',
            default=['remove'],
            help='''How to handle individuals who are tested positive, which should be
                "keep" (do not do anything), "replace" (remove from population), "recover"
                (instant recover, to model constant workforce size),  "quarantine"
                (put aside until it recovers), and "reintegrate" (remove from quarantine).
                Quarantine can be specified as "quarantine_7" etc to specify  duration of
                quarantine. Individuals that are already in quarantine will continue to be
                quarantined. Default to "remove", meaning all symptomatic cases
                will be removed from population. Multipliers are allows to specify
                different reactions for individuals from different subpopulations.'''
        )
        return parser

    def summarize_model(self, simu_args, args):
        print(f'\nPlugin {self}:')

        model = Model(Params(simu_args))
        for asym_carriers in (0, 1, None):
            if asym_carriers is not None:
                model.params.set('prop_asym_carriers', 'loc', asym_carriers)
                model.params.set('prop_asym_carriers', 'scale', 0)
            else:
                model = Model(Params(simu_args))

            # average test sensitivity
            sensitivities7 = []
            sensitivities20 = []
            with open(os.devnull, 'w') as logger:
                logger.id = 1

                for i in range(10000):
                    model.draw_prop_asym_carriers()
                    ind = Individual(
                        id='0', susceptibility=1, model=model, logger=logger)
                    ind.infect(0, by=None, leadtime=0)

                    for i in range(20):
                        test_lod = args.sensitivity[1] if len(
                            args.sensitivity) == 2 else 0

                        lod_sensitivity = ind.test_sensitivity(i, test_lod)
                        if lod_sensitivity == 0:
                            continue
                        #
                        sensitivity = lod_sensitivity * args.sensitivity[0]
                        if i <= 7:
                            sensitivities7.append(sensitivity)
                        else:
                            sensitivities20.append(sensitivity)
            print(
                f"\nTest sensitivity (for {model.params.prop_asym_carriers*100:.1f}% asymptomatic carriers)"
            )
            print(
                f"    <= 7 days:     {pd.Series(sensitivities7).mean() * 100:.1f}%"
            )
            print(
                f"    > 7 days:      {pd.Series(sensitivities20).mean() * 100:.1f}%"
            )
            print(
                f"    all:           {pd.Series(sensitivities7 + sensitivities20).mean() * 100:.1f}%"
            )

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

        if args.ignore_vaccinated:
            args.target = ['unvaccinated']

        if not args.target:
            args.target = ['all']

        def select(ind):
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

            affected = isinstance(ind.infected, float)

            n_tested += 1
            if affected:
                test_lod = args.sensitivity[1] if len(
                    args.sensitivity) == 2 else 0
                lod_sensitivity = ind.test_sensitivity(time, test_lod)
                #
                sensitivity = lod_sensitivity * args.sensitivity[0]
                res = sensitivity == 1 or sensitivity > np.random.uniform()

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

                res = args.specificity != 1 and args.specificity <= np.random.uniform(
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

            IDs = []
            for name, sz in population.group_sizes.items():
                prop = proportions.get(name if name in proportions else '', 1.0)
                count = int(sz * prop) if prop < 1 else sz
                if count == 0:
                    continue

                spIDs = [
                    x.id
                    for x in population.individuals.values()
                    if name in ('', x.group)
                ]
                IDs.extend([
                    x for x in select_individuals(population, spIDs,
                                                  args.target, count)
                    if select(population[x])
                ])

        events = []

        for ID in IDs:
            if ID not in population:
                raise ValueError(f'Invalid ID to quanrantine {ID}')

            handle_positive = parse_handle_symptomatic_options(
                args.handle_positive, population[ID].group)
            proportion = handle_positive.get('proportion', 1)
            if handle_positive['reaction'] == 'remove':
                if proportion == 1 or np.random.uniform(0, 1,
                                                        1)[0] <= proportion:
                    events.append(
                        Event(
                            time + args.turnaround_time,
                            EventType.REMOVAL,
                            target=population[ID],
                            logger=self.logger))
            elif handle_positive['reaction'] == 'quarantine':
                duration = handle_positive.get('duration', 14)
                if proportion == 1 or np.random.uniform(0, 1,
                                                        1)[0] <= proportion:
                    events.append(
                        Event(
                            time + args.turnaround_time,
                            EventType.QUARANTINE,
                            target=population[ID],
                            logger=self.logger,
                            till=time + duration,
                            reason='detected'))
            elif handle_positive['reaction'] == 'replace':
                if proportion == 1 or np.random.uniform(0, 1,
                                                        1)[0] <= proportion:
                    events.append(
                        Event(
                            time + args.turnaround_time,
                            EventType.REPLACEMENT,
                            reason='detected',
                            keep=['vaccinated', 'immunity', 'infectivity'],
                            target=population[ID],
                            logger=self.logger))
            elif handle_positive['reaction'] == 'reintegrate':
                if proportion == 1 or np.random.uniform(0, 1,
                                                        1)[0] <= proportion:
                    events.append(
                        Event(
                            time + args.turnaround_time,
                            EventType.REINTEGRATION,
                            target=population[ID],
                            logger=self.logger))
            elif handle_positive['reaction'] != 'keep':
                raise ValueError(
                    f'Unsupported action for patients who test positive: {handle_positive}'
                )

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
