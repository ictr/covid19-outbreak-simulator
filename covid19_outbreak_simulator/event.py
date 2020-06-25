from enum import Enum

import numpy as np


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


class Event(object):
    '''
    Events that happen during the simulation.
    '''

    def __init__(self,
                 time,
                 action,
                 target=None,
                 logger=None,
                 priority=False,
                 **kwargs):
        self.time = time
        self.action = action
        if target is None or isinstance(target, str):
            self.target = target
        else:
            raise ValueError(
                f'Target of events should be None or an ID: {target} of type {target.__class__.__name__} provided'
            )
        self.logger = logger
        self.kwargs = kwargs
        self.priority = priority

    def apply(self, population):
        if self.action == EventType.INFECTION:
            if self.target is not None:
                selected = self.target
            else:
                selected = population.select(exclude=self.target)

                if not selected:
                    self.logger.write(
                        f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_FAILED.name}\t{self.target}\tby={self.kwargs["by"]}\n'
                    )
                    return []
            if 'by' not in self.kwargs:
                raise ValueError('Parameter by is required for INECTION event.')
            if self.kwargs['by'] in population:
                by_ind = population[self.kwargs['by']]
                if by_ind.quarantined and by_ind.quarantined >= self.time:
                    self.logger.write(
                        f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={by_ind.id}\n'
                    )
                    return []
            return population[selected].infect(self.time, **self.kwargs)
        elif self.action == EventType.QUARANTINE:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.QUARANTINE.name}\t{self.target}\ttill={self.kwargs["till"]:.2f}\n'
            )
            return population[self.target].quarantine(**self.kwargs)
        elif self.action == EventType.REINTEGRATION:
            if self.target not in population:
                return []
            else:
                self.logger.write(
                    f'{self.logger.id}\t{self.time:.2f}\t{EventType.REINTEGRATION.name}\t{self.target}\tsucc=True\n'
                )
                return population[self.target].reintegrate(**self.kwargs)
        elif self.action == EventType.INFECTION_AVOIDED:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={self.kwargs["by"]}\n'
            )
            return []
        elif self.action == EventType.SHOW_SYMPTOM:
            if self.target in population:
                population[self.target].show_symptom = self.time
                self.logger.write(
                    f'{self.logger.id}\t{self.time:.2f}\t{EventType.SHOW_SYMPTOM.name}\t{self.target}\t.\n'
                )
            else:
                self.logger.write(
                    f'{self.logger.id}\t{self.time:.2f}\t{EventType.SHOW_SYMPTOM.name}\t{self.target}\tsucc=False\n'
                )
            return []
        elif self.action == EventType.REMOVAL:
            if self.target in population:
                population.remove(self.target)
                self.logger.write(
                    f'{self.logger.id}\t{self.time:.2f}\t{EventType.REMOVAL.name}\t{self.target}\tpopsize={len(population)}\n'
                )
            else:
                self.logger.write(
                    f'{self.logger.id}\t{self.time:.2f}\t{EventType.REMOVAL.name}\t{self.target}\tpopsize={len(population)},already_removed=True\n'
                )
            return []
        elif self.action == EventType.RECOVER:
            removed = self.target not in population

            if not removed:
                population[self.target].recovered = self.time

            n_recovered = len([
                x for x, ind in population.items()
                if ind.recovered not in (False, None)
            ])
            n_infected = len([
                x for x, ind in population.items()
                if ind.infected not in (False, None)
            ])
            params = dict(
                recovered=n_recovered,
                infected=n_infected,
                popsize=len(population))
            if removed:
                params[removed] = True
            param = ','.join(f'{x}={y}' for x, y in params.items())
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.RECOVER.name}\t{self.target}\t{param}\n'
            )
            return []
        else:
            raise RuntimeError(f'Unrecognized action {self.action}')

    def __str__(self):
        return f'{self.action.name}_{self.target if self.target is not None else ""}_at_{self.time:.2f}'
