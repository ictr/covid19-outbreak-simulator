import pytest
from itertools import product
from covid19_outbreak_simulator.simulator import Individual, EventType


def test_individual(default_model, logger):
    ind = Individual(0, default_model, logger)

    assert ind.infected is None
    assert ind.quarantined is None
    assert ind.n_infectee == 0

    assert ind.r0 is None
    assert ind.incubation_period is None


def test_quarantine(individual):
    res = individual.quarantine(till=2)

    assert individual.quarantined == 2
    assert len(res) == 1
    assert res[0].action == EventType.REINTEGRATION
    assert res[0].time == 2
    assert res[0].target == individual

    res = individual.reintegrate()

    assert not res
    assert individual.quarantined is None


def test_infect(individual):
    individual.model.draw_prop_asym_carriers()
    res = individual.infect(5.0, by=None)


def test_infect_infected(individual_factory):
    ind = individual_factory(id=1)
    ind1 = individual_factory(id=3)
    ind.model.draw_prop_asym_carriers()
    ind.infected = 5.5

    res = ind.infect(5.0, by=ind1)

    assert not res


@pytest.mark.parametrize('by, keep_symptomatic, quarantined',
                         product([None, 1], [True, False], [True, False]))
def test_symptomatic_infect(individual_factory, by, keep_symptomatic,
                            quarantined):
    ind1 = individual_factory(id=1)
    ind2 = individual_factory(id=2)

    ind1.model.draw_prop_asym_carriers()
    if quarantined:
        ind2.quarantine(20)
    #
    res = ind1.symptomatic_infect(
        5.0, by=None if by is None else ind2, keep_symptomatic=keep_symptomatic)

    assert ind1.infected == 5.0
    assert ind1.r0 is not None
    assert ind1.incubation_period is not None


@pytest.mark.parametrize('by, keep_symptomatic, quarantined',
                         product([None, 1], [True, False], [True, False]))
def test_asymptomatic_infect(individual_factory, by, keep_symptomatic,
                             quarantined):
    ind1 = individual_factory(id=1)
    ind2 = individual_factory(id=2)

    ind1.model.draw_prop_asym_carriers()
    if quarantined:
        ind2.quarantine(20)
    #
    res = ind1.asymptomatic_infect(
        5.0, by=None if by is None else ind2, keep_symptomatic=keep_symptomatic)

    assert ind1.infected == 5.0
    assert ind1.r0 is not None
    assert ind1.incubation_period is not None