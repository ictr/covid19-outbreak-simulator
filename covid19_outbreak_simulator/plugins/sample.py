import argparse
from covid19_outbreak_simulator.plugin import BasePlugin
import random


#
# This plugin take random samples from the population during evolution.
#
class RandomSampler(BasePlugin):

    # events that will trigger this plugin
    events = set()

    def __init__(self, *args, **kwargs):
        # this will set self.population, self.simualtor, self.logger
        super(RandomSampler, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = argparse.ArgumentParser(
            'Draw random sample from the population'
            '')
        parser.add_argument(
            '--sample-proportion',
            type=float,
            help='''Proprotion of the population to sample.''')
        parser.add_argument(
            '--sample-size',
            type=int,
            help='''Number of individuals to sample.''')
        return parser

    def apply(self, time, args=None):
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

        stat[f'n_recovered'] = len([
            x for s, (x, ind) in zip(samples, self.population.items())
            if ind.recovered is True and s
        ])
        stat[f'n_infected'] = len([
            x for s, (x, ind) in zip(samples, self.population.items())
            if ind.infected not in (False, None) and s
        ])
        stat[f'n_popsize'] = len(
            [x for s, (x, ind) in zip(samples, self.population.items())])
        stat[f'n_seroprevalence'] = '0' if stat[
            f'n_popsize'] == 0 else '{:.3f}'.format(
                (stat[f'n_recovered'] + stat[f'n_infected']) /
                stat[f'n_popsize'])
        param = ','.join(f'{k}={v}' for k, v in stat.items())
        self.logger.write(f'{self.logger.id}\t{time:.2f}\tSAMPLE\t.\t{param}\n')
        return []