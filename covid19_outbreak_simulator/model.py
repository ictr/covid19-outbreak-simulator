
import random
import re

import numpy as np
from scipy.stats import norm
from scipy.optimize import bisect

sd_5 = bisect(lambda x: norm.cdf(10, loc=5, scale=x) - 0.995, a=0.001, b=5)
sd_6 = bisect(lambda x: norm.cdf(14, loc=6, scale=x) - 0.975, a=0.001, b=5)

class Params:
    def __init__(self):
        self.params = set([
            'incubation_period',
                'proportion_of_asymptomatic_carriers',
                'proportion_of_asymptomatic_carriers',
                'symptomatic_r0', 'asymptomatic_r0'
        ])

    def draw_proportion_of_asymptomatic_carriers(self):
        self.proportion_of_asymptomatic_carriers = np.random.normal(
            loc=self.proportion_of_asymptomatic_carriers_loc,
            scale=self.proportion_of_asymptomatic_carriers_scale
        )

    def set(self, param, prop, value):
        if param not in self.params:
            raise ValueError(f'Unrecgonzied parameter {param}')
        if prop is None or prop == 'self':
            setattr(self, param, value)
        if prop in ('loc', 'low', 'high'):
            setattr(self, f'{param}_{prop}', value)
        elif re.match('quantile_(.*)', prop):
            lq = float(re.match('quantile_(.*)', prop)[1])/100
            loc = getattr(self, f'{param}_loc')
            sd = bisect(lambda x: norm.cdf(value, loc=loc,
                scale=x) - lq, a=0.00001, b=25)
            setattr(self, f'{param}_scale', sd)
        else:
            raise ValueError('Unrecognized property {prop}')


class Model(object):
    def __init__(self, params):
        self.params = params

    def drawn_is_asymptomatic(self):
        return np.random.uniform(0, 1) < self.params.proportion_of_asymptomatic_carriers

    def draw_random_r0(self, symptomatic):
        '''
        Reproduction number, drawn randomly between 1.4 and 2.8.
        '''

        return np.random.uniform(self.params.symptomatic_r0_low,
            self.params.symptomatic_r0_high) if symptomatic else             np.random.uniform(self.params.asymptomatic_r0_low,
            self.params.asymptomatic_r0_high)


    def draw_random_incubation_period(self):
        '''
        Incubation period, drawn from a lognormal distribution.
        '''
        return np.random.lognormal(mean=1.621, sigma=0.418)






    def get_symptomatic_transmission_probability(self, incu, R0, interval=1/24):
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
        dist_right = norm(incu, sd_6)
        # left hand side with a incu day interval
        sd_left = bisect(lambda x: norm.cdf(2*incu, loc=incu, scale=x) - 0.99, a=0.001, b=15, xtol=0.001)
        dist_left = norm(incu, sd_left)
        scale = dist_right.pdf(incu) / dist_left.pdf(incu)
        x = np.linspace(0, incu + 10, int((incu+10)/interval))
        idx = int(incu / interval)
        y = np.concatenate([dist_left.pdf(x[:idx])*scale, dist_right.pdf(x[idx:])])
        sum_y = sum(y)
        return x, y / sum(y) * R0


    def get_asymptomatic_transmission_probability(self, R0, interval=1/24):
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
        dist = norm(4.8, sd_5)
        x = np.linspace(0, 12, int(12/interval))
        y = dist.pdf(x)
        sum_y = sum(y)
        return x, y / sum(y) * R0
