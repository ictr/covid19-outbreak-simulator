import pytest

from covid19_outbreak_simulator.model import Params, Model, get_default_params
from covid19_outbreak_simulator.simulator import Simulator, Individual
from argparse import Namespace


@pytest.fixture
def params():
    return Params()


@pytest.fixture
def default_params():
    return get_default_params()


@pytest.fixture
def default_model():
    return Model(get_default_params())


@pytest.fixture
def logger():
    with open('test.log', 'w') as logger:
        logger.id = 1
        yield logger


@pytest.fixture
def simulator(default_params, logger):
    simu_args = Namespace()
    simu_args.popsize = 64
    simu_args.repeat = 1
    simu_args.keep_symptomatic = True
    simu_args.pre_quarantine = None

    return Simulator(params=default_params, logger=logger, simu_args=simu_args)


@pytest.fixture
def individual(default_model, logger):
    return Individual(0, default_model, logger)


@pytest.fixture
def individual_factory(default_model, logger):
    return lambda id: Individual(id, default_model, logger)