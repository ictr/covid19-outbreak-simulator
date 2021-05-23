import copy
import math
import numpy as np
from numpy.random import choice, rand
from fnmatch import fnmatch
from .utils import as_float
from .event import Event, EventType
import re


class Individual(object):

    def __init__(self, id, susceptibility, model, logger):
        self.id = id
        self.model = model
        self.susceptibility = 1.0 if susceptibility is None else min(
            1, susceptibility)
        self.logger = logger

        # these will be set to event happen time
        self.infectivity = None
        self.infected = False
        self.show_symptom = False
        self.recovered = False
        self.symptomatic = None
        self.vaccinated = False
        self.quarantined = False

        self.r0 = None
        self.incubation_period = None

    @property
    def group(self):
        return self.id.rsplit("_", 1)[0] if "_" in self.id else ""

    def __str__(self):
        return self.id

    def quarantine(self, **kwargs):
        if "till" in kwargs:
            till = kwargs["till"]
        else:
            raise ValueError(
                "No till parameter is specified for quarantine event.")
        self.quarantined = till
        return [
            Event(
                till,
                EventType.REINTEGRATION,
                target=self.id,
                logger=self.logger)
        ]

    def vaccinate(self, time, immunity, infectivity, **kwargs):
        self.vaccinated = time
        self.susceptibility = 1 - immunity
        self.infectivity = infectivity

    def reintegrate(self):
        self.quarantined = False
        return []

    def symptomatic_infect(self, time, **kwargs):
        self.symptomatic = True
        self.r0 = self.model.draw_random_r0(symptomatic=True, group=self.group)

        if self.infectivity is not None:
            self.r0 *= self.infectivity
            if self.r0 < 1:
                return self.asymptomatic_infect(time, r0=self.r0, **kwargs)

        self.r0_multiplier = getattr(self.model.params,
                                     f"symptomatic_r0_multiplier_{self.group}",
                                     1.0)
        #
        self.incubation_period = self.model.draw_random_incubation_period(
            group=self.group)
        self.infect_params = self.model.draw_infection_params(symptomatic=True)

        #
        # infect others
        (x_grid,
         trans_prob) = self.model.get_symptomatic_transmission_probability(
             self.incubation_period, self.r0 * self.r0_multiplier,
             self.infect_params)

        by = kwargs.get("by", None)

        if "leadtime" in kwargs and kwargs["leadtime"] is not None:
            if by is not None:
                raise ValueError(
                    "leadtime is only allowed during initialization of infection event (no by option.)"
                )
            if kwargs["leadtime"] == "any":
                lead_time = np.random.uniform(0, x_grid[-1])
            elif kwargs["leadtime"] == "asymptomatic":
                lead_time = np.random.uniform(0, self.incubation_period)
            else:
                lead_time = as_float(
                    kwargs["leadtime"],
                    "--leadtime can only be any, asymptomatic, or a fixed number",
                )
        else:
            lead_time = 0

        self.infected = float(time - lead_time)

        if "handle_symptomatic" not in kwargs or kwargs[
                "handle_symptomatic"] is None:
            handle_symptomatic = ["remove", 1]
        else:
            handle_symptomatic = kwargs["handle_symptomatic"]
        # show symptom
        kept = True
        evts = []
        symp_time = time + self.incubation_period - lead_time
        if symp_time < 0:
            self.show_symptom = symp_time
        else:
            # show symptom after current time ...
            evts.append(
                Event(
                    symp_time,
                    EventType.SHOW_SYMPTOM,
                    target=self.id,
                    logger=self.logger,
                ))
        #
        if self.quarantined and self.quarantined > symp_time:
            # show symptom during quarantine, ok
            pass
        elif handle_symptomatic[0] in ("remove", "keep"):
            if len(handle_symptomatic) == 1:
                proportion = 1
            else:
                proportion = as_float(
                    handle_symptomatic[1],
                    "Proportion in --handle-symptomatic remove/keep prop should be a float number",
                )
            if proportion > 1 or proportion < 0:
                raise ValueError(
                    f'Proportion in "--handle-symptomatic remove/keep prop" should be a float number between 0 and 1: {proportion} provided'
                )
            if (handle_symptomatic[0] == "keep" and
                    np.random.uniform(0, 1, 1)[0] > proportion) or (
                        handle_symptomatic[0] == "remove" and
                        (proportion == 1 or
                         np.random.uniform(0, 1, 1)[0] <= proportion)):
                kept = False
                if symp_time >= 0:
                    evts.append(
                        # scheduling REMOVAL
                        Event(
                            symp_time,
                            EventType.REMOVAL,
                            target=self.id,
                            logger=self.logger,
                        ))
                else:
                    # just remove
                    self.logger.write(
                        f'{time:.2f}\t{EventType.WARNING.name}\t{self.id}\tmsg="Individual not removed before it show symptom before {time}"\n'
                    )
        elif handle_symptomatic[0] == "replace":
            if symp_time >= 0:
                evts.append(
                    # scheduling REMOVAL
                    Event(
                        symp_time,
                        EventType.REPLACEMENT,
                        target=self.id,
                        reason='symptom',
                        keep=['vaccinated'],
                        logger=self.logger,
                    ))
            else:
                # just ignore
                self.logger.write(
                    f'{time:.2f}\t{EventType.WARNING.name}\t{self.id}\tmsg="Individual not replaced before it show symptom before {time}"\n'
                )
        elif handle_symptomatic[0].startswith("quarantine"):
            if handle_symptomatic[0] == "quarantine":
                quarantine_duration = 14
            else:
                quarantine_duration = as_float(
                    handle_symptomatic[0].split("_", 1)[1],
                    "quanrantine duration should be specified as quarantine_DURATION",
                )
            if len(handle_symptomatic) == 1:
                proportion = 1
            else:
                proportion = as_float(
                    handle_symptomatic[1],
                    "Proportion in --handle-symptomatic quarantine_DURATION prop should be a float number",
                )
            if proportion > 1 or proportion < 0:
                raise ValueError(
                    f'Proportion in "--handle-symptomatic quarantine_DUURATION prop" should be a float number between 0 and 1: {proportion} provided'
                )
            if proportion == 1 or np.random.uniform(0, 1, 1)[0] <= proportion:
                kept = False
                if symp_time >= 0:
                    evts.append(
                        # scheduling QUARANTINE
                        Event(
                            symp_time,
                            EventType.QUARANTINE,
                            target=self.id,
                            logger=self.logger,
                            till=symp_time + quarantine_duration,
                        ))
                else:
                    self.quarantined = symp_time + quarantine_duration
        else:
            raise ValueError(
                f'Unrecognizable symptomatic case handling method: {" ".join(handle_symptomatic)}'
            )

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
                            target=self.id,
                            logger=self.logger,
                            by=self.id,
                        ))
                    infected[idx] = 0
        #
        for x, infe in zip(x_before, infected):
            if infe:
                evts.append(
                    Event(
                        time + x,
                        EventType.INFECTION,
                        target=None,
                        logger=self.logger,
                        by=self.id,
                        handle_symptomatic=kwargs.get("handle_symptomatic",
                                                      None),
                    ))

        evts.append(
            Event(
                time + x_grid[-1] - lead_time,
                EventType.RECOVER,
                target=self.id,
                logger=self.logger,
            ))
        if by:
            params = [f"by={by}"]
        elif lead_time:
            params = [f"leadtime={lead_time:.2f}"]
        else:
            params = []
        #
        params.extend([
            f"r0={self.r0:.2f}",
            f"r0_multiplier={self.r0_multiplier:.2f}",
            f"r={sum(infected)}",
            f"r_presym={len(presymptomatic_infected)}",
            f"r_sym={len(symptomatic_infected)}",
            f"incu={self.incubation_period:.2f}",
        ])
        self.logger.write(
            f'{time:.2f}\t{EventType.INFECTION.name}\t{self.id}\t{",".join(params)}\n'
        )
        return evts

    def asymptomatic_infect(self, time, **kwargs):
        self.symptomatic = False
        if 'r0' in kwargs:
            self.r0 = kwargs.pop('r0')
        else:
            self.r0 = self.model.draw_random_r0(symptomatic=False)
            if self.infectivity is not None:
                self.r0 *= self.infectivity

        self.r0_multiplier = getattr(
            self.model.params, f"asymptomatic_r0_multiplier_{self.group}", 1.0)

        self.incubation_period = -1

        by = kwargs.get("by")
        self.infect_params = self.model.draw_infection_params(symptomatic=False)

        (x_grid,
         trans_prob) = self.model.get_asymptomatic_transmission_probability(
             self.r0 * self.r0_multiplier, self.infect_params)

        if "leadtime" in kwargs and kwargs["leadtime"] is not None:
            if by is not None:
                raise ValueError(
                    "leadtime is only allowed during initialization of infection event (no by option.)"
                )

            if kwargs["leadtime"] in ("any", "asymptomatic"):
                # this is the first infection, the guy should be asymptomatic, but
                # could be anywhere in his incubation period
                lead_time = np.random.uniform(0, x_grid[-1])
            else:
                lead_time = min(
                    as_float(
                        kwargs["leadtime"],
                        "--leadtime can only be any, asymptomatic, or a fixed number",
                    ),
                    x_grid[-1],
                )
        else:
            lead_time = 0

        self.infected = float(time - lead_time)

        # REMOVAL ...
        evts = []
        #
        if lead_time > 0:
            idx = int(lead_time / self.model.params.simulation_interval)
            if idx >= len(trans_prob):
                idx -= 1
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
                            target=self.id,
                            logger=self.logger,
                            by=self.id,
                        ))
                    infected[idx] = 0
        #
        for x, infe in zip(x_grid, infected):
            if infe:
                evts.append(
                    Event(
                        time + x,
                        EventType.INFECTION,
                        target=None,
                        logger=self.logger,
                        by=self.id,
                        handle_symptomatic=kwargs.get("handle_symptomatic",
                                                      None),
                    ))
        evts.append(
            Event(
                time + x_grid[-1],
                EventType.RECOVER,
                target=self.id,
                logger=self.logger))

        params = [f"by={'.' if by is None else by}"]
        if lead_time > 0:
            params = [f"leadtime={lead_time:.2f}"]
        else:
            params = []
        #
        params.extend([
            f"r0={self.r0:.2f}",
            f"r0_multiplier={self.r0_multiplier:.2f}",
            f"r={asymptomatic_infected}",
            f"r_asym={asymptomatic_infected}",
        ])
        self.logger.write(
            f'{time:.2f}\t{EventType.INFECTION.name}\t{self.id}\t{",".join(params)}\n'
        )
        return evts

    def transmissibility(self, time):

        if self.symptomatic is None:
            return 0

        # return transmissibility at specified time
        interval = time - self.infected
        if self.symptomatic:
            (x_grid,
             trans_prob) = self.model.get_symptomatic_transmission_probability(
                 self.incubation_period, self.r0 * self.r0_multiplier,
                 self.infect_params)
        else:
            (x_grid,
             trans_prob) = self.model.get_asymptomatic_transmission_probability(
                 self.r0 * self.r0_multiplier, self.infect_params)
        idx = int(interval / self.model.params.simulation_interval)
        return 0 if idx >= len(x_grid) else trans_prob[idx]

    def communicable_period(self):
        if self.symptomatic is None:
            raise ValueError('Individual has not been infected yet.')

        if self.symptomatic:
            (x_grid,
             trans_prob) = self.model.get_symptomatic_transmission_probability(
                 self.incubation_period, self.r0 * self.r0_multiplier,
                 self.infect_params)
        else:
            (x_grid,
             trans_prob) = self.model.get_asymptomatic_transmission_probability(
                 self.r0 * self.r0_multiplier, self.infect_params)
        prob = np.array(trans_prob)
        return len(np.trim_zeros(prob,
                                 'fb')) * self.model.params.simulation_interval

    def total_duration(self):
        if self.symptomatic is None:
            raise ValueError('Individual has not been infected yet.')

        if self.symptomatic:
            (x_grid,
             trans_prob) = self.model.get_symptomatic_transmission_probability(
                 self.incubation_period, self.r0 * self.r0_multiplier,
                 self.infect_params)
        else:
            (x_grid,
             trans_prob) = self.model.get_asymptomatic_transmission_probability(
                 self.r0 * self.r0_multiplier, self.infect_params)
        prob = np.array(trans_prob)
        return len(np.trim_zeros(prob,
                                 'b')) * self.model.params.simulation_interval

    def viral_load(self, time):
        # NOTE THAT viral load is proportional to R0,
        # but not to R0 multiplier #16
        if self.symptomatic is None:
            return 0

        # return transmissibility at specified time
        interval = time - self.infected
        if self.symptomatic:
            (x_grid,
             trans_prob) = self.model.get_symptomatic_transmission_probability(
                 self.incubation_period, self.r0, self.infect_params)
        else:
            (x_grid,
             trans_prob) = self.model.get_asymptomatic_transmission_probability(
                 self.r0, self.infect_params)
        peak_idx = np.argmax(trans_prob)
        idx = int(interval / self.model.params.simulation_interval)
        multiplier = 0.7 if self.symptomatic else 1.8
        # translate to log10 CP/ML.
        # prob / iterval ==> daily probability from 0.1 up to 0.8
        # 0.01 to 3
        # * 10 to up to 8 (10**8)
        if idx < peak_idx:
            return (multiplier * trans_prob[idx] /
                    self.model.params.simulation_interval) * 20
        idx = peak_idx + (idx - peak_idx) // 2
        if idx >= len(x_grid):
            return 0
        else:
            return (multiplier * trans_prob[idx] /
                    self.model.params.simulation_interval) * 20

    def test_sensitivity(self, time, lod):
        # return transmissibility at specified time
        viral_load = self.viral_load(time)
        if viral_load == 0.0:
            # if it is 0, it will already be 0
            return 0
        elif viral_load >= lod:
            return 1
        else:
            return viral_load / lod

    def infect(self, time, **kwargs):
        if isinstance(self.infected, float):
            by_id = "." if kwargs["by"] is None else kwargs["by"]
            self.logger.write(
                f"{time:.2f}\t{EventType.INFECTION_IGNORED.name}\t{self.id}\tby={by_id}\n"
            )
            return []

        if self.susceptibility < 1 and rand() > self.susceptibility:
            by_id = "." if kwargs["by"] is None else kwargs["by"]
            self.logger.write(
                f"{time:.2f}\t{EventType.INFECTION_FAILED.name}\t{self.id}\tby={by_id},reason=susceptibility\n"
            )
            return []

        if self.model.draw_is_asymptomatic():
            return self.asymptomatic_infect(time, **kwargs)
        else:
            return self.symptomatic_infect(time, **kwargs)


