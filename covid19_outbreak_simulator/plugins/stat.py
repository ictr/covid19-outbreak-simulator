from covid19_outbreak_simulator.event import EventType
from covid19_outbreak_simulator.plugin import BasePlugin


#
# This plugin take random samples from the population during evolution.
#
class stat(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(stat, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(stat, self).get_parser()
        parser.prog = '--plugin stat'
        parser.description = 'Print STAT information'
        return parser

    def apply(self, time, population, args=None):
        res = {}
        res[f'n_recovered'] = len([
            x for x, ind in population.items()
            if isinstance(ind.recovered, float)
        ])
        res[f'n_infected'] = len([
            x for x, ind in population.items()
        if isinstance(ind.infected, float)
        ])
        res[f'n_active'] = res['n_infected'] - res['n_recovered']
        res[f'n_popsize'] = len(population)
        res[f'incidence_rate'] = '0' if res[
            f'n_popsize'] == 0 else '{:.5f}'.format(res[f'n_active'] /
                                                    res[f'n_popsize'])
        res[f'seroprevalence'] = '0' if res[
            f'n_popsize'] == 0 else '{:.5f}'.format(res[f'n_infected'] /
                                                    res[f'n_popsize'])

        groups = set([x.group for x in population.values()])
        for group in groups:
            if group == '':
                continue
            res[f'n_{group}_recovered'] = len([
                x for x, ind in population.items()
                if isinstance(ind.recovered, float) and ind.group == group
            ])
            res[f'n_{group}_infected'] = len([
                x for x, ind in population.items()
                if isinstance(ind.infected, float) and ind.group == group
            ])
            res[f'n_{group}_active'] = res[f'n_{group}_infected'] - res[
                f'n_{group}_recovered']
            res[f'n_{group}_popsize'] = len(
                [x for x, ind in population.items() if ind.group == group])
            res[f'{group}_incidence_rate'] = 0 if res[
                f'n_{group}_popsize'] == '0' else '{:.3f}'.format(
                    res[f'n_{group}_active'] / res[f'n_{group}_popsize'])
            res[f'{group}_seroprevalence'] = 0 if res[
                f'n_{group}_popsize'] == '0' else '{:.3f}'.format(
                    res[f'n_{group}_infected'] / res[f'n_{group}_popsize'])
        param = ','.join(f'{k}={v}' for k, v in res.items())
        if args.verbosity > 0:
            self.logger.write(
                f'{time:.2f}\t{EventType.STAT.name}\t.\t{param}\n'
            )

        return []
