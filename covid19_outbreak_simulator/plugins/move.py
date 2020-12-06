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
        parser.add_argument('IDs',
            nargs='+', help='IDs of individuals to be moved.')
        parser.add_argument('-t', '--to',
            help='Name of the subpopulation of the destination.')
        return parser

    def apply(self, time, population, args=None):
        for ID in args.IDs:
            new_id = population.move(ID, args.to)
            if args.verbosity > 0:
                self.logger.write(f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=move,subpop={args.to},id={ID},new_id={new_id}\n')
        return []
