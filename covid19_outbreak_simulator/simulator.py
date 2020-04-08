from enum import Enum

import random
import numpy as np
from collections import defaultdict

from .model import Model


class Individual(object):

    def __init__(self, id, model, logger):
        self.id = id
        self.model = model
        self.logger = logger

        self.infected = None
        self.quarantined = None
        self.n_infectee = 0

        self.r0 = None
        self.incubation_period = None

    def quarantine(self, till):
        self.quarantined = till
        return [Event(till, EventType.REINTEGRATION, self, logger=self.logger)]

    def reintegrate(self):
        self.quarantined = None
        return []

    def symptomatic_infect(self, time, **kwargs):
        self.infected = time
        self.r0 = self.model.draw_random_r0(symptomatic=True)
        self.incubation_period = self.model.draw_random_incubation_period()

        by = kwargs.get('by', None)

        if by is None and 'allow_lead_time' in kwargs:
            # this is the first infection, the guy should be asymptomatic, but
            # could be anywhere in his incubation period
            lead_time = np.random.uniform(0, self.incubation_period)
        else:
            lead_time = 0

        keep_symptomatic = kwargs.get('keep_symptomatic', False)

        # REMOVAL ...
        evts = [
            Event(
                time + self.incubation_period - lead_time,
                EventType.SHOW_SYMPTOM,
                self,
                logger=self.logger)
        ]
        if not keep_symptomatic:
            if self.quarantined and time + self.incubation_period - lead_time < self.quarantined:
                # scheduling ABORT
                evts.append(
                    Event(
                        time + self.incubation_period - lead_time,
                        EventType.ABORT,
                        self,
                        logger=self.logger))
            else:
                evts.append(
                    # scheduling REMOVAL
                    Event(
                        time + self.incubation_period - lead_time,
                        EventType.REMOVAL,
                        self,
                        logger=self.logger))
        #
        x_grid, trans_prob = self.model.get_symptomatic_transmission_probability(
            self.incubation_period, self.r0)
        # infect only before removal
        if keep_symptomatic:
            x_before = x_grid
        else:
            x_before = [
                x for x in x_grid if x < self.incubation_period - lead_time
            ]
        infected = np.random.binomial(1, trans_prob[:len(x_before)],
                                      len(x_before))
        presymptomatic_infected = [
            xx for xx, ii in zip(x_before, infected)
            if ii and xx < self.incubation_period
        ]
        symptomatic_infected = [
            xx for xx, ii in zip(x_before, infected)
            if ii and xx >= self.incubation_period
        ]
        if self.quarantined:
            for idx, x in enumerate(x_before):
                if time + x < self.quarantined and infected[idx] != 0:
                    evts.append(
                        Event(
                            time + x,
                            EventType.INFECTION_AVOIDED,
                            self.id,
                            logger=self.logger,
                            by=self))
                    infected[idx] = 0
        #
        for x, infe in zip(x_before, infected):
            if infe:
                evts.append(
                    Event(
                        time + x,
                        EventType.INFECTION,
                        None,
                        logger=self.logger,
                        by=self))

        if by:
            by.n_infectee += 1
            params = [f'by={by.id}']
        elif lead_time:
            params = [f'leadtime={lead_time:.2f}']
        else:
            params = []
        #
        params.extend([
            f'r0={self.r0:.2f}',
            f'r={sum(infected)}',
            f'r_presym={len(presymptomatic_infected)}',
            f'r_sym={len(symptomatic_infected)}',
            f'incu={self.incubation_period:.2f}',
        ])
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION.name}\t{self.id}\t{",".join(params)}\n'
        )
        return evts

    def asymptomatic_infect(self, time, **kwargs):
        self.infected = time
        self.r0 = self.model.draw_random_r0(symptomatic=False)
        self.incubation_period = -1

        by = kwargs.get('by',)

        if by is None and 'allow_lead_time' in kwargs:
            # this is the first infection, the guy should be asymptomatic, but
            # could be anywhere in his incubation period
            lead_time = np.random.uniform(0, 10)
        else:
            lead_time = 0

        # REMOVAL ...
        evts = []
        #
        x_grid, trans_prob = self.model.get_asymptomatic_transmission_probability(
            self.r0)

        if lead_time > 0:
            idx = int(lead_time / self.model.params.simulation_interval)
            trans_prob = trans_prob[idx:]
            x_grid = x_grid[idx:]
            x_grid = x_grid - x_grid[0]

        # infect only before removal
        infected = np.random.binomial(1, trans_prob, len(x_grid))
        asymptomatic_infected = sum(infected)
        if self.quarantined:
            for idx, x in enumerate(x_grid):
                if time + x < self.quarantined and infected[idx] != 0:
                    evts.append(
                        Event(
                            time + x,
                            EventType.INFECTION_AVOIDED,
                            self.id,
                            logger=self.logger,
                            by=self))
                    infected[idx] = 0
        #
        for x, infe in zip(x_grid, infected):
            if infe:
                evts.append(
                    Event(
                        time + x,
                        EventType.INFECTION,
                        None,
                        logger=self.logger,
                        by=self))

        if by:
            by.n_infectee += 1
            params = [f'by={by.id}']
        elif lead_time > 0:
            params = [f'leadtime={lead_time:.2f}']
        else:
            params = []
        #
        params.extend([
            f'r0={self.r0:.2f}', f'r={asymptomatic_infected}',
            f'r_asym={asymptomatic_infected}'
        ])
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION.name}\t{self.id}\t{",".join(params)}\n'
        )
        return evts

    def infect(self, time, **kwargs):
        if self.infected is not None:
            self.logger.write(
                f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION_IGNORED.name}\t{self.id}\tby={kwargs["by"].id}\n'
            )
            return []

        if self.model.draw_is_asymptomatic():
            return self.asymptomatic_infect(time, **kwargs)
        else:
            return self.symptomatic_infect(time, **kwargs)


