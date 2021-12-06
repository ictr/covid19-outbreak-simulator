import pytest
from itertools import product
from covid19_outbreak_simulator.population import Individual
from covid19_outbreak_simulator.event import EventType

from covid19_outbreak_simulator.utils import status_to_condition


@pytest.mark.parametrize(
    "cond",
    [
        "infected",
        "uninfected",
        "recovered",
        "!recovered",
        "quarantined",
        "unquarantined",
        "vaccinated",
        "unvaccinated",
        "all",
        "infected&quarantined",
        "infected|quarantined",
    ],
)
def test_individual_status(default_model, logger, cond):
    ind = Individual("group1_0", 1.2, default_model, logger)

    if cond == "infected":
        ind.infected = 1.0
    elif cond == "uninfected":
        pass
    elif cond == "recovered":
        ind.recovered = 1.2
    elif cond == "!recovered":
        pass
    elif cond == "quarantined":
        ind.quarantined = 1.2
    elif cond == "unquarantined":
        pass
    elif cond == "vaccinated":
        ind.vaccinated = 1.2
    elif cond == "unvaccinated":
        pass
    elif cond == "all":
        pass
    elif cond == "infected&quarantined":
        ind.infected = 1.2
        ind.quarantined = 1.2
    elif cond == "infected|quarantined":
        ind.infected = 1.2

    assert status_to_condition(cond)(ind), f"assert {cond} failed"


@pytest.mark.parametrize(
    "cond",
    [
        "infected",
        "uninfected",
        "recovered",
        "!recovered",
        "quarantined",
        "unquarantined",
        "vaccinated",
        "unvaccinated",
        "infected&quarantined",
        "infected|quarantined",
    ],
)
def test_individual_negative_status(default_model, logger, cond):
    ind = Individual("group1_0", 1.2, default_model, logger)

    if cond == "infected":
        pass
    elif cond == "uninfected":
        ind.infected = 1.0
    elif cond == "recovered":
        pass
    elif cond == "!recovered":
        ind.recovered = 1.2
    elif cond == "quarantined":
        pass
    elif cond == "unquarantined":
        ind.quarantined = 1.2
    elif cond == "vaccinated":
        pass
    elif cond == "unvaccinated":
        ind.vaccinated = 1.2
    elif cond == "infected&quarantined":
        pass
    elif cond == "infected|quarantined":
        pass

    assert not status_to_condition(cond)(ind), f"negative assert {cond} failed"
