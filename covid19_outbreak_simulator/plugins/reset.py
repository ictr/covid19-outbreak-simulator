from covid19_outbreak_simulator.event import EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import select_individuals


class reset(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'after_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = '--plugin reset'
        parser.description = 'reset individuals from subpopulations.'
        parser.add_argument(
            'subpops',
            nargs='*',
            help='Subpopulation that we will be reset')
        return parser

    def apply(self, time, population, args=None):
        for sp in args.subpops:
            if sp not in population.group_sizes:
                raise ValueError(f'Unrecorgnized subpopulation {sp}')

        sps = set(args.subpops)
        n_resetted = 0
        for ind in population.individuals():
            if ind.group in sps:
                ind.immunity = None
                ind.infectivity = None
                ind.infected = False
                ind.show_symptom = False
                ind.recovered = False
                ind.symptomatic = None
                ind.vaccinated = False
                ind.quarantined = False
                ind.r0 = None
                ind.incubation_period = None
                n_resetted += 1

        self.logger.write(
            f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=reset,subpops={args.subpops},n_resetted={n_resetted}\n'
        )

        return []
