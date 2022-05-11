import random

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier, parse_target_param


class community_infection(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = '--plugin community_infection'
        parser.description = '''Community infection that infect everyone in the population randomly.
            IDs of list of infected will be output with -v 2.'''
        parser.add_argument(
            '--probability',
            nargs='+',
            action='append',
            default=[],
            help='''The probability of anyone to be affected at a given
            interval, which is usually per day (with option --interval 1).
            Multipliers are allowed to specify probability for each group.
            If individuals have different susceptibility specified by option
            --susceptibility, the probability will be multiplied by the
            susceptibility multipliers, The infection events do not have to
            cause actual infection because the individual might be in quarantine,
            or has been infected. The default value of this parameter is 0.005.
            Note that individuals currently in quarantine will not be affected
            by community infection. If multiple time points are specified with
            option --at, multiple --probability parameters can be specified to specify
            probability at each time points.''')
        parser.add_argument(
            "--target",
            nargs="*",
            help="""Type of individuals to be tested, can be "infected", "uninfected",
            "quarantined", "recovered", "vaccinated", "unvaccinated", or "all", or
            '!' of its negation, and any combination of '&' and '|' of these. If
            count is not specified, all matching individuals will be tested, otherwise
            count number will be tested, following the order of types. Default to "all".""",
        )
        return parser

    def apply(self, time, population, args=None):
        events = []

        assert isinstance(args.probability, list)
        assert isinstance(args.probability[0], list)

        if len(args.probability) == 1:
            probability = parse_param_with_multiplier(
                args.probability[0], subpops=population.group_sizes.keys())
        else:
            if not args.at:
                raise ValueError('Parameter --at is expected when multiple probability values are specified.')
            if time not in args.at:
                raise ValueError(f'{time} is not in the list of --at {args.at}')
            idx = args.at.index(time)
            if len(args.probability) < idx + 1:
                raise ValueError(f'No value of --probability corresponding to time {time}')
            probability = parse_param_with_multiplier(
                args.probability[idx], subpops=population.group_sizes.keys())

        is_targeted = parse_target_param(args.target)

        for subpop, prob in probability.items():
            if prob == 0.0:
                continue
            # drawning random number one by one
            sp_events = [Event(
                    time,
                    EventType.INFECTION,
                    target=ind,
                    logger=self.logger,
                    priority=True,
                    by=None,
                    leadtime=0,
                    handle_symptomatic=self.simulator.simu_args
                    .handle_symptomatic,
                    handle_symptomatic_vaccinated=self.simulator.simu_args
                    .handle_symptomatic_vaccinated,
                    handle_symptomatic_unvaccinated=self.simulator.simu_args
                    .handle_symptomatic_unvaccinated,
                    handle_infection=self.simulator.simu_args.handle_infection)
                for id, ind in population.items(group=subpop)
                if is_targeted(ind) and not isinstance(ind.quarantined, float) and random.random() < prob *
                ind.susceptibility
            ]
            sus = [id for id, ind in population.items(group=subpop)
                if not ind.quarantined]

            IDs = [x.target.id for x in sp_events]
            ID_list = f',infected={",".join(IDs)}' if IDs and args.verbosity > 1 else ''

            if args.verbosity > 0:
                self.logger.write(
                        f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=community_infection,subpop={subpop if subpop else "all"},n_qualified={len(sus)},n_infected={len(IDs)}{ID_list if args.verbosity > 1.else ""}\n'
                    )

            events += sp_events
        return events
