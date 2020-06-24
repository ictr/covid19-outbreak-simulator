import pytest

from covid19_outbreak_simulator.model import Params, Model
from covid19_outbreak_simulator.simulator import Simulator, Individual
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
def simulator(params, logger):
    simu_args = Namespace()
    simu_args.popsize = 64
    simu_args.repeat = 1
    simu_args.handle_symptomatic = 'remove'

    return Simulator(params=params, logger=logger, simu_args=simu_args, cmd=[])


@pytest.fixture
def individual(default_model, logger):
    return Individual('0', 'group', 0.8, default_model, logger)


@pytest.fixture
def individual_factory(default_model, logger):
    return lambda id: Individual(id, 'group 2', 1.2, default_model, logger)
