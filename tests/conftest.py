import pytest
import os

from covid19_outbreak_simulator.model import Params, Model
from covid19_outbreak_simulator.simulator import Simulator
from covid19_outbreak_simulator.population import Individual, Population
from argparse import Namespace


@pytest.fixture
def params():
    return Params()


@pytest.fixture
def default_model():
    return Model(Params())


@pytest.fixture
def logger():
    with open('test.log', 'w') as logger:
        logger.id = 1
        yield logger

@pytest.fixture
def clear_log():
    if os.path.isfile('simulation.log'):
        os.remove('simulation.log')

@pytest.fixture
def simulator(params, logger):
    simu_args = Namespace()
    simu_args.popsize = 64
    simu_args.repeat = 1
    simu_args.handle_symptomatic = 'remove'

    return Simulator(params=params, logger=logger, simu_args=simu_args, cmd=[])


@pytest.fixture
def individual(default_model, logger):
    return Individual('group_0', 0.8, default_model, logger)


@pytest.fixture
def individual_factory(default_model, logger):
    return lambda id: Individual(id, 1.2, default_model, logger)


@pytest.fixture
def population_factory(default_model, logger):
    def get_population(**kwargs):
        return Population(popsize=kwargs.pop('popsize', ['100']),
            model=default_model, logger=logger,
            vicinity=kwargs.pop('vicinity', None))

    return get_population