class Population(object):

    def __init__(self, popsize, model, vicinity, logger):
        self.individuals = {}
        self.group_sizes = {
            (ps.split("=", 1)[0] if "=" in ps else ""): 0 for ps in popsize
        }
        self.max_ids = {x: y for x, y in self.group_sizes.items()}
        self.subpop_from_id = re.compile("^(.*?)[\d]+$")
        self.vicinity = self.parse_vicinity(vicinity)

        idx = 0

        for ps in popsize:
            if "=" in ps:
                # this is named population size
                name, sz = ps.split("=", 1)
            else:
                name = ""
                sz = ps
            try:
                sz = int(sz)
            except Exception:
                raise ValueError(
                    f"Named population size should be name=int: {ps} provided")

            self.add(
                [
                    Individual(
                        f"{name}_{idx}" if name else str(idx),
                        susceptibility=getattr(model.params,
                                               f"susceptibility_mean", 1) *
                        getattr(model.params,
                                f"susceptibility_multiplier_{name}", 1),
                        model=model,
                        logger=logger,
                    ) for idx in range(idx, idx + sz)
                ],
                subpop=name,
            )

    def move(self, ID, subpop):
        if subpop not in self.group_sizes:
            raise ValueError(f'Invalid subpopulation name {subpop}')
        if ID not in self.individuals:
            return
        from_sp = self.individuals[ID].group
        self.group_sizes[from_sp] -= 1
        self.group_sizes[subpop] += 1
        new_id = f'{subpop}_{self.max_ids[subpop]}'
        self.individuals[ID].id = new_id
        self.max_ids[subpop] += 1
        return new_id

    def parse_vicinity(self, params):
        if not params:
            return {}

        res = {}
        for param in params:
            matched = re.match("^(.*)-(.*)=(\d+)$", param)
            if matched:
                infector_sp = matched.group(1)
                infectee_sp = matched.group(2)
                neighbor_size = int(matched.group(3))
            else:
                matched = re.match("^(.*)=(\d+)$", param)
                if matched:
                    infector_sp = ""
                    infectee_sp = matched.group(1)
                    neighbor_size = int(matched.group(2))
                if not matched:
                    raise ValueError(
                        f'Vicinity should be specified as "INFECTOR_SO-INFECTEE_SP=SIZE": {param} specified'
                    )

            if infector_sp == "":
                infector_sps = [""]
            elif infector_sp.startswith("!"):
                infector_sps = [
                    x for x in self.group_sizes.keys()
                    if not fnmatch(x, infector_sp[1:])
                ]
            else:
                infector_sps = [
                    x for x in self.group_sizes.keys()
                    if fnmatch(x, infector_sp)
                ]

            if infectee_sp.startswith("!"):
                infectee_sps = [
                    x for x in self.group_sizes.keys()
                    if not fnmatch(x, infectee_sp[1:])
                ]
            else:
                infectee_sps = [
                    x for x in self.group_sizes.keys()
                    if fnmatch(x, infectee_sp)
                ]

            if infector_sp != "" and not infector_sps:
                raise ValueError(f"Unrecognized group {infector_sp}")
            if not infectee_sps:
                raise ValueError(f"Unrecognized group {infectee_sp}")

            for infector_sp in infector_sps:
                for infectee_sp in infectee_sps:
                    if infector_sp in res:
                        res[infector_sp][infectee_sp] = neighbor_size
                    else:
                        res[infector_sp] = {infectee_sp: neighbor_size}
        return res

    def add(self, items, subpop):
        sz = len(self.individuals)
        self.individuals.update({x.id: x for x in items})
        if sz + len(items) != len(self.individuals):
            raise ValueError(f"One or more IDs are already in the population.")
        self.group_sizes[subpop] += len(items)
        self.max_ids[subpop] += len(items)

    def replace(self, id, keep=[], **kwargs):
        old_id = id
        ind = self.individuals[id]
        grp = ind.group
        idx = self.max_ids[grp]

        self.max_ids[grp] += 1

        ind.id = f'{grp}_{idx}' if grp else str(idx)

        # we keep the susceptibility parameter...
        for attr, def_value in [
            ('infected', False),
            ('infectivity', None),
            ('show_symptom', False),
            ('recovered', False),
            ('symptomatic', None),
            ('vaccinated', False),
            ('quarantined', False),
            ('r0', None),
            ('incubation_period', None)
        ]:
            if attr not in keep:
                setattr(self, attr, def_value)

        self.individuals[ind.id] = self.individuals.pop(old_id)

    @property
    def ids(self):
        return self.individuals.keys()

    def remove(self, item):
        self.group_sizes[self.individuals[item].group] -= 1
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

    def select(self, infector=None):
        # select one non-quarantined indivudal to infect
        #
        if infector is not None and infector not in self.individuals:
            raise RuntimeError(
                f"Can not select infectee if since infector {infector} no longer exists."
            )

        # if not cicinity is defines, or
        # if infection is from community and '' not in vicinity, or
        # with infector but self.vicinity does not have this case.
        if (not self.vicinity or
            (infector is None and "" not in self.vicinity) or
            (infector is not None and
             self.individuals[infector].group not in self.vicinity)):
            ids = [
                id for id, ind in self.individuals.items()
                if infector != ind.id and not ind.quarantined
            ]
        else:
            # quota from each group.
            groups = list(self.group_sizes.keys())

            if infector in self.individuals:
                freq = copy.deepcopy(
                    self.vicinity[self.individuals[infector].group])
            else:
                freq = copy.deepcopy(self.vicinity[""])

            for grp in self.group_sizes.keys():
                if grp not in freq:
                    freq[grp] = self.group_sizes[grp]
                    # now, we know the number of qualified invidiauls from each
                    # group, but we still have excluded and quarantined....
            total = sum(freq.values())
            freq = {x: y / total for x, y in freq.items()}
            # first determine which group ...
            grp = choice(groups, 1, p=[freq[x] for x in groups])

            # then select a random individual from the group.
            ids = [
                id for id, ind in self.individuals.items() if
                ind.group == grp and infector != ind.id and not ind.quarantined
            ]

        if not ids:
            return None
        return choice(ids)
