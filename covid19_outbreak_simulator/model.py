import re

import numpy as np
from scipy.optimize import bisect
from scipy.stats import norm


class Params:

    def __init__(self, args=None):
        # args should be args returned from argparser
        self.params = set([
            'simulation_interval', 'prop_asym_carriers', 'incubation_period',
            'symptomatic_r0', 'asymptomatic_r0', 'susceptibility'
        ])
        self.groups = {}
        self.set_params(args)

    def set(self, param, prop, value):
        if param not in self.params:
            raise ValueError(f'Unrecgonzied parameter {param}')
        if prop is None or prop == 'self':
            setattr(self, param, value)
        elif prop in ('loc', 'low', 'high', 'mean', 'sigma', 'scale'):
            setattr(self, f'{param}_{prop}', value)
        elif prop.startswith('multiplier_'):
            group = prop[11:]
            if group not in self.groups:
                raise ValueError(
                    f'Group {group} does not exist. Available groups are: {", ".join(self.groups.keys())}'
                )
            if value < 0:
                raise ValueError(
                    f'Multiplier should be positive {value} specified')
            setattr(self, f'{param}_{prop}', value)
        elif re.match('quantile_(.*)', prop):
            lq = float(re.match('quantile_(.*)', prop)[1]) / 100
            loc = getattr(self, f'{param}_loc')
            sd = bisect(
                lambda x: norm.cdf(value, loc=loc, scale=x) - lq,
                a=0.00001,
                b=25)
            setattr(self, f'{param}_scale', sd)
        else:
            raise ValueError(f'Unrecognized property {prop}')

    def check_id(self, ID):
        if ID.isnumeric():
            if '' not in self.groups:
                raise ValueError(f'Invalid ID {ID}: No default group.')
            if int(ID) >= self.groups[''] or int(ID) < 0:
                raise ValueError(f'Invalid ID {ID}: Index out of range.')
        else:
            found = False
            for name, size in self.groups.items():
                if ID.startswith(name) and ID[len(name):].isnumeric():
                    idx = int(ID[len(name):])
                    if idx >= self.groups[name] or idx < 0:
                        raise ValueError(
                            f'Invalid ID {ID}: Index out of range.')
                    found = True
                    break
            if not found:
                raise ValueError(f'Invalid ID {ID}')

    def set_popsize(self, val):
        if not val:
            return
        for ps in val:
            if '=' in ps:
                name, size = ps.split('=', 1)
                if name[-1].isnumeric():
                    raise ValueError(
                        f'Group names that end with numbers are not allowed. {name}'
                    )
            else:
                name = ''
                size = ps
            try:
                size = int(size)
            except Exception:
                raise ValueError(f'Incorrect popsize {ps}')
            if name in self.groups:
                raise ValueError(f'Group "{name}" has been specified before')
            self.groups[name] = size

    def set_infectors(self, val):
        if not val:
            return
        for ID in val:
            self.check_id(ID)

    def set_symptomatic_r0(self, val):
        if not val:
            return
        # if asymptomatic_r0 is specified, it should a number of a range...
        pars = [x for x in val if '=' not in x]
        if len(pars) == 1:
            try:
                self.set('symptomatic_r0', 'low', float(pars[0]))
                self.set('symptomatic_r0', 'high', float(pars[0]))
            except Exception:
                raise ValueError(
                    f'The symptomatic_r0 should be a float number, if it is not a multiplier for groups: {pars[0]} provided'
                )
        elif len(pars) == 2:
            try:
                self.set('symptomatic_r0', 'low', float(pars[0]))
            except Exception:
                raise ValueError(
                    f'The symptomatic_r0 should be a float number, if it is not a multiplier for groups: {pars[0]} provided'
                )
            try:
                self.set('symptomatic_r0', 'high', float(pars[1]))
            except Exception:
                raise ValueError(
                    f'The symptomatic_r0 should be a float number, if it is not a multiplier for groups: {pars[1]} provided'
                )
        elif len(pars) > 2:
            raise ValueError(
                f'The symptomatic_r0 should be one or two float number.')
        #
        for multiplier in [x for x in val if '=' in x]:
            name, value = multiplier.split('=', 1)
            try:
                value = float(value)
            except Exception:
                raise ValueError(
                    f'Multiplier should have format name=float_value: {multiplier} provided'
                )
            self.set('symptomatic_r0', f'multiplier_{name}', value)

    def set_asymptomatic_r0(self, val):
        if not val:
            return
        # if asymptomatic_r0 is specified, it should a number of a range...
        pars = [x for x in val if '=' not in x]
        if len(pars) == 1:
            try:
                self.set('asymptomatic_r0', 'low', float(pars[0]))
                self.set('asymptomatic_r0', 'high', float(pars[0]))
            except Exception:
                raise ValueError(
                    f'The asymptomatic_r0 should be a float number, if it is not a multiplier for groups: {pars[0]} provided'
                )
        elif len(pars) == 2:
            try:
                self.set('asymptomatic_r0', 'low', float(pars[0]))
            except Exception:
                raise ValueError(
                    f'The asymptomatic_r0 should be a float number, if it is not a multiplier for groups: {pars[0]} provided'
                )
            try:
                self.set('asymptomatic_r0', 'high', float(pars[1]))
            except Exception:
                raise ValueError(
                    f'The asymptomatic_r0 should be a float number, if it is not a multiplier for groups: {pars[1]} provided'
                )
        elif len(pars) > 2:
            raise ValueError(
                f'The asymptomatic_r0 should be one or two float number.')
        #
        for multiplier in [x for x in val if '=' in x]:
            name, value = multiplier.split('=', 1)
            try:
                value = float(value)
            except Exception:
                raise ValueError(
                    f'Multiplier should have format name=float_value: {multiplier} provided'
                )
            self.set('asymptomatic_r0', f'multiplier_{name}', value)

    def set_incubation_period(self, val):
        if not val:
            return

        pars = [x for x in val if x in ('normal', 'lognormal') or '=' not in x]
        if pars:
            if len(pars) < 3:
                raise ValueError(
                    f'Parameter incubation period requires aat least three values: {len(val)} provided'
                )
            if pars[0] not in ('normal', 'lognormal'):
                raise ValueError(
                    f'Only normal or lognormal distribution for incubation period is supported. {pars[0]} provided'
                )
            try:
                self.set('incubation_period',
                         'mean' if pars[0] == 'lognormal' else 'loc',
                         float(pars[1]))
            except Exception:
                raise ValueError(
                    f'Second parameter of incubation_period should be a float number: {pars[1]} provided'
                )
            try:
                self.set('incubation_period',
                         'sigma' if pars[0] == 'lognormal' else 'scale',
                         float(pars[2]))
            except Exception:
                raise ValueError(
                    f'Third parameter of lognormal incubation_period should be a float number: {pars[2]} provided'
                )
        # multipliers
        for multiplier in [x for x in val if '=' in x]:
            name, value = multiplier.split('=', 1)
            try:
                value = float(value)
            except Exception:
                raise ValueError(
                    f'Multiplier should have format name=float_value: {multiplier} provided'
                )
            self.set('incubation_period', f'multiplier_{name}', value)

    def set_susceptibility(self, val):
        if not val:
            return
        for multiplier in val:
            if '=' not in multiplier:
                raise ValueError(
                    f'Susceptibility has to be specified as name=weight: {multiplier} specified.'
                )
            name, value = multiplier.split('=', 1)
            try:
                value = float(value)
            except Exception:
                raise ValueError(
                    f'Multiplier should have format name=float_value: {multiplier} provided'
                )
            self.set('susceptibility', f'multiplier_{name}', value)

    def set_prop_asym_carriers(self, val):
        if not val:
            return
        try:
            pars = [float(x) for x in val if '=' not in x]
        except Exception:
            raise ValueError(
                f'Paramter prop-asym-carriers expect one or two float value or multipliers: {" ".join(val)} provided'
            )
        if len(pars) == 1:
            self.set('prop_asym_carriers', 'loc', float(pars[0]))
            self.set('prop_asym_carriers', 'scale', 0)
        elif len(pars) == 2:
            if pars[0] > pars[1]:
                raise ValueError(
                    f'Proportions for parameter prop-asym-carriers should be incremental.'
                )
            self.set('prop_asym_carriers', 'loc', (pars[0] + pars[1]) / 2)
            self.set('prop_asym_carriers', 'quantile_2.5', pars[0])
        elif len(pars) > 2:
            raise ValueError(
                f'Parameter prop-asym-carriers accepts one or two numbers.')
        #
        for multiplier in [x for x in val if '=' in x]:
            name, value = multiplier.split('=', 1)
            try:
                value = float(value)
            except Exception:
                raise ValueError(
                    f'Multiplier should have format name=float_value: {multiplier} provided'
                )
            self.set('prop_asym_carriers', f'multiplier_{name}', value)

    def set_params(self, args):
        # set some default values first
        self.set('simulation_interval', 'self',
                 args.interval if args else 1 / 24)
        self.set('prop_asym_carriers', 'loc', 0.25)
        self.set('prop_asym_carriers', 'quantile_2.5', 0.1)
        self.set('symptomatic_r0', 'low', 1.4)
        self.set('symptomatic_r0', 'high', 2.8)
        self.set('asymptomatic_r0', 'low', 0.28)
        self.set('asymptomatic_r0', 'high', 0.56)
        self.set('incubation_period', 'mean', 1.621)
        self.set('incubation_period', 'sigma', 0.418)

        if not args:
            return

        self.set_popsize(args.popsize)
        self.set_infectors(args.infectors)
        # modify from command line args
        self.set_symptomatic_r0(args.symptomatic_r0)
        self.set_asymptomatic_r0(args.asymptomatic_r0)
        self.set_incubation_period(args.incubation_period)
        self.set_susceptibility(args.susceptibility)
        self.set_prop_asym_carriers(args.prop_asym_carriers)


