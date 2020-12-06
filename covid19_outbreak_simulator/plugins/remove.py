import random

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin


class remove(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'after_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(remove, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(remove, self).get_parser()
        parser.prog = '--plugin remove'
        parser.description = 'remove individuals from the population'
        parser.add_argument(
            'popsize',
            nargs='+',
            help='''Number of individuals to be removed, which can be from
            the entire population, or from specific groups
            (e.g. nurse=10) if there are groups.''')
        return parser

    def apply(self, time, population, args=None):
        events = []
        for ps in args.popsize:
            name = ps.split('=', 1)[0] if '=' in ps else ''
            sz = int(ps.split('=', 1)[1]) if '=' in ps else int(ps)

            if name not in population.group_sizes:
                raise ValueError(f'Subpopulation {name} does not exist')

            IDs = [x for x in population.ids if x.startswith(name) and x[len(name):].isnumeric()]
            random.shuffle(IDs)
            for ID in IDs[:sz]:
                population.remove(ID)
            removed_list = f',removed={",".join(IDs[:sz])}' if args.verbosity > 1 else ''
            if args.verbosity > 0:
                self.logger.write(f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=remove,subpop={name},size={sz}{removed_list}\n')
        return events
