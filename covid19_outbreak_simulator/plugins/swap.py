from covid19_outbreak_simulator.event import EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import select_individuals


class swap(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'after_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super().__init__(*args, **kwargs)

    def get_parser(self):
        parser = super().get_parser()
        parser.prog = '--plugin swap'
        parser.description = 'swap individuals from two subpopulations.'
        parser.add_argument(
            'subpops',
            nargs=2,
            help='Two subpopulation that we will swap subpopulation')
        return parser

    def apply(self, time, population, args=None):
        sp1 = args.subpops[0]
        sp2 = args.subpops[1]
        sz1 = population.group_sizes[sp1]
        sz2 = population.group_sizes[sp2]

        ID1s = set()
        ID2s = set()

        for ind in population.individuals.values():
            grp = ind.group
            if grp == sp1:
                ID1s.add(ind.id)
            elif grp == sp2:
                ID2s.add(ind.id)

        assert len(ID1s) == sz1, f'assert {sp1} has IDs {len(ID1s)} != {sz1}, at {time}'
        assert len(ID2s) == sz2, f'assert {sp2} has IDs {len(ID2s)} != {sz2}, at {time}'

        pop1 = {ID: population.individuals.pop(ID) for ID in ID1s}
        pop2 = {ID: population.individuals.pop(ID) for ID in ID2s}

        # add back
        for ID in ID1s:
            new_id = sp2 + '_' + ID.rsplit("_", 1)[1]
            population.individuals[new_id] = pop1.pop(ID)
            population.individuals[new_id].id = new_id

        for ID in ID2s:
            new_id = sp1 + '_' + ID.rsplit("_", 1)[1]
            population.individuals[new_id] = pop2.pop(ID)
            population.individuals[new_id].id = new_id


        population.group_sizes[sp1] = sz2
        population.group_sizes[sp2] = sz1

        self.logger.write(
            f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=swap,subpops={args.subpops[0]},{args.subpops[1]},size1={sz1},size2={sz2}\n'
        )

        return []