class Model(object):

    sd_5 = bisect(lambda x: norm.cdf(10, loc=5, scale=x) - 0.995, a=0.001, b=5)
    sd_6 = bisect(lambda x: norm.cdf(14, loc=6, scale=x) - 0.975, a=0.001, b=5)

    def __init__(self, params):
        self.params = params
        self.params.prop_asym_carriers = None

    def draw_prop_asym_carriers(self, group=''):
        self.params.prop_asym_carriers = np.random.normal(
            loc=self.params.prop_asym_carriers_loc,
            scale=self.params.prop_asym_carriers_scale)
        return min(
            max(
                self.params.prop_asym_carriers * getattr(
                    self.params, f'prop_asym_carriers_multiplier_{group}', 1.0),
                0), 1)

    def draw_is_asymptomatic(self):
        return np.random.uniform(0, 1) < self.params.prop_asym_carriers

    def draw_random_r0(self, symptomatic, group=''):
        '''
        Reproduction number, drawn randomly between 1.4 and 2.8.
        '''
        if symptomatic:
            r0 = np.random.uniform(self.params.symptomatic_r0_low,
                                   self.params.symptomatic_r0_high)
            return r0 * getattr(self.params,
                                f'symptomatic_r0_multiplier_{group}', 1.0)
        else:
            r0 = np.random.uniform(self.params.asymptomatic_r0_low,
                                   self.params.asymptomatic_r0_high)
            return r0 * getattr(self.params,
                                f'asymptomatic_r0_multiplier_{group}', 1.0)

    def draw_random_incubation_period(self, group=''):
        '''
        Incubation period, drawn from a lognormal distribution.
        '''
        if hasattr(self.params, 'incubation_period_loc'):
            # if a normal distribution is specified
            ip = max(
                0,
                np.random.normal(
                    loc=self.params.incubation_period_loc,
                    scale=self.params.incubation_period_scale))
        else:
            ip = np.random.lognormal(
                mean=self.params.incubation_period_mean,
                sigma=self.params.incubation_period_sigma)
        return ip * getattr(self.params,
                            f'incubation_period_multiplier_{group}', 1.0)

    def get_symptomatic_transmission_probability(self, incu, R0):
        '''Transmission probability.
        incu
            incubation period in days (can be float)

        R0
            reproductive number, which is the expected number of infectees

        interval
            interval of simulation, default to 1/24, which is by hours

        returns

        x
            time point
        y
            probability of transmission for each time point
        '''
        # right side with 6 day interval
        incu = incu * 2 / 3
        dist_right = norm(incu, self.sd_6)

        # if there is no left-hand-side
        if incu <= self.params.simulation_interval:
            x = np.linspace(0, incu + 8,
                            int((incu + 8) / self.params.simulation_interval))
            y = dist_right.pdf(x)
        else:
            # left hand side with a incu day interval
            try:
                sd_left = bisect(
                    lambda x: norm.cdf(2 * incu, loc=incu, scale=x) - 0.99,
                    a=0.001,
                    b=15,
                    xtol=0.001)
            except:
                # if incubation period is zer0
                sd_left = 0.0
            dist_left = norm(incu, sd_left)
            scale = dist_right.pdf(incu) / dist_left.pdf(incu)

            x = np.linspace(0, incu + 8,
                            int((incu + 8) / self.params.simulation_interval))
            idx = int(incu / self.params.simulation_interval)
            y = np.concatenate(
                [dist_left.pdf(x[:idx]) * scale,
                 dist_right.pdf(x[idx:])])
        return x, y / sum(y) * R0

    def get_asymptomatic_transmission_probability(self, R0):
        '''Asymptomatic Transmission probability.
        R0
            reproductive number, which is the expected number of infectees

        interval
            interval of simulation, default to 1/24, which is by hours

        returns

        x
            time point
        y
            probability of transmission for each time point
        '''
        dist = norm(4.8, self.sd_5)
        x = np.linspace(0, 12, int(12 / self.params.simulation_interval))
        y = dist.pdf(x)
        return x, y / sum(y) * R0
