from enum import Enum

import random
import numpy as np
from numpy.random import choice
from collections import defaultdict
from itertools import groupby

from .model import Model
from importlib import import_module


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

        if by is None and 'allow_lead_time' in kwargs:
            # this is the first infection, the guy should be asymptomatic, but
            # could be anywhere in his incubation period
            lead_time = np.random.uniform(0, self.incubation_period)
        else:
            lead_time = 0
        self.infected = time - lead_time

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
                    f'Proportion in "--handle-symptomatic remove/keep prop" should be a float number between 0 and 1: {removal_proportion} provided'
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
                except Exception as e:
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
                        till=time + self.incubation_period - lead_time + 14))
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

        if by is None and 'allow_lead_time' in kwargs:
            # this is the first infection, the guy should be asymptomatic, but
            # could be anywhere in his incubation period
            lead_time = np.random.uniform(0, 10)
        else:
            lead_time = 0

        self.infected = time - lead_time

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


class EventType(Enum):
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
                selected = self.target
            elif simu_args.susceptibility:
                # select one non-quarantined indivudal to infect
                ids = [(id, ind.susceptibility)
                       for id, ind in population.items()
                       if (not self.target or id != self.target.id) and
                       not ind.quarantined]

                if not ids:
                    self.logger.write(
                        f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_FAILED.name}\t{self.target}\tby={self.kwargs["by"]}\n'
                    )
                    return []
                weights = np.array([x[1] for x in ids])
                weights = weights / sum(weights)
                selected = ids[choice(len(ids), 1, p=weights)[0]][0]
            else:
                # select one non-quarantined indivudal to infect
                ids = [
                    id for id, ind in population.items()
                    if (not self.target or id != self.target.id) and
                    not ind.quarantined
                ]
                if not ids:
                    self.logger.write(
                        f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_FAILED.name}\t{self.target}\tby={self.kwargs["by"]}\n'
                    )
                    return []
                selected = random.choice(ids)
            return population[selected].infect(
                self.time,
                handle_symptomatic=simu_args.handle_symptomatic,
                allow_lead_time=simu_args.allow_lead_time,
                **self.kwargs)
        elif self.action == EventType.QUARANTINE:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.QUARANTINE.name}\t{self.target}\ttill={self.kwargs["till"]:.2f}\n'
            )
            return population[self.target.id].quarantine(**self.kwargs)
        elif self.action == EventType.REINTEGRATION:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.REINTEGRATION.name}\t{self.target}\t.\n'
            )
            return population[self.target.id].reintegrate(**self.kwargs)
        elif self.action == EventType.INFECTION_AVOIDED:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={self.kwargs["by"]}\n'
            )
            return []
        elif self.action == EventType.SHOW_SYMPTOM:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.SHOW_SYMPTOM.name}\t{self.target}\t.\n'
            )
            return []
        elif self.action == EventType.REMOVAL:
            if self.target.id in population:
                population.pop(self.target.id)
                self.logger.write(
                    f'{self.logger.id}\t{self.time:.2f}\t{EventType.REMOVAL.name}\t{self.target}\tpopsize={len(population)}\n'
                )
            else:
                self.logger.write(
                    f'{self.logger.id}\t{self.time:.2f}\t{EventType.REMOVAL.name}\t{self.target}\tpopsize={len(population)},already_removed=True\n'
                )
            return []
        elif self.action == EventType.RECOVER:
            removed = self.target.id not in population

            if not removed:
                population[self.target.id].recovered = self.time

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
        elif self.action == EventType.STAT:
            stat = {}
            stat[f'n_recovered'] = len([
                x for x, ind in population.items()
                if ind.recovered not in (None, False)
            ])
            stat[f'n_infected'] = len([
                x for x, ind in population.items()
                if ind.infected not in (False, None)
            ])
            stat[f'n_popsize'] = len([x for x, ind in population.items()])
            stat[f'incidence_rate'] = '0' if stat[
                f'n_popsize'] == 0 else '{:.4f}'.format(stat[f'n_infected'] /
                                                        stat[f'n_popsize'])
            stat[f'seroprevalence'] = '0' if stat[
                f'n_popsize'] == 0 else '{:.4f}'.format(
                    (stat[f'n_recovered'] + stat[f'n_infected']) /
                    stat[f'n_popsize'])

            groups = set([x.group for x in population.values()])
            for group in groups:
                if group == '':
                    continue
                stat[f'n_{group}_recovered'] = len([
                    x for x, ind in population.items()
                    if ind.recovered is True and ind.group == group
                ])
                stat[f'n_{group}_infected'] = len([
                    x for x, ind in population.items()
                    if ind.infected not in (False, None) and ind.group == group
                ])
                stat[f'n_{group}_popsize'] = len(
                    [x for x, ind in population.items() if ind.group == group])
                stat[f'{group}_incidence_rate'] = 0 if stat[
                    f'n_{group}_popsize'] == '0' else '{:.3f}'.format(
                        stat[f'n_{group}_infected'] /
                        stat[f'n_{group}_popsize'])
                stat[f'{group}_seroprevalence'] = 0 if stat[
                    f'n_{group}_popsize'] == '0' else '{:.3f}'.format(
                        (stat[f'n_{group}_recovered'] +
                         stat[f'n_{group}_infected']) /
                        stat[f'n_{group}_popsize'])
            param = ','.join(f'{k}={v}' for k, v in stat.items())
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.STAT.name}\t.\t{param}\n'
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
        self.plugins = {}

    def load_plugins(self, population):
        if not self.simu_args.plugin:
            return
        # split by '--plugin'
        groups = [
            list(group) for k, group in groupby(
                self.simu_args.plugin, lambda x: x == '--plugin') if not k
        ]

        for group in groups:
            plugin = group[0]
            if '.' not in plugin:
                module_name, plugin_name = plugin, plugin
            else:
                module_name, plugin_name = plugin.rsplit('.', 1)
            try:
                mod = import_module(module_name)
            except Exception as e:
                try:
                    mod = import_module(
                        f'covid19_outbreak_simulator.plugins.{module_name}')
                except Exception as e:
                    raise ValueError(
                        f'Failed to import module {module_name}: {e}')
            try:
                obj = getattr(mod, plugin_name)(
                    simulator=self, population=population)
            except Exception as e:
                raise ValueError(
                    f'Failed to retrieve plugin {plugin_name} from module {module_name}'
                )
            # if there is a parser
            if hasattr(obj, 'get_parser'):
                parser = obj.get_parser()
                args = parser.parse_args(group[1:])
            else:
                args = None
            #
            if not hasattr(obj, 'apply'):
                raise ValueError('No "apply" function is defined for plugin')
            self.plugins[obj] = args

    def call_plugins(self, time, population):
        events = []
        for plugin, args in self.plugins.items():
            events.extend(plugin.apply(time=time, args=args))
        return events

    def simulate(self, id):
        #
        # get proportion of asymptomatic
        #
        self.model = Model(self.params)
        self.model.draw_prop_asym_carriers()

        # collection of individuals
        population = {}
        idx = 0

        self.load_plugins(population=population)

        # population prevalence and incidence rate
        ir = {'': 0.0}
        if self.simu_args.initial_incidence_rate:
            # the first number must be float
            try:
                ir[''] = float(self.simu_args.initial_incidence_rate[0])
            except Exception as e:
                raise ValueError(
                    f'The first parameter of --initial-incidence-rate should be a float number "{self.simu_args.initial_incidence_rate[0]}" provided: {e}'
                )
            for multiplier in self.simu_args.initial_incidence_rate[1:]:
                if '=' not in multiplier:
                    raise ValueError(
                        f'The non-first parameter of --initial-incidence-rate should be a float number "{multiplier}" provided.'
                    )
                name, value = multiplier.split('=', 1)
                try:
                    value = float(value)
                except Exception:
                    raise ValueError(
                        f'Multiplier should have format name=float_value: {multiplier} provided'
                    )
                ir[name] = value * ir['']
        #
        isp = {'': 0.0}
        if self.simu_args.initial_seroprevalence:
            # the first number must be float
            try:
                isp[''] = float(self.simu_args.initial_seroprevalence[0])
            except Exception as e:
                raise ValueError(
                    f'The first parameter of --initial-seroprevalence should be a float number "{self.simu_args.initial_incidence_rate[0]}" provided: {e}'
                )
            for multiplier in self.simu_args.initial_seroprevalence[1:]:
                if '=' not in multiplier:
                    raise ValueError(
                        f'The non-first parameter of --initial-incidence-rate should be a float number "{multiplier}" provided.'
                    )
                name, value = multiplier.split('=', 1)
                try:
                    value = float(value)
                except Exception:
                    raise ValueError(
                        f'Multiplier should have format name=float_value: {multiplier} provided'
                    )
                isp[name] = value * ir['']

        for ps in self.simu_args.popsize:
            if '=' in ps:
                # this is named population size
                name, sz = ps.split('=', 1)

            else:
                name = ''
                sz = ps
            try:
                sz = int(sz)
            except Exception:
                raise ValueError(
                    f'Named population size should be name=int: {ps} provided')
            pop_ir = ir.get(name if name in ir else '', 0.0)
            n_ir = np.random.binomial(sz, pop_ir, 1)[0]

            pop_isp = isp.get(name if name in isp else '', 0.0)
            if pop_isp == 0.0:
                n_recovered = 0
            elif pop_isp < pop_ir:
                raise ValueError(
                    'Seroprevalence, if specified, should be greater than or equal to incidence rate.'
                )
            else:
                n_recovered = np.random.binomial(sz, pop_isp - pop_ir, 1)[0]
            pop_status = [1] * n_ir + [2] * n_recovered + [0] * (
                sz - n_ir - n_recovered)
            random.shuffle(pop_status)

            population.update({
                name + str(idx): Individual(
                    name + str(idx),
                    group=name,
                    susceptibility=getattr(self.model.params,
                                           f'susceptibility_multiplier_{name}',
                                           1),
                    infected=sts == 1,
                    recovered=sts == 2,
                    model=self.model,
                    logger=self.logger)
                for idx, sts in zip(range(idx, idx + sz), pop_status)
            })

        events = defaultdict(list)
        self.logger.id = id

        if self.simu_args.initial_incidence_rate:
            for id, ind in population.items():
                if ind.infected:
                    events[0].append(
                        Event(
                            0,
                            EventType.INFECTION,
                            target=id,
                            logger=self.logger))
                    ind.infected = False

        # quanrantine the first person if args.pre-quarantine > 0
        if self.simu_args.pre_quarantine:
            try:
                till = float(self.simu_args.pre_quarantine[0])
            except Exception:
                raise ValueError(
                    f'The first value of pre_quarantine should be days (a float number): {self.simu_args.pre_quarantine[0]} provided'
                )
            IDs = ['0'] if len(self.simu_args.pre_quarantine
                              ) == 1 else self.simu_args.pre_quarantine[1:]
            for ID in IDs:
                if ID not in population:
                    raise ValueError(f'Invalid ID to quanrantine {ID}')
                events[0].append(
                    Event(
                        0,
                        EventType.QUARANTINE,
                        population[ID],
                        logger=self.logger,
                        till=till))

        infectors = [
            '0'
        ] if self.simu_args.infectors is None else self.simu_args.infectors
        for infector in infectors:
            if infector not in population:
                raise ValueError(f'Invalid ID for carrier {infector}')
            # infect the first person
            events[0].append(
                Event(
                    0, EventType.INFECTION, target=infector,
                    logger=self.logger))

        last_stat = None
        while True:
            # find the latest event
            if not events:
                time = 0
                max_time = 0
            else:
                time = min(events.keys())
                max_time = max(events.keys())

            if self.simu_args.stat_interval > 0 and last_stat is None or max_time - last_stat > self.simu_args.stat_interval:
                while last_stat is None or last_stat <= max_time:
                    last_stat = 0 if last_stat is None else last_stat + self.simu_args.stat_interval
                    events[last_stat].append(
                        Event(last_stat, EventType.STAT, logger=self.logger))

            if self.simu_args.stop_if is not None:
                if self.simu_args.stop_if[0].startswith('t>'):
                    #
                    try:
                        st = float(self.simu_args.stop_if[0][2:])
                    except Exception:
                        raise ValueError(
                            f'Invalid value for option --stop-if "{self.simu_args.stop_if[0]}": {e}'
                        )
                    if time > st:
                        time = st
                        break
                else:
                    raise ValueError(
                        f'Option --stop-if currently only supports t>TIME to stop after certain time point.'
                    )
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

            #
            new_events.extend(
                self.call_plugins(time=time, population=population))
            events.pop(time)
            #
            for evt in new_events:
                # print(f'ADDING\t{evt}')
                events[evt.time].append(evt)

            if not events or aborted:
                break
            # if self.simu_args.handle_symptomatic and all(
            #         x.infected for x in population.values()):
            #     break
        res = {
            'popsize': len(population),
            'prop_asym': f'{self.model.params.prop_asym_carriers:.3f}'
        }
        if self.simu_args.stop_if:
            res['stop_if'] = ''.join(self.simu_args.stop_if)
        params = ','.join([f'{x}={y}' for x, y in res.items()])
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.END.name}\t{len(population)}\t{params}\n'
        )
