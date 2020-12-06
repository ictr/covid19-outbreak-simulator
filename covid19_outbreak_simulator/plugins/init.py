import random
import numpy as np
from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier


class init(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(init, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(init, self).get_parser()
        parser.prog = '--plugin init'
        parser.description = '''Initialize population with initial prevalence and seroprevalence.
            IDs of infected individuals will be output with -v 2.'''
        parser.add_argument(
            '--incidence-rate',
            nargs='*',
            help='''Incidence rate of the population (default to zero), which should be
            the probability that any individual is currently affected with the virus (not
            necessarily show any symptom). Multipliers are allowed to specify incidence rate
            for each group.''')
        parser.add_argument(
            '--seroprevalence',
            nargs='*',
            help='''Seroprevalence of the population (default to zero). This aprameter
            specify the probability (or proportion if --as-proportion is set) of idividuals
            who have had the virus but have recovered, and will not be infected again (according
            to current simulation model, which might change later).''')
        parser.add_argument(
            '--as-proportion',
            action='store_true',
            help='''Seroprevalence and incidence rates are considered as probabilities.
            However, if you are simulating a large population and would like to ensure the
            same proportion of infected individuals across replicate simulations, you can
            set "--as-proportion" to intepret incidence rae and seroprevalence as proportions.
            Note that noone will be carrying the virus if the population size * proportion is
            less than 1.'''
        )
        parser.add_argument(
            '--leadtime',
            help='''With "leadtime" infections are assumed to happen before the simulation.
            This option can be a fixed positive number `t` when the infection happens
            `t` days before current time. If can also be set to 'any' for which the
            carrier can be any time during its course of infection, or `asymptomatic`
            for which the leadtime is adjust so that the carrier does not show any
            symptom at the time point (in incubation period for symptomatic case).
            All events triggered before current time are ignored.''')
        return parser

    def apply(self, time, population, args=None):
        idx = 0

        # population prevalence and incidence rate
        ir = parse_param_with_multiplier(args.incidence_rate,
                subpops=population.group_sizes.keys(), default=0.0)
        #
        isp = parse_param_with_multiplier(args.seroprevalence,
                subpops=population.group_sizes.keys(), default=0.0)

        infected = []
        if args.as_proportion:
            events = []
            n_ir = 0
            n_isp = 0
            for name, sz in population.group_sizes.items():
                pop_ir = ir.get(name if name in ir else '', 0.0)
                sp_ir = int(sz * pop_ir)

                pop_isp = isp.get(name if name in isp else '', 0.0)
                sp_isp = int(sz * pop_isp)
                sp_isp = min(sp_isp, sz - sp_ir)

                pop_status = [1] * sp_ir + [2] * sp_isp + [0] * (
                    sz - sp_ir - sp_isp)
                random.shuffle(pop_status)

                n_ir += sp_ir
                n_isp += sp_isp
                for idx, sts in zip(range(0, sz), pop_status):
                    if sts == 2:
                        population[f'{name}_{idx}' if name else str(idx)].infected = -10.0
                        population[f'{name}_{idx}' if name else str(idx)].recovered = -2.0
                    if sts == 1:
                        ID = f'{name}_{idx}' if name else str(idx)
                        infected.append(ID)
                        events.append(
                            Event(
                                0.0,
                                EventType.INFECTION,
                                target=ID,
                                logger=self.logger,
                                priority=True,
                                by=None,
                                leadtime=args.leadtime,
                                handle_symptomatic=self.simulator.simu_args
                                .handle_symptomatic))
        else:
            # initialize as probability
            events = []
            n_ir = 0
            n_isp = 0
            for name, sz in population.group_sizes.items():
                pop_ir = ir.get(name if name in ir else '', 0.0)
                pop_isp = isp.get(name if name in isp else '', 0.0)
                pop_isp = min(pop_isp, 1 - pop_ir)

                pop_rng = np.random.uniform(0, 1, sz)
                for idx, rng in zip(range(0, sz), pop_rng):
                    if rng < pop_ir:
                        n_ir += 1
                        ID = f'{name}_{idx}' if name else str(idx)
                        infected.append(ID)
                        events.append(
                            Event(
                                0.0,
                                EventType.INFECTION,
                                target=ID,
                                logger=self.logger,
                                priority=True,
                                by=None,
                                leadtime=args.leadtime,
                                handle_symptomatic=self.simulator.simu_args
                                .handle_symptomatic))
                    elif rng < pop_ir + pop_isp:
                        n_isp += 1
                        population[f'{name}_{idx}' if name else str(idx)].infected = -10.0
                        population[f'{name}_{idx}' if name else str(idx)].recovered = -2.0
        infected_list = f',infected={",".join(infected)}' if infected and args.verbosity > 1 else ""
        if args.verbosity > 0:
            self.logger.write(
                f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=init,n_recovered={n_isp},n_infected={n_ir}{infected_list}\n'
            )

        return events
