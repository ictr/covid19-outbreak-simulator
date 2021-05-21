import pytest
from itertools import product
from covid19_outbreak_simulator.population import Individual
from covid19_outbreak_simulator.event import EventType


def test_individual(default_model, logger):
    ind = Individual('group1_0', 1.2, default_model, logger)

    assert ind.infected is False
    assert ind.quarantined is False

    assert ind.r0 is None
    assert ind.incubation_period is None


def test_quarantine(individual):
    res = individual.quarantine(till=2)

    assert individual.quarantined == 2
    assert len(res) == 1
    assert res[0].action == EventType.REINTEGRATION
    assert res[0].time == 2
    assert res[0].target == individual.id

    res = individual.reintegrate()

    assert not res
    assert individual.quarantined is False


def test_quarantine_error(individual):
    with pytest.raises(ValueError):
        individual.quarantine()


def test_infect(individual):
    individual.model.draw_prop_asym_carriers()
    #
    res = []
    for x in range(1000):
        individual.infected = None
        res += individual.infect(5.0, by=None)
    regular = len(res)
    assert res

    individual.susceptibility = 0
    res = []
    for x in range(100):
        individual.infected = None
        res += individual.infect(5.0, by=None)
    assert not res

    # 80% of infection events would fail
    individual.susceptibility = 0.2
    res = []
    for x in range(1000):
        individual.infected = None
        res += individual.infect(5.0, by=None)
    assert len(res) > regular * 0.10 and len(res) < regular * 0.30


def test_infect_infected(individual_factory):
    ind = individual_factory(id='1')
    ind1 = individual_factory(id='3')
    ind.model.draw_prop_asym_carriers()
    ind.infected = 5.5

    res = ind.infect(5.0, by=ind1.id)

    assert not res


def test_infect_with_leadtime(individual_factory):
    ind = individual_factory(id='1')
    ind.model.draw_prop_asym_carriers()
    res = ind.infect(5.0, by=None, leadtime=True)

    assert ind.infected != 5.0


@pytest.mark.parametrize(
    'by, handle_symptomatic, proportion, quarantined, leadtime',
    product([None, 1], ['keep', 'remove', 'quarantine', 'quarantine_14'],
            [None, 0, 0.2, 1], [True, False], [None, 2, 'any', 'asymptomatic']))
def test_symptomatic_infect(individual_factory, by, handle_symptomatic,
                            proportion, quarantined, leadtime):
    ind1 = individual_factory(id='1')
    ind2 = individual_factory(id='2')

    ind1.model.draw_prop_asym_carriers()
    if quarantined:
        ind1.quarantine(till=20)
    #
    if proportion is None:
        res = ind1.symptomatic_infect(
            5.0,
            by=None if by is None or leadtime is not None else ind2.id,
            handle_symptomatic=[handle_symptomatic],
            leadtime=leadtime)
    else:
        res = ind1.symptomatic_infect(
            5.0,
            by=None if by is None or leadtime is not None else ind2.id,
            handle_symptomatic=[handle_symptomatic, proportion],
            leadtime=leadtime)

    if leadtime:
        assert ind1.infected != 5.0
    else:
        assert ind1.infected == 5.0
    assert ind1.r0 is not None
    assert ind1.incubation_period is not None


@pytest.mark.parametrize(
    'by, handle_symptomatic, proportion, quarantined, leadtime',
    product([None, 1], ['keep', 'remove', 'quanrantine', 'quarantine_7'],
            ['A', 1], [True, False], [None, 1, 'any', 'asymptomatic']))
def test_asymptomatic_infect(individual_factory, by, handle_symptomatic,
                             proportion, quarantined, leadtime):
    ind1 = individual_factory(id='1')
    ind2 = individual_factory(id='2')

    ind1.model.draw_prop_asym_carriers()
    if quarantined:
        ind1.quarantine(till=20)
    #
    # asymptomatic case does not care about handle_symptomatic and proportion etc
    res = ind1.asymptomatic_infect(
        5.0,
        by=None if by is None or leadtime is not None else ind2.id,
        handle_symptomatic=[handle_symptomatic, proportion],
        leadtime=leadtime)

    if leadtime:
        assert ind1.infected != 5.0
    else:
        assert ind1.infected == 5.0
    assert ind1.r0 is not None
    assert ind1.incubation_period is not None


@pytest.mark.parametrize('immunity, infectivity',
                         product([0, 0.75, 1], [0.2, 0.3]))
def test_vaccination(individual_factory, immunity, infectivity):
    ind = individual_factory(id='1')
    #
    ind.model.params.set_prop_asym_carriers(['0.2'])
    ind.model.draw_prop_asym_carriers()

    assert ind.model.params.prop_asym_carriers == 0.2
    ind.vaccinate(time=0, immunity=immunity, infectivity=infectivity)
    #
    # try to infect the individual
    #
    N = 1000
    N_infected = 0
    N_asymptomatic = 0
    N_symptomatic = 0
    for x in range(N):
        ind.infected = None
        ind.symptomatic = None
        ind.infect(0, by=None)
        N_infected += ind.infected is not None
        if ind.symptomatic == False:
            N_asymptomatic += 1
        elif ind.symptomatic == True:
            N_symptomatic += 1

    if immunity == 1:
        assert N_infected == 0
        assert N_asymptomatic == 0
        assert N_symptomatic == 0
    elif immunity == 0:
        assert N_infected == N
        assert N_asymptomatic / (
            N_asymptomatic +
            N_symptomatic) > 0.2, 'expect {N_asymptomatic/N} to be > 0.2'
    else:
        assert N_infected < N * (1 - immunity + 0.1)
        assert N_infected > N * (1 - immunity - 0.1)
        assert N_asymptomatic / (
            N_asymptomatic +
            N_symptomatic) > 0.2, 'expect {N_asymptomatic/N} to be > 0.2'