class EventType(Enum):
    # Infection
    INFECTION = 1
    # infection failed due to perhaps no more people to infect
    INFECTION_FAILED = 2
    # infection event happens during quarantine
    INFECTION_AVOIDED = 3
    # infection event happens to an infected individual
    INFECTION_IGNORED = 4

    # removal of individual showing symptom
    SHOW_SYMPTOM = 5
    REMOVAL = 6
    # quarantine individual given a specified time
    QUARANTINE = 7
    # reintegrate individual to the population (release from quarantine)
    REINTEGRATION = 8

    # abort simulation, right now due to infector showing symptoms during quarantine
    ABORT = 9
    # end of simulation
    END = 10


class Event(object):
    '''
    Events that happen during the simulation.
    '''

    def __init__(self, time, action, target=None, logger=None, **kwargs):
        self.time = time
        self.action = action
        self.target = target
        self.logger = logger
        self.kwargs = kwargs

    def apply(self, population, simu_args):
        if self.action == EventType.INFECTION:
            if self.target is not None:
                choice = self.target
            else:
                # select one non-quarantined indivudal to infect
                ids = [
                    id for id, ind in population.items()
                    if (not self.target or id != self.target.id) and
                    not ind.quarantined
                ]
                if not ids:
                    self.logger.write(
                        f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_FAILED.name}\t{self.target.id}\tby={self.kwargs["by"].id}\n'
                    )
                    return []
                choice = random.choice(ids)
            return population[choice].infect(
                self.time,
                keep_symptomatic=simu_args.keep_symptomatic,
                allow_lead_time=simu_args.allow_lead_time,
                **self.kwargs)
        elif self.action == EventType.QUARANTINE:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.QUARANTINE.name}\t{self.target.id}\ttill={self.kwargs["till"]:.2f}\n'
            )
            return population[self.target.id].quarantine(**self.kwargs)
        elif self.action == EventType.REINTEGRATION:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.REINTEGRATION.name}\t{self.target.id}\t.\n'
            )
            return population[self.target.id].reintegrate(**self.kwargs)
        elif self.action == EventType.INFECTION_AVOIDED:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={self.kwargs["by"].id}\n'
            )
            return []
        elif self.action == EventType.SHOW_SYMPTOM:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.SHOW_SYMPTOM.name}\t{self.target.id}\t.\n'
            )
            return []
        elif self.action == EventType.REMOVAL:
            population.pop(self.target.id)
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.REMOVAL.name}\t{self.target.id}\tpopsize={len(population)}\n'
            )
            return []
        else:
            raise RuntimeError(f'Unrecognized action {self.action}')

    def __str__(self):
        return f'{self.action.name}_{self.target.id if self.target else ""}_at_{self.time:.2f}'


class Simulator(object):

    def __init__(self, params, logger, simu_args):
        self.logger = logger
        self.simu_args = simu_args
        self.params = params
        self.model = None

    def simulate(self, id):
        #
        # get proportion of asymptomatic
        #
        self.model = Model(self.params)
        self.model.draw_prop_asym_carriers()

        # collection of individuals
        population = {
            idx: Individual(idx, model=self.model, logger=self.logger)
            for idx in range(self.simu_args.popsize)
        }

        events = defaultdict(list)
        self.logger.id = id

        # quanrantine the first person if args.pre-quarantine > 0
        if self.simu_args.pre_quarantine is not None and self.simu_args.pre_quarantine > 0:
            events[0].append(
                Event(
                    0,
                    EventType.QUARANTINE,
                    population[0],
                    logger=self.logger,
                    till=self.simu_args.pre_quarantine))
        # infect the first person
        events[0].append(
            Event(0, EventType.INFECTION, target=0, logger=self.logger))

        while True:
            # find the latest event
            time = min(events.keys())

            new_events = []
            aborted = False
            # processing events
            for evt in events[time]:
                if evt.action == EventType.ABORT:
                    self.logger.write(
                        f'{self.logger.id}\t{time:.2f}\t{EventType.ABORT.name}\t{evt.target.id}\tpopsize={len(population)}\n'
                    )
                    aborted = True
                    break
                # event triggers new event
                new_events.extend(evt.apply(population, self.simu_args))
            events.pop(time)
            #
            for evt in new_events:
                # print(f'ADDING\t{evt}')
                events[evt.time].append(evt)

            if not events or aborted:
                break
            # if self.simu_args.keep_symptomatic and all(
            #         x.infected for x in population.values()):
            #     break
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.END.name}\t{len(population)}\tpopsize={len(population)},prop_asym={self.model.params.prop_asym_carriers:.3f}\n'
        )
