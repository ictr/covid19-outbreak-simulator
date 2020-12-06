from datetime import datetime
import subprocess

from collections import defaultdict
from importlib import import_module
from itertools import groupby

from .event import Event, EventType
from .model import Model
from .population import Population


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
        if not args.disable:
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
        population = Population(popsize=self.simu_args.popsize, model=self.model,
            vicinity=self.simu_args.vicinity, logger=self.logger)

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
            f'0.00\t{EventType.START.name}\t.\t{start_params}\n'
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
                        f'{time:.2f}\t{EventType.ABORT.name}\t{evt.target}\tpopsize={len(population)}\n'
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

            if not events or aborted or (all_plugin and
                                         self.simu_args.stop_if is None):
                break
            # if self.simu_args.handle_symptomatic and all(
            #         x.infected for x in population.values()):
            #     break
        remaining_events = defaultdict(int)
        infected_by = set()
        for time, events_at_time in events.items():
            for event in events_at_time:
                if event.action.name in ('SHOW_SYMPTOM', 'RECOVER', 'REMOVAL') and event.target not in population:
                    continue
                if event.action.name in ('INFECTION'):
                    if event.kwargs['by'] in population:
                        infected_by.add(event.kwargs['by'])
                    else:
                        continue
                remaining_events[event.action.name] += 1
        if infected_by:
            remaining_events['INFECTION'] = f"{remaining_events['INFECTION']} (by {len(infected_by)} infectors)"
        remaining_events = ','.join(f'{x}:{y}' for x,y in remaining_events.items())
        res = {
            'popsize': len(population),
            'prop_asym': f'{self.model.params.prop_asym_carriers:.3f}',
            'time': datetime.now().strftime("%m/%d/%Y-%H:%M:%S"),
        }
        if remaining_events:
            res['remaining_events'] = remaining_events
        if self.simu_args.stop_if:
            res['stop_if'] = ''.join(self.simu_args.stop_if)
        params = ','.join([f'{x}={y}' for x, y in res.items()])

        self.logger.write(
            f'{time:.2f}\t{EventType.END.name}\t{len(population)}\t{params}\n'
        )
