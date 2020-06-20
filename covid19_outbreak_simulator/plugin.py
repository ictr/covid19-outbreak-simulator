class BasePlugin(object):

    def __init__(self, simulator, population, *args, **kwargs):
        self.simulator = simulator
        self.population = population
        self.logger = self.simulator.logger

    def get_parser(self):
        parser = argparse.ArgumentParser(
            description='A plugin for covid19-outbreak-simulator')
        parser.add_argument(
            '--start', type=float, help='''Start time, default to 0''')
        parser.add_argument(
            '--end', type=float, help='''End time, default to none''')
        return parser