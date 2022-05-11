from enum import Enum
import random
from covid19_outbreak_simulator.utils import parse_handle_symptomatic_options


class EventType(Enum):
    # START
    START = 0
    # Infection
    INFECTION = 1
    # infection failed due to perhaps no more people to infect
    INFECTION_FAILED = 2
    # infection event happens during quarantine
    INFECTION_AVOIDED = 3
    # infection event happens to an infected individual
    INFECTION_IGNORED = 4
    # recover (no longer infectious)
    RECOVER = 5

    # removal of individual showing symptom
    SHOW_SYMPTOM = 6
    REMOVAL = 7
    # quarantine individual given a specified time
    QUARANTINE = 8
    # reintegrate individual to the population (release from quarantine)
    REINTEGRATION = 9
    # population statistics
    STAT = 10
    # abort simulation, right now due to infector showing symptoms during quarantine
    ABORT = 11
    # end of simulation
    END = 12
    # ERROR
    ERROR = 13
    WARNING = 14
    #
    PLUGIN = 15

    # vaccine shot
    VACCINATION = 16
    REPLACEMENT = 17
    CONTACT_TRACING = 19


class Event(object):
    """
    Events that happen during the simulation.
    """

    def __init__(
        self, time, action, target=None, logger=None, priority=False, **kwargs
    ):
        self.time = time
        self.action = action
        if target is None or hasattr(target, "id"):
            self.target = target
        else:
            raise ValueError(
                f"Target of events should be None or an individual: {target} of type {target.__class__.__name__} provided"
            )
        self.logger = logger
        self.kwargs = kwargs
        self.priority = priority

    def apply(self, population):
        if self.action == EventType.INFECTION:
            if "by" not in self.kwargs:
                raise ValueError("Parameter by is required for INECTION event.")

            if self.kwargs["by"] is not None:
                # if infector is removed or quarantined
                if self.kwargs["by"].id not in population:
                    self.logger.write(
                        f'{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={self.kwargs["by"]},reason=REMOVED\n'
                    )
                    return []
                #
                by_ind = self.kwargs["by"]
                if by_ind.quarantined and by_ind.quarantined >= self.time:
                    self.logger.write(
                        f"{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={by_ind},reason=QUARANTINED\n"
                    )
                    return []
                #
                if self.kwargs.get("handle_infection", None) is not None:
                    if self.kwargs["handle_infection"] != "ignore=t/7<2":
                        raise ValueError(
                            f"Currently handle-infection only support option ignore=t/7<2"
                        )
                    if self.time % 7 < 2:
                        self.logger.write(
                            f'{self.time:.2f}\t{EventType.INFECTION_IGNORED.name}\t.\tby={self.kwargs["by"]},reason=t/7<2\n'
                        )
                        return []

            # determin einfectee
            if self.target is not None:
                # if the target is preselected (e.g. through init plugin or infector)
                if self.target.id not in population:
                    self.logger.write(
                        f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=INFECTION target no longer exists\n"
                    )
                    return []
                infectee = self.target
            else:
                # select infectee from the population, subject to vicinity of infector
                infectee = population.select(infector=self.kwargs["by"].id)

                if not infectee:
                    self.logger.write(
                        f'{self.time:.2f}\t{EventType.INFECTION_FAILED.name}\t{self.target}\tby={self.kwargs["by"]},reason=no_infectee\n'
                    )
                    return []
            #
            return infectee.infect(self.time, **self.kwargs)
        elif self.action == EventType.QUARANTINE:
            if self.target.id not in population:
                self.logger.write(
                    f'{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\treason={self.kwargs["reason"]},msg=QUARANTINE target no longer exists.\n'
                )
                return []
            if isinstance(self.target.quarantined, float):
                self.logger.write(
                    f'{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\treason={self.kwargs["reason"]},msg=QUARANTINE target already quarantined\n'
                )
                return []
            self.logger.write(
                f'{self.time:.2f}\t{EventType.QUARANTINE.name}\t{self.target}\ttill={self.kwargs["till"]:.2f},reason={self.kwargs["reason"]},infected={isinstance(self.target.infected, float)},recovered={isinstance(self.target.recovered, float)}\n'
            )
            return self.target.quarantine(**self.kwargs)

        elif self.action == EventType.REINTEGRATION:
            # reintegrate from REPLACEMENT
            if hasattr(self.target, "replaced_by"):
                restore_to = self.target.replaced_by
                while True:
                    if restore_to.id in population:
                        break
                    try:
                        restore_to = restore_to.replaced_by
                        #
                        # case:
                        # A replaced by  B [B in, A out]
                        # B replaced by  C [C in, A, B out]
                        #
                        # A reintegrate with B, B restore to C,, C is in
                    except Exception as e:
                        self.logger.write(
                            f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tfailed to restore {restore_to}.\n"
                        )
                        # case:
                        # A replaced by  B [B in, A out]
                        # B replaced by  C [C in, A, B out]
                        #
                        # A reintegrate with C [A in, B out, C out]
                        #
                        # try to reintegrate B
                        # B replaced by C, C is not in population, and there is no replaced by
                        return []

                population.individuals.pop(restore_to.id)
                population.individuals[self.target.id] = self.target
                self.target.reintegrate(time=self.time, **self.kwargs)
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.REINTEGRATION.name}\t{self.target}\treason=replacement,with={restore_to}\n"
                )
                return []

            # reintegrate from quarantine
            if self.target.id not in population:
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=REINTEGRATION target no longer exists\n"
                )
                return []
            elif not isinstance(self.target.quarantined, float):
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=REINTEGRATION target is not in quarantine\n"
                )
                return []
            else:
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.REINTEGRATION.name}\t{self.target}\treason=quarantine\n"
                )
                return self.target.reintegrate(time=self.time, **self.kwargs)

        elif self.action == EventType.INFECTION_AVOIDED:
            self.logger.write(
                f'{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={self.kwargs["by"]}\n'
            )
            return []

        elif self.action == EventType.SHOW_SYMPTOM:
            if self.target.id in population:
                self.target.show_symptom = self.time
                handle_symptomatic = parse_handle_symptomatic_options(
                    self.kwargs.get("handle_symptomatic", None),
                    self.kwargs.get("handle_symptomatic_vaccinated", None),
                    self.kwargs.get("handle_symptomatic_unvaccinated", None),
                    self.target.group,
                    isinstance(self.target.vaccinated, float),
                )
                tracing = handle_symptomatic.get("tracing", None)
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.SHOW_SYMPTOM.name}\t{self.target}\thandle_symptomatic={self.kwargs.get('handle_symptomatic', None)}\n"
                )
                if tracing is not None and tracing > 0.0:
                    return [
                        Event(
                            self.time,
                            EventType.CONTACT_TRACING,
                            target=self.target,
                            reason="symptoms",
                            handle_traved=[
                                self.kwargs.get("handle_symptomatic", None),
                                self.kwargs.get("handle_symptomatic_vaccinated", None),
                                self.kwargs.get(
                                    "handle_symptomatic_unvaccinated", None
                                ),
                            ],
                            logger=self.logger,
                        )
                    ]
            else:
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=SHOW_SYMPTOM target no longer exists\n"
                )
            return []

        elif self.action == EventType.CONTACT_TRACING:
            handle_infection = parse_handle_symptomatic_options(
                *self.kwargs["handle_traced"],
                self.target.group,
                isinstance(self.target.vaccinated, float),
            )
            succ_rate = handle_infection.get("tracing", None)

            IDs = []
            missed_IDs = []
            events = []
            for ind in population.values():
                if getattr(ind, "infected_by", None) == self.target:
                    if random.random() > succ_rate:
                        missed_IDs.append(ind.id)
                        continue
                    IDs.append(ind.id)
                    if handle_infection["reaction"] == "remove":
                        events.append(
                            Event(
                                self.time,
                                EventType.REMOVAL,
                                reason=f"contact tracing (by {self.target})",
                                target=ind,
                                logger=self.logger,
                            )
                        )
                    elif handle_infection["reaction"] == "quarantine":
                        duration = handle_infection.get("duration", 14)
                        events.append(
                            Event(
                                self.time,
                                EventType.QUARANTINE,
                                target=ind,
                                logger=self.logger,
                                till=self.time + duration,
                                reason=f"contact tracing ({ind.infected} by {self.target})",
                            )
                        )
                    elif handle_infection["reaction"] == "replace":
                        duration = handle_infection.get("duration", 14)
                        events.append(
                            Event(
                                self.time,
                                EventType.REPLACEMENT,
                                reason=f"contact tracing (by {self.target})",
                                till=self.time + duration,
                                keep=["vaccinated"],
                                target=ind,
                                logger=self.logger,
                            )
                        )
                    elif handle_infection["reaction"] == "reintegrate":
                        events.append(
                            Event(
                                self.time,
                                EventType.REINTEGRATION,
                                target=ind,
                                logger=self.logger,
                            )
                        )
                    elif handle_infection["reaction"] != "keep":
                        raise ValueError(
                            f"Unsupported action for patients who test positive: {handle_infection}"
                        )
            self.logger.write(
                f"{self.time:.2f}\t{EventType.CONTACT_TRACING.name}\t{self.target}\tsucc_rate={succ_rate},reason={self.kwargs['reason']},n_traced={len(IDs)},n_missed={len(missed_IDs)},handle_infection={handle_infection}\n"
            )
            return events
        elif self.action == EventType.REMOVAL:
            if self.target.id in population:
                population.remove(self.target)
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.REMOVAL.name}\t{self.target}\tpopsize={len(population)},reason={self.kwargs.get('reason', 'unspecified')}\n"
                )
            else:
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=REMOVAL target no longer exists\n"
                )
            return []

        elif self.action == EventType.VACCINATION:
            if self.target.id in population:
                self.target.vaccinate(self.time, **self.kwargs)
                self.logger.write(
                    f'{self.time:.2f}\t{EventType.VACCINATION.name}\t{self.target}\timmunity={self.kwargs["immunity"]},infectivity={self.kwargs["infectivity"]}\n'
                )
            else:
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=VACCINATION target no longer exists\n"
                )
            return []

        elif self.action == EventType.REPLACEMENT:
            if self.target.id not in population:
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=REPLACEMENT target no longer exists\n"
                )
                return []

            by_ind = population.replace(self.target, **self.kwargs)

            self.logger.write(
                f'{self.time:.2f}\t{EventType.REPLACEMENT.name}\t{self.target}\treason={self.kwargs["reason"]},infected={"False" if self.target.infected is False else "True"},by={by_ind}\n'
            )
            if "till" in self.kwargs:
                till = self.kwargs["till"]
                if till is None:
                    return []
                return [
                    Event(
                        till,
                        EventType.REINTEGRATION,
                        target=self.target,
                        logger=self.logger,
                    )
                ]
            else:
                return []

        elif self.action == EventType.RECOVER:
            removed = self.target.id not in population

            if not removed:
                self.target.recovered = self.time
                self.target.immunity = population.model.params.immunity_of_recovered
                self.target.infectivity = (
                    population.model.params.infectivity_of_recovered
                )
            else:
                self.logger.write(
                    f"{self.time:.2f}\t{EventType.WARNING.name}\t{self.target}\tmsg=RECOVER target no longer exists\n"
                )
                return []

            n_recovered = len(
                [
                    x
                    for x, ind in population.items()
                    if ind.recovered not in (False, None)
                ]
            )
            n_infected = len(
                [
                    x
                    for x, ind in population.items()
                    if ind.infected not in (False, None)
                ]
            )
            params = dict(
                recovered=n_recovered, infected=n_infected, popsize=len(population)
            )
            if removed:
                params[removed] = True
            param = ",".join(f"{x}={y}" for x, y in params.items())
            self.logger.write(
                f"{self.time:.2f}\t{EventType.RECOVER.name}\t{self.target}\t{param}\n"
            )
            return []
        else:
            raise RuntimeError(f"Unrecognized action {self.action}")

    def __str__(self):
        return f'{self.action.name}_{self.target if self.target is not None else ""}_at_{self.time:.2f}'
