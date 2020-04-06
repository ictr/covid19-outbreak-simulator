from covid19_outbreak_simulator.simulator import Event, EventType


def test_event_infection(simulator):
    event = Evemt(0, EventType.INFECT, target=None, logger=simulator.logger)
