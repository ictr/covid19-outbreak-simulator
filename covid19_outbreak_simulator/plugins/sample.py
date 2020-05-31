import argparse
from covid19_outbreak_simulator.plugin import BasePlugin


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
            '--url',
            help='''URL to the raw sos file, which will be linked
            to filenames in the HTML output''')
        return parser

    def apply(self, time, args=None):
        self.logger.write(f'{self.logger.id}\t{time:.2f}\tWHATEVER\t.\t.\n')
        return []