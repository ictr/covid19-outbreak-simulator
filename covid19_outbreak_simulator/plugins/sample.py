import random

from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.event import EventType

#
# This plugin take random samples from the population during evolution.
#
class sample(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(sample, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(sample, self).get_parser()
        parser.prog = '--plugin sample'
        parser.description = 'Draw random sample from the population'
        grp = parser.add_mutually_exclusive_group(required=True)
        grp.add_argument(
            '--proportion',
            type=float,
            help='''Proprotion of the population to sample.''')
        grp.add_argument(
            '--size', type=int, help='''Number of individuals to sample.''')
        return parser

    def apply(self, time, population, args=None):
        stat = {}

        if args.proportion:
            sz = int(args.proportion * len(population))
            stat['proportion'] = '{:.3f}'.format(args.proportion)
        elif args.size:
            sz = min(args.size, len(population))
            stat['size'] = args.size
        #
        # draw a random sample
        samples = [1] * sz + [0] * (len(population) - sz)
        random.shuffle(samples)

        stat['n_recovered'] = len([
            x for s, (x, ind) in zip(samples, population.items())
            if isinstance(ind.recovered, float) and s
        ])
        stat['n_infected'] = len([
            x for s, (x, ind) in zip(samples, population.items())
            if ind.infected not in (False, None) and s
        ])
        stat['n_popsize'] = len(
            [x for s, (x, ind) in zip(samples, population.items()) if s])
        stat['incidence_rate'] = '0' if stat[
            'n_popsize'] == 0 else '{:.5f}'.format(
                (stat['n_infected']) / stat['n_popsize'])
        stat['seroprevalence'] = '0' if stat[
            'n_popsize'] == 0 else '{:.5f}'.format(
                (stat['n_recovered'] + stat['n_infected']) / stat['n_popsize'])
        param = ','.join(f'{k}={v}' for k, v in stat.items())
        if args.verbosity > 0:
            self.logger.write(f'{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=sample,{param}\n')
        return []
