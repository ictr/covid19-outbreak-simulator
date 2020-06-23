import random
import numpy as np
from numpy.random import choice

from .event import Event, EventType


class Individual(object):

    def __init__(self, id, group, susceptibility, infected, recovered, model,
                 logger):
        self.id = id
        self.model = model
        self.group = group
        self.susceptibility = susceptibility
        self.logger = logger

        self.infected = infected
        self.recovered = recovered
        self.quarantined = None
        self.n_infectee = 0

        self.r0 = None
        self.incubation_period = None

    def __str__(self):
        return self.id

    def quarantine(self, **kwargs):
        if 'till' in kwargs:
            till = kwargs['till']
        else:
            raise ValueError(
                'No till parameter is specified for quarantine event.')
        self.quarantined = till
        return [Event(till, EventType.REINTEGRATION, self, logger=self.logger)]

    def reintegrate(self):
        self.quarantined = None
        return []

    def symptomatic_infect(self, time, **kwargs):
        self.r0 = self.model.draw_random_r0(symptomatic=True, group=self.group)
        self.incubation_period = self.model.draw_random_incubation_period(
            group=self.group)

        by = kwargs.get('by', None)

        if by is None and 'allow_lead_time' in kwargs and kwargs[
                'allow_lead_time']:
            # this is the first infection, the guy should be asymptomatic, but
            # could be anywhere in his incubation period
            lead_time = np.random.uniform(0, self.incubation_period)
        else:
            lead_time = 0
        self.infected = float(time - lead_time)

        handle_symptomatic = kwargs.get('handle_symptomatic', ['remove', 1])

        # REMOVAL ...
        evts = [
            Event(
                time + self.incubation_period - lead_time,
                EventType.SHOW_SYMPTOM,
                self,
                logger=self.logger)
        ]
        kept = True
        if self.quarantined and time + self.incubation_period - lead_time < self.quarantined:
            # scheduling ABORT
            evts.append(
                Event(
                    time + self.incubation_period - lead_time,
                    EventType.ABORT,
                    self,
                    logger=self.logger))
        elif handle_symptomatic[0] in ('remove', 'keep'):
            if len(handle_symptomatic) == 1:
                proportion = 1
            else:
                try:
                    proportion = float(handle_symptomatic[1])
                except Exception:
                    raise ValueError(
                        f'Proportion in "--handle-symptomatic remove/keep prop" should be a float number: {handle_symptomatic[1]} provided'
                    )
            if proportion > 1 or proportion < 0:
                raise ValueError(
                    f'Proportion in "--handle-symptomatic remove/keep prop" should be a float number between 0 and 1: {proportion} provided'
                )
            if (handle_symptomatic[0] == 'keep' and
                    np.random.uniform(0, 1, 1)[0] > proportion) or (
                        handle_symptomatic[0] == 'remove' and
                        (proportion == 1 or
                         np.random.uniform(0, 1, 1)[0] <= proportion)):
                kept = False
                evts.append(
                    # scheduling REMOVAL
                    Event(
                        time + self.incubation_period - lead_time,
                        EventType.REMOVAL,
                        self,
                        logger=self.logger))
        elif handle_symptomatic[0].startswith('quarantine'):
            if handle_symptomatic[0] == 'quarantine':
                quarantine_duration = 14
            else:
                try:
                    quarantine_duration = float(handle_symptomatic[0].split(
                        '_', 1)[1])
                except Exception:
                    raise ValueError(
                        f'quanrantine duration should be specified as "quarantine_DURATION": {handle_symptomatic[0]} provided'
                    )
            if len(handle_symptomatic) == 1:
                proportion = 1
            else:
                try:
                    proportion = float(handle_symptomatic[1])
                except Exception:
                    raise ValueError(
                        f'Proportion in "--handle-symptomatic quarantine_DURATION prop" should be a float number: {handle_symptomatic[1]} provided'
                    )
            if proportion > 1 or proportion < 0:
                raise ValueError(
                    f'Proportion in "--handle-symptomatic quarantine_DUURATION prop" should be a float number between 0 and 1: {proportion} provided'
                )
            if proportion == 1 or np.random.uniform(0, 1, 1)[0] <= proportion:
                kept = False
                evts.append(
                    # scheduling QUARANTINE
                    Event(
                        time + self.incubation_period - lead_time,
                        EventType.QUARANTINE,
                        self,
                        logger=self.logger,
                        till=time + self.incubation_period - lead_time +
                        quarantine_duration))
        else:
            raise ValueError(
                f'Unrecognizable symptomatic case handling method: {" ".join(handle_symptomatic)}'
            )
        #
        x_grid, trans_prob = self.model.get_symptomatic_transmission_probability(
            self.incubation_period, self.r0)
        # infect only before removal or quarantine
        if kept:
            x_before = x_grid
        else:
            # remove or quanratine
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

        evts.append(
            Event(
                time + x_grid[-1] - lead_time,
                EventType.RECOVER,
                self,
                logger=self.logger))
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
        self.r0 = self.model.draw_random_r0(symptomatic=False)
        self.incubation_period = -1

        by = kwargs.get('by',)

        if by is None and 'allow_lead_time' in kwargs and kwargs[
                'allow_lead_time']:
            # this is the first infection, the guy should be asymptomatic, but
            # could be anywhere in his incubation period
            lead_time = np.random.uniform(0, 10)
        else:
            lead_time = 0

        self.infected = float(time - lead_time)

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
        evts.append(
            Event(
                time + x_grid[-1], EventType.RECOVER, self, logger=self.logger))
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
        if self.infected not in (False, None) or self.recovered not in (False,
                                                                        None):
            by_id = kwargs["by"].id if "by" in kwargs else 'None'
            self.logger.write(
                f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION_IGNORED.name}\t{self.id}\tby={by_id}\n'
            )
            return []

        if self.model.draw_is_asymptomatic():
            return self.asymptomatic_infect(time, **kwargs)
        else:
            return self.symptomatic_infect(time, **kwargs)


class Population(object):

    def __init__(self):
        self.individuals = {}

    def add(self, items):
        self.individuals.update({x.id: x for x in items})

    def remove(self, item):
        self.individuals.pop(item)

    def __len__(self):
        return len(self.individuals)

    def __contains__(self, item):
        return item in self.individuals

    def __getitem__(self, id):
        return self.individuals[id]

    def items(self):
        return self.individuals.items()

    def values(self):
        return self.individuals.values()

    def select(self, exclude, susceptibility=False):
        if susceptibility:
            # select one non-quarantined indivudal to infect
            ids = [(id, ind.susceptibility)
                   for id, ind in self.individuals.items()
                   if (not exclude or id != exclude.id) and not ind.quarantined]

            if not ids:
                return None

            weights = np.array([x[1] for x in ids])
            weights = weights / sum(weights)
            return ids[choice(len(ids), 1, p=weights)[0]][0]
        else:
            # select one non-quarantined indivudal to infect
            ids = [
                id for id, ind in self.individuals.items()
                if (not exclude or id != exclude.id) and not ind.quarantined
            ]
            if not ids:
                return None
            return random.choice(ids)
