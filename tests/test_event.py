from covid19_outbreak_simulator.event import Event, EventType


def test_event_infection(simulator):
    event = Event(
        0, EventType.INFECTION, target=None, by=None, logger=simulator.logger)
