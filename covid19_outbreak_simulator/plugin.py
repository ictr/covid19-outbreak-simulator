import argparse

from covid19_outbreak_simulator.event import EventType


class PlugInEvent(object):

    def __init__(self, time, plugin, args, priority=False, trigger_event=None):
        self.time = time
        self.plugin = plugin
        self.args = args
        self.priority = priority
        self.action = EventType.PLUGIN
        self.trigger_event = trigger_event

    def apply(self, population):
        return self.plugin.apply_plugin(self.time, population, self.args)

    def __str__(self):
        return f'Call {self.plugin} at {self.time}'


class BasePlugin(object):

    # this option can be
    #
    #  after_core_events:
    #       applied after core events at specified time
    #
    #  before_core_events:
    #       applied before core events at specified time
    #
    apply_at = 'after_core_events'

    def __init__(self, simulator, *args, **kwargs):
        self.simulator = simulator
        self.logger = self.simulator.logger if self.simulator else None
        self.last_applied = None
        self.applied_at = set()

    def __str__(self):
        return self.__class__.__name__

    def get_parser(self):
        parser = argparse.ArgumentParser(
            '--plugin', description='A plugin for covid19-outbreak-simulator')
        parser.add_argument('--disable',
            action='store_true',
            help='Disable the plugin if this parameter is specified.'
        )
        parser.add_argument(
            '--start',
            type=float,
            help='''Start time. Default to 0 no parameter is defined so the
                plugin will be called once at the beginning.''')
        parser.add_argument(
            '--end',
            type=float,
            help='''End time, default to none, meaning there is no end time.''')
        parser.add_argument(
            '--at',
            nargs='*',
            type=float,
            help='''Specific time at which the plugin is applied.''')
        parser.add_argument(
            '--interval',
            type=float,
            help='''Interval at which plugin is applied, it will assume
             a 0 starting time if --start is left unspecified.''')
        parser.add_argument(
            '--trigger-by',
            nargs='*',
            help='''Events that triggers this plug in.''')
        parser.add_argument(
            '-v', '--verbosity',
            default=1,
            type=int,
            choices=[0, 1, 2],
            help='''Set verbosity level of the plugin, default to 1 (general), can be
                set to 0 (warning and error) only, and 2 (more output)'''
        )
        return parser

    def get_plugin_events(self, args):
        events = []

        if args.disable:
            raise RuntimeError(f'Disabled plugin should not be triggered')

        if args.interval is not None and args.interval <= 0:
            return events

        if args.start is not None:
            events.append(
                PlugInEvent(
                    time=args.start,
                    plugin=self,
                    args=args,
                    priority=self.apply_at == 'before_core_events'))

        if args.interval is not None and args.start is None:
            events.append(
                PlugInEvent(
                    time=0,
                    plugin=self,
                    args=args,
                    priority=self.apply_at == 'before_core_events'))

        if args.at is not None:
            for t in args.at:
                events.append(
                    PlugInEvent(
                        time=t,
                        plugin=self,
                        args=args,
                        priority=self.apply_at == 'before_core_events'))

        if not events and not args.trigger_by:
            events.append(
                PlugInEvent(
                    time=0,
                    plugin=self,
                    args=args,
                    priority=self.apply_at == 'before_core_events'))
        return events

    def get_trigger_events(self, args):
        if args.trigger_by:
            return [
                PlugInEvent(
                    time=0,
                    plugin=self,
                    args=args,
                    priority=self.apply_at == 'before_core_events',
                    trigger_event=EventType[x]) for x in args.trigger_by
            ]
        return []

    def apply(self, time, population, args=None):
        # redefined by subclassed
        raise ValueError('This function should be redefined.')

    def apply_plugin(self, time, population, args=None):

        events = self.apply(time, population, args)

        # schedule the next call
        if args.interval is not None and (args.end is None or
                                          time + args.interval <= args.end):
            events.append(
                PlugInEvent(time=time + args.interval, plugin=self, args=args))
        return events
