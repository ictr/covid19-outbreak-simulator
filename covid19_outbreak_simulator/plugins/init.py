import random

from covid19_outbreak_simulator.event import Event, EventType
from covid19_outbreak_simulator.plugin import BasePlugin
from covid19_outbreak_simulator.utils import parse_param_with_multiplier


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
            necessarily show any symptom). Multipliers are allowed to specify incidence rate
            for each group.''')
        parser.add_argument(
            '--seroprevalence',
            nargs='*',
            help='''Seroprevalence of the population (default to zero). The seroprevalence
            should always be greater than or euqal to initial incidence rate. The difference
            between seroprevalence and incidence rate will determine the "recovered" rate of
            the population. Multipliers are allowed to specify seroprevalence for each
            group.''')
        parser.add_argument(
            '--leadtime',
            help='''With "leadtime" infections are assumed to happen before the simulation.
            This option can be a fixed positive number `t` when the infection happens
            `t` days before current time. If can also be set to 'any' for which the
            carrier can be any time during its course of infection, or `asymptomatic`
            for which the leadtime is adjust so that the carrier does not show any
            symptom at the time point (in incubation period for symptomatic case).
            All events triggered before current time are ignored.''')
        return parser

    def apply(self, time, population, args=None):
        idx = 0

        # population prevalence and incidence rate
        ir = parse_param_with_multiplier(args.incidence_rate,
                subpops=population.group_sizes.keys(), default=0.0)
        #
        isp = parse_param_with_multiplier(args.seroprevalence,
                subpops=population.group_sizes.keys(), default=0.0)

        events = []
        for name, sz in population.group_sizes.items():
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

            self.logger.write(
                f'{self.logger.id}\t{time:.2f}\t{EventType.PLUGIN.name}\t.\tname=init,n_recovered={n_recovered},n_infected={n_ir}\n'
            )
            for idx, sts in zip(range(0, sz), pop_status):
                if sts == 2:
                    population[f'{name}_{idx}' if name else str(idx)].infected = -10.0
                    population[f'{name}_{idx}' if name else str(idx)].recovered = -2.0
                if sts == 1:
                    events.append(
                        Event(
                            0.0,
                            EventType.INFECTION,
                            target=name + str(idx),
                            logger=self.logger,
                            priority=True,
                            by=None,
                            leadtime=args.leadtime,
                            handle_symptomatic=self.simulator.simu_args
                            .handle_symptomatic))

        return events
