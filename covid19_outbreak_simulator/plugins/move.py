from covid19_outbreak_simulator.event import EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import select_individuals


class move(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'after_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = '--plugin move'
        parser.description = 'move individuals from one subpopulation to another.'
        parser.add_argument(
            'IDs',
            nargs='*',
            help='''IDs of individuals to be moved. All other paramters will
                be ignored if IDs are specified''')
        parser.add_argument(
            '--target',
            nargs='*',
            choices=[
                "infected", "uninfected", "quarantined", "recovered",
                "vaccinated", "unvaccinated", "all"
            ],
            help='''One or more types of individuals to be removed, can be "infected", "uninfected",
            "quarantined", "recovered", "vaccinated", "unvaccinated", or "all". If
            count is not specified, all matching individuals will be removed, otherwise
            count number will be moved, following the order of types. Default to "all".'''
        )
        parser.add_argument(
            '--count',
            type=int,
            help='''Number of people to move, which will be randomly
            selected following specified --target.''')
        parser.add_argument(
            '--from',
            required=True,
            dest='from_subpop',
            help='Name of the subpopulation of the source.')
        parser.add_argument(
            '--to',
            required=True,
            dest='to_subpop',
            help='Name of the subpopulation of the destination.')
        parser.add_argument(
            '--reintegrate',
            action='store_true',
            help='''If specified, remove the quarantine status of moved
                individuals
            ''')
        return parser

    def move(self, time, population, args, IDs):
        n_infected = 0
        ID_map = {}
        for ID in IDs:
            new_id = population.move(ID, args.to_subpop)
            if args.reintegrate and isinstance(population[new_id].quarantined,
                                               float):
                population[new_id].reintegrate()
            if isinstance(population[new_id].infected,
                          float) and not isinstance(
                              population[new_id].recovered, float):
                n_infected += 1
                ID_map[ID] = new_id + '*'
            else:
                ID_map[ID] = new_id
        if args.verbosity > 1 and ID_map:
            ID_map = ',ID_map=' + ','.join(
                [f'{x}->{y}' for x, y in ID_map.items()])
        else:
            ID_map = ''
        self.logger.write(
            f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=move,from={args.from_subpop},to={args.to_subpop},n_moved={len(IDs)},n_infected={n_infected}{ID_map}\n'
        )
        return []

    def apply(self, time, population, args=None):
        if args.IDs:
            return self.move(time, population, args, args.IDs)

        assert args.count is not None

        #
        # from
        from_IDs = [
            x.id
            for x in population.individuals.values()
            if x.group == args.from_subpop
        ]
        #
        move_IDs = select_individuals(population, from_IDs, args.target,
                                      args.count)

        if len(move_IDs) < args.count:
            self.logger.write(
                f'{time:.2f}\t{EventType.WARNING.name}\t.\tmsg="Not enough people to move. Expected {args.count}, actual {len(move_IDs)}"\n'
            )

        return self.move(time, population, args, move_IDs)
