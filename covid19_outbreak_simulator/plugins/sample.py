import argparse
from covid19_outbreak_simulator.plugin import BasePlugin
import random


#
# This plugin take random samples from the population during evolution.
#
class sample(BasePlugin):

    # events that will trigger this plugin
    events = set()

    def __init__(self, *args, **kwargs):
        # this will set self.population, self.simualtor, self.logger
        super(sample, self).__init__(*args, **kwargs)
        self.last_sampled = None

    def get_parser(self):
        parser = super(sample, self).get_parser()
        parser.prog = '--plugin sample'
        parser.description = 'Draw random sample from the population'
        parser.add_argument(
            '--sample-proportion',
            type=float,
            help='''Proprotion of the population to sample.''')
        parser.add_argument(
            '--sample-size',
            type=int,
            help='''Number of individuals to sample.''')
        parser.add_argument(
            '--sample-interval',
            default=1,
            type=float,
            help='''Sampling interval, default to 1.''')
        return parser

    def apply(self, time, args=None):
        if self.last_sampled is not None and time - self.last_sampled < args.sample_interval:
            return []

        self.last_sampled = time
        stat = {}

        if args.sample_proportion:
            sz = int(args.sample_proportion * len(self.population))
            stat['sample_proportion'] = '{:.3f}'.format(args.sample_proportion)
        elif args.sample_size:
            sz = min(args.sample_size, len(self.population))
            stat['sample_size'] = args.sample_size
        #
        # draw a random sample
        samples = [1] * sz + [0] * (len(self.population) - sz)
        random.shuffle(samples)

        stat['n_recovered'] = len([
            x for s, (x, ind) in zip(samples, self.population.items())
            if ind.recovered not in (None, False) and s
        ])
        stat['n_infected'] = len([
            x for s, (x, ind) in zip(samples, self.population.items())
            if ind.infected not in (False, None) and s
        ])
        stat['n_popsize'] = len(
            [x for s, (x, ind) in zip(samples, self.population.items()) if s])
        stat['incidence_rate'] = '0' if stat[
            'n_popsize'] == 0 else '{:.4f}'.format(
                (stat['n_infected']) / stat['n_popsize'])
        stat['seroprevalence'] = '0' if stat[
            'n_popsize'] == 0 else '{:.4f}'.format(
                (stat['n_recovered'] + stat['n_infected']) / stat['n_popsize'])
        param = ','.join(f'{k}={v}' for k, v in stat.items())
        self.logger.write(f'{self.logger.id}\t{time:.2f}\tSAMPLE\t.\t{param}\n')
        return []