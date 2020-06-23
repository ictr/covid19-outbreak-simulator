from covid19_outbreak_simulator.plugin import BasePlugin


#
# This plugin changes R0 at certain time
#
class dynamic_r0(BasePlugin):

    def __init__(self, *args, **kwargs):
        # this will set self.simualtor, self.logger
        super(dynamic_r0, self).__init__(*args, **kwargs)

    def get_parser(self):
        parser = super(dynamic_r0, self).get_parser()
        parser.description = 'Change multiplier number at specific time.'
        parser.prog = '--plugin dynamic_r0'
        parser.add_argument(
            '--new-symptomatic-r0',
            nargs='+',
            help='''Updated production number of symptomatic infectors, should be specified as a single
                fixed number, or a range, and/or multipliers for different groups such as
                A=1.2. For example "--symptomatic-r0 1.4 2.8 nurse=1.2" means a general R0
                ranging from 1.4 to 2.8, while nursed has a range from 1.4*1.2 and 2.8*1.2.'''
        )
        parser.add_argument(
            '--new-asymptomatic-r0',
            nargs='+',
            help='''Updated production number of asymptomatic infectors, should be specified as a single
                fixed number, or a range and/or multipliers for different groups'''
        )
        return parser

    def apply(self, time, population, args=None, simu_args=None):
        # change parameter
        self.simulator.model.params.set_symptomatic_r0(args.new_symptomatic_r0)
        self.simulator.model.params.set_asymptomatic_r0(
            args.new_asymptomatic_r0)

        pars = {}
        if args.new_symptomatic_r0:
            pars['new_symptomatic_r0'] = args.new_symptomatic_r0
        if args.new_asymptomatic_r0:
            pars['new_asymptomatic_r0'] = args.new_asymptomatic_r0
        param = ','.join(f'{x}={y}' for x, y in pars.items())
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\tDYNAMIC_R\t.\t{param}\n')
        return []
