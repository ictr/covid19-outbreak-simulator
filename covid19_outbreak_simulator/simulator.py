from datetime import datetime
import subprocess
import sys

from collections import defaultdict
from importlib import import_module
from itertools import groupby

from .event import Event, EventType
from .model import Model
from .population import Individual, Population


def load_plugins(args, simulator=None):
    groups = [
        list(group)
        for k, group in groupby(args, lambda x: x == '--plugin')
        if not k
    ]
    plugins = []
    for group in groups:
        plugin = group[0]
        if '.' not in plugin:
            module_name, plugin_name = plugin, plugin.replace('-', '_')
        else:
            module_name, plugin_name = plugin.rsplit('.', 1)
        try:
            mod = import_module(
                f'covid19_outbreak_simulator.plugins.{module_name}')
        except Exception:
            try:
                mod = import_module(module_name)
            except Exception as e:
                raise ValueError(f'Failed to import module {module_name}: {e}')
        try:
            obj = getattr(mod, plugin_name)(simulator)
        except Exception as e:
            raise ValueError(
                f'Failed to retrieve plugin {plugin_name} from module {module_name}: {e}'
            )
        # if there is a parser
        parser = obj.get_parser()
        args = parser.parse_args(group[1:])
        #
        if not hasattr(obj, 'apply'):
            raise ValueError('No "apply" function is defined for plugin')
        plugins.append([obj, args])
    return plugins


class Simulator(object):

    def __init__(self, params, logger, simu_args, cmd):
        self.logger = logger
        self.simu_args = simu_args
        self.params = params
        self.model = None
        self.cmd = cmd
        self.plugins = {}

    def get_plugin_events(self):
        if not self.simu_args.plugin:
            return [], {}

        trigger_events = []
        initial_events = []

        for plugin, args in load_plugins(self.simu_args.plugin, simulator=self):
            initial_events.extend(plugin.get_plugin_events(args))
            trigger_events.extend(plugin.get_trigger_events(args))

        trigger_events_dict = defaultdict(list)
        for te in trigger_events:
            trigger_events_dict[te.trigger_event].append(te)
        return initial_events, trigger_events_dict

    def simulate(self, id):
        #
        # get proportion of asymptomatic
        #
        self.model = Model(self.params)
        self.model.draw_prop_asym_carriers()

        # collection of individuals
        population = Population(
            popsize=self.simu_args.popsize,
            uneven_susceptibility=self.simu_args.susceptibility is not None)
        idx = 0

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

            population.add([
                Individual(
                    name + str(idx),
                    group=name,
                    susceptibility=getattr(self.model.params,
                                           f'susceptibility_multiplier_{name}',
                                           1),
                    model=self.model,
                    logger=self.logger) for idx in range(idx, idx + sz)
            ])

        events = defaultdict(list)
        self.logger.id = id

        infectors = [] if self.simu_args.infectors is None else self.simu_args.infectors
        for infector in infectors:
            if infector not in population:
                raise ValueError(f'Invalid ID for carrier {infector}')
            # infect the first person
            events[0].append(
                Event(
                    0,
                    EventType.INFECTION,
                    target=infector,
                    logger=self.logger,
                    by=None,
                    handle_symptomatic=self.simu_args.handle_symptomatic,
                    leadtime=self.simu_args.leadtime))

        # load the plugins
        init_events, trigger_events = self.get_plugin_events()
        for evt in init_events:
            events[evt.time].append(evt)

        start_params = {
            'id': self.logger.id,
            'time': datetime.now().strftime("%m/%d/%Y-%H:%M:%S"),
            'args': subprocess.list2cmdline(self.cmd)
        }
        start_params = ','.join([f'{x}={y}' for x, y in start_params.items()])

        self.logger.write(
            f'{self.logger.id}\t0.00\t{EventType.START.name}\t.\t{start_params}\n'
        )
        while True:
            # find the latest event
            time = 0.00 if not events else min(events.keys())

            if self.simu_args.stop_if is not None:
                st = float(self.simu_args.stop_if[0][2:])
                if time > st:
                    time = st
                    break

            new_events = []
            aborted = False
            # processing events
            cur_events = [x for x in events[time] if x.priority
                         ] + [x for x in events[time] if not x.priority]
            while True:
                try:
                    evt = cur_events.pop(0)
                except:
                    break
                if evt.action == EventType.ABORT:
                    self.logger.write(
                        f'{self.logger.id}\t{time:.2f}\t{EventType.ABORT.name}\t{evt.target}\tpopsize={len(population)}\n'
                    )
                    aborted = True
                    break
                res = evt.apply(population)
                if evt.action in trigger_events:
                    for x in trigger_events[evt.action]:
                        x.time = time
                        res.append(x)

                for x in res:
                    if x.time == time:
                        if x.priority:
                            cur_events.insert(0, x)
                        else:
                            cur_events.append(x)
                    else:
                        new_events.append(x)

            events.pop(time)
            # if there is no other events, and all new ones are plugin generated
            # (through --interval, it is time to stop
            all_plugin = not events
            for evt in new_events:
                # print(f'ADDING\t{evt}')
                events[evt.time].append(evt)
                if isinstance(evt, Event):
                    all_plugin = False

            if not events or aborted or all_plugin:
                break
            # if self.simu_args.handle_symptomatic and all(
            #         x.infected for x in population.values()):
            #     break
        res = {
            'popsize': len(population),
            'prop_asym': f'{self.model.params.prop_asym_carriers:.3f}',
            'time': datetime.now().strftime("%m/%d/%Y-%H:%M:%S"),
        }
        if self.simu_args.stop_if:
            res['stop_if'] = ''.join(self.simu_args.stop_if)
        params = ','.join([f'{x}={y}' for x, y in res.items()])
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.END.name}\t{len(population)}\t{params}\n'
        )
