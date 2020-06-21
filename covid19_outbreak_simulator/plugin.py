import argparse


class BasePlugin(object):

    def __init__(self, simulator, population, *args, **kwargs):
        self.simulator = simulator
        self.population = population
        self.logger = self.simulator.logger if self.simulator else None
        self.last_applied = None
        self.applied_at = set()

    def get_parser(self):
        parser = argparse.ArgumentParser(
            '--plugin', description='A plugin for covid19-outbreak-simulator')
        parser.add_argument(
            '--start',
            type=float,
            default=0,
            help='''Start time, default to 0''')
        parser.add_argument(
            '--end', type=float, help='''End time, default to none''')
        parser.add_argument(
            '--at',
            nargs='+',
            type=float,
            help='''Specific time at which the plugin is applied''')
        parser.add_argument(
            '--interval',
            type=float,
            help='''Interval at which plugin is applied''')
        return parser

    def can_apply(self, time, args):
        if time in self.applied_at:
            return False

        if args.end is not None and time > args.end:
            return False

        if args.start is not None:
            if self.last_applied is None and time >= args.start:
                self.applied_at.add(time)
                self.last_applied = time
                return True
            else:
                return False

        if args.interval is not None:
            if time - self.last_applied >= args.interval:
                self.applied_at.add(time)
                self.last_applied = time
                return True

        if args.at is not None and time in args.at:
            self.applied_at.add(time)
            self.last_applied = time
            return True

        return False

    def apply(self, time, args=None):
        if not self.can_apply(time, args):
            return []