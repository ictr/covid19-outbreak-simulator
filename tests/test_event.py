from covid19_outbreak_simulator.simulator import Event, EventType


def test_event_infection(simulator):
    event = Event(0, EventType.INFECTION, target=None, logger=simulator.logger)
