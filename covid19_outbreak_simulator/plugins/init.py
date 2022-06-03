import random

import numpy as np

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier, parse_target_param
from covid19_outbreak_simulator.population import Population


class init(BasePlugin):

    # events that will trigger this plugin
    apply_at = "before_core_events"

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = "--plugin init"
        parser.description = """Initialize population with initial prevalence and seroprevalence.
            IDs of infected individuals will be output with -v 2."""
        parser.add_argument(
            "--incidence-rate",
            nargs="*",
            help="""Incidence rate of the population (default to zero), which should be
            the probability that any individual is currently affected with the virus (not
            necessarily show any symptom). Multipliers are allowed to specify incidence rate
            for each group.""",
        )
        parser.add_argument(
            "--target",
            nargs="*",
            help="""Type of individuals to be tested, can be "infected", "uninfected",
            "quarantined", "recovered", "vaccinated", "unvaccinated", or "all", or
            '!' of its negation, and any combination of '&' and '|' of these. If
            count is not specified, all matching individuals will be tested, otherwise
            count number will be tested, following the order of types. Default to "all".""",
        )
        parser.add_argument(
            "--seroprevalence",
            nargs="*",
            help="""Seroprevalence of the population (default to zero). This parameter
            specify the probability (or proportion if --as-proportion is set) of idividuals
            who have had the virus but have recovered.""",
        )
        parser.add_argument(
            "--as-proportion",
            action="store_true",
            help="""Seroprevalence and incidence rates are considered as probabilities.
            However, if you are simulating a large population and would like to ensure the
            same proportion of infected individuals across replicate simulations, you can
            set "--as-proportion" to intepret incidence rae and seroprevalence as proportions.
            Note that noone will be carrying the virus if the population size * proportion is
            less than 1.""",
        )
        parser.add_argument(
            "--leadtime",
            help="""With "leadtime" infections are assumed to happen before the simulation.
            This option can be a fixed positive number `t` when the infection happens
            `t` days before current time. If can also be set to 'any' for which the
            carrier can be any time during its course of infection, or `asymptomatic`
            for which the leadtime is adjust so that the carrier does not show any
            symptom at the time point (in incubation period for symptomatic case).
            All events triggered before current time are ignored.""",
        )
        return parser

    def apply(self, time, population, args=None):

        if args.target is not None:
            is_targeted = parse_target_param(args.target)
            inds = {id:ind for id,ind in population.individuals.items() if is_targeted(ind)}
            pop = Population([], population.model, [], None)
            pop.individuals = inds
            pop.group_sizes = {x:0 for x in population.group_sizes.keys()}
            for ind in inds.values():
                pop.group_sizes[ind.group] += 1
        else:
            pop = population

        # get IDs of population
        spIDs = {x:[] for x in pop.group_sizes}
        for id, ind in pop.individuals.items():
            spIDs[ind.group].append(id)

        # population prevalence and incidence rate
        ir = parse_param_with_multiplier(
            args.incidence_rate, subpops=pop.group_sizes.keys()
        )
        #
        isp = parse_param_with_multiplier(
            args.seroprevalence, subpops=pop.group_sizes.keys()
        )

        infected = []
        if args.as_proportion:
            events = []
            n_ir = 0
            n_isp = 0
            for name, sz in pop.group_sizes.items():
                pop_ir = ir.get(name if name in ir else "", 0.0)
                sp_ir = int(sz * pop_ir)

                pop_isp = isp.get(name if name in isp else "", 0.0)
                sp_isp = int(sz * pop_isp)
                sp_isp = min(sp_isp, sz - sp_ir)

                pop_status = [1] * sp_ir + [2] * sp_isp + [0] * (sz - sp_ir - sp_isp)
                random.shuffle(pop_status)

                n_ir += sp_ir
                n_isp += sp_isp
                for ind_id, sts in zip(spIDs[name], pop_status):
                    if sts == 2:
                        pop[ind_id].infected = time - 10.0
                        pop[ind_id].recovered = time - 2.0
                        pop[ind_id].immunity = pop.model.params.immunity_of_recovered
                        pop[ind_id].infectivity = pop.model.params.infectivity_of_recovered
                    if sts == 1:
                        infected.append(ind_id)
                        events.append(
                            Event(
                                time,
                                EventType.INFECTION,
                                target=pop[ind_id],
                                logger=self.logger,
                                priority=True,
                                by=None,
                                leadtime=args.leadtime,
                                handle_symptomatic=self.simulator.simu_args.handle_symptomatic,
                                handle_infection=self.simulator.simu_args.handle_infection,
                            )
                        )
        else:
            # initialize as probability
            events = []
            n_ir = 0
            n_isp = 0
            for name, sz in pop.group_sizes.items():
                pop_ir = ir.get(name if name in ir else "", 0.0)
                pop_isp = isp.get(name if name in isp else "", 0.0)
                pop_isp = min(pop_isp, 1 - pop_ir)

                pop_rng = np.random.uniform(0, 1, sz)
                for ind_id, rng in zip(spIDs[name], pop_rng):
                    if rng < pop_ir:
                        n_ir += 1
                        infected.append(ind_id)
                        events.append(
                            Event(
                                time,
                                EventType.INFECTION,
                                target=pop[ind_id],
                                logger=self.logger,
                                priority=True,
                                by=None,
                                leadtime=args.leadtime,
                                handle_symptomatic=self.simulator.simu_args.handle_symptomatic,
                                handle_infection=self.simulator.simu_args.handle_infection,
                            )
                        )
                    elif rng < pop_ir + pop_isp:
                        n_isp += 1
                        pop[ind_id].infected = time - 10.0
                        pop[ind_id].recovered = time - 2.0
                        pop[ind_id].immunity = pop.model.params.immunity_of_recovered
                        pop[ind_id].infectivity = pop.model.params.infectivity_of_recovered
        infected_list = (
            f',infected={",".join(infected)}' if infected and args.verbosity > 1 else ""
        )
        if args.verbosity > 0:
            self.logger.write(
                f"{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=init,n_initialized={sum(pop.group_sizes.values())},n_recovered={n_isp},n_infected={n_ir}{infected_list}\n"
            )

        return events
