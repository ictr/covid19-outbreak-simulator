import argparse
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.simulator import Event, EventType
import numpy as np
import random


class init(BasePlugin):

    # events that will trigger this plugin
    apply_at = 'before_core_events'

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(init, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(init, self).get_parser()
        parser.prog = '--plugin init'
        parser.description = 'Initialize population with initial prevalence and seroprevalence'
        parser.add_argument(
            '--incidence-rate',
            nargs='*',
            help='''Incidence rate of the population (default to zero), which should be
            the probability that any individual is currently affected with the virus (not
            necessarily show any symptom). Multipliers can be specified to set incidence
            rate of for particular groups (e.g. --initial-incidence-rate 0.1 docter=1.2
            will set incidence rate to 0.12 for doctors).''')
        parser.add_argument(
            '--seroprevalence',
            nargs='*',
            help='''Seroprevalence of the population (default to zero). The seroprevalence
            should always be greater than or euqal to initial incidence rate. The difference
            between seroprevalence and incidence rate will determine the "recovered" rate of
            the population. Multipliers can be specified to set incidence rate of
            for particular groups (e.g. --initial-incidence-rate 0.1 docter=1.2 will set
            incidence rate to 0.12 for doctors).''')

        return parser

    def apply(self, time, population, args=None, simu_args=None):
        idx = 0

        # population prevalence and incidence rate
        ir = {'': 0.0}
        if args.incidence_rate:
            # the first number must be float
            try:
                ir[''] = float(args.incidence_rate[0])
            except Exception as e:
                raise ValueError(
                    f'The first parameter of --initial-incidence-rate should be a float number "{args.incidence_rate[0]}" provided: {e}'
                )
            for multiplier in args.incidence_rate[1:]:
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
        if args.seroprevalence:
            # the first number must be float
            try:
                isp[''] = float(args.seroprevalence[0])
            except Exception as e:
                raise ValueError(
                    f'The first parameter of --initial-seroprevalence should be a float number "{args.incidence_rate[0]}" provided: {e}'
                )
            for multiplier in args.seroprevalence[1:]:
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

        events = []
        for ps in simu_args.popsize:
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
            n_ir = int(sz * pop_ir)

            pop_isp = isp.get(name if name in isp else '', 0.0)
            if pop_isp == 0.0:
                n_recovered = 0
            elif pop_isp < pop_ir:
                raise ValueError(
                    'Seroprevalence, if specified, should be greater than or equal to incidence rate.'
                )
            else:
                n_recovered = int(sz * (pop_isp - pop_ir))
            pop_status = [1] * n_ir + [2] * n_recovered + [0] * (
                sz - n_ir - n_recovered)
            random.shuffle(pop_status)

            for idx, sts in zip(range(idx, idx + sz), pop_status):
                population[name + str(idx)].recovered = sts == 2
                if sts == 1:
                    events.append(
                        Event(
                            0.0,
                            EventType.INFECTION,
                            target=name + str(idx),
                            logger=self.logger,
                            priority=True))

        return events