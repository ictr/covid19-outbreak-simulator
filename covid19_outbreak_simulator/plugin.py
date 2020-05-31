

class BasePlugin(object):

    def __init__(self, simulator, population, *args, **kwargs):
        self.simulator = simulator
        self.population = population
        self.logger = self.simulator.logger