import random

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin


class move(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'after_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(move, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(move, self).get_parser()
        parser.prog = '--plugin move'
        parser.description = 'move individuals from one subpopulation to another.'
        parser.add_argument(
            'IDs',
            nargs='*',
            help='''IDs of individuals to be moved. All other paramters will
                be ignored if IDs are specified''')
        parser.add_argument(
            '--type',
            dest='src_types',
            nargs='*',
            help='''Type of individuals to be removed, can be "infected",
            "quarantined", "recovered", "vaccinated", "unvaccinated", or "all". If
            count is not specified, all matching individuals will be removed, otherwise
            count number will be moved, following the order of types. Default to "all".'''
        )
        parser.add_argument(
            '--count', type=int, help='''Number of people to move''')
        parser.add_argument(
            '--from',
            dest='from_subpop',
            help='Name of the subpopulation of the source.')
        parser.add_argument(
            '--to',
            dest='to_subpop',
            help='Name of the subpopulation of the destination.')
        return parser

    def move(self, time, population, args, IDs):
        ID_map = {}
        for ID in IDs:
            new_id = population.move(ID, args.to_subpop)
            ID_map[ID] = new_id
        if args.verbosity > 0:
            ID_map = ',ID_map=' + ','.join(
                [f'{x}->{y}' for x, y in ID_map.items()])
        else:
            ID_map = ''
        self.logger.write(
            f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=move,from={args.from_subpop},to={args.to_subpop}{ID_map}\n'
        )
        return []

    def apply(self, time, population, args=None):
        if args.IDs:
            return self.move(time, population, args, args.IDs)

        #
        # from
        from_IDs = [
            x.id
            for x in population.individuals.values()
            if x.group == args.from_subpop
        ]
        #
        random.shuffle(from_IDs)
        #
        # now find the individuals to move
        if not args.src_types:
            args.src_types = ['all']

        def add_ind(match_cond, max_count):
            res = []
            count = 0
            for ID in from_IDs:
                if match_cond(population[ID]):
                    res.append(ID)
                    from_IDs.remove(ID)
                    count += 1
                    if count == max_count:
                        break
            return res

        count = 0
        move_IDs = []
        for src_type in args.src_types:
            if src_type == 'infected':
                move_IDs.extend(
                    add_ind(
                        lambda ind: isinstance(ind, float) and not isinstance(
                            ind.recovered, float), args.count - len(move_IDs)))
            #
            elif src_type == 'recovered':
                move_IDs.extend(
                    add_ind(lambda ind: isinstance(ind.recovered, float),
                            args.count - len(move_IDs)))
            #
            elif src_type == 'quarantined':
                move_IDs.extend(
                    add_ind(lambda ind: isinstance(ind.quarantined, float),
                            args.count - len(move_IDs)))
            #
            elif src_type == 'vaccinated':
                move_IDs.extend(
                    add_ind(lambda ind: isinstance(ind.vaccinated, float),
                            args.count - len(move_IDs)))
            #
            elif src_type == 'unvaccinated':
                move_IDs.extend(
                    add_ind(lambda ind: not isinstance(ind.vaccinated, float),
                            args.count - len(move_IDs)))
            #
            elif src_type == 'all':
                move_IDs.extend(
                    add_ind(lambda ind: True, args.count - len(move_IDs)))

            if len(move_IDs) == args.count:
                break

        if len(move_IDs) < args.count:
            self.logger.write(
                f'{time:.2f}\t{EventType.WARNING.name}\t{self.id}\tmsg="Not enough people to move. Expected {args.count}, actual {len(move_IDs)}"\n'
            )

        return self.move(time, population, args, move_IDs)