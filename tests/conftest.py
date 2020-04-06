import pytest

from covid19_outbreak_simulator.model import Params, Model, get_default_params


@pytest.fixture
def params():
    return Params()


@pytest.fixture
def default_params():
    return get_default_params()


@pytest.fixture
def default_model():
    return Model(get_default_params())