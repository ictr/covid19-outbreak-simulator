---
title: The plugin system
permalink: /docs/plugins/
---


It is very likely that for complex simulations you would have scenarios that are
not provided by the core simulator. This simulator has a plug-in system that allows
you to define your own functions that would be called by the simulator at specified
time or intervals.


## Specify one or more plugins from command line

One or more plugins can be specified with option `--plugin` at the end of the
`outbreak_simuator` command, for example,

```bash
outbreak_simulator \
   # regular parameters
   -j 4 \
   # first plugin
   --plugin plugin1 --interval 1 --succ-rate 0.8  \
   # second plugin
   --plugin plugin_name --start 10 --par2 val2 --par3
```
where

1. Each plugin is defined after a `--plugin` parameter and before another `--plugin` or the end of command line arguments.
2. A plugin can be a system plugin that is located under the `plugins` directory, or a cutomized plugin that you have defined.
3. Plugins accept a common set of parameters (e.g. `--start`, `--end`, `--at` and `--interval`) to define when the plugin will be triggered.
5. The rest of the plugin parameters will be parsed by the plugin themselves


## Common paramters of plugins

All plugins accept the following parameters, which indicates when the plugins
will be called.

```sh
% outbreak_simulator --plugin -h

A plugin for covid19-outbreak-simulator

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.

```

## System plugins

### Plugin `init`

```sh
% outbreak_simulator --plugin init -h

usage: --plugin init [-h] [--start START] [--end END] [--at AT [AT ...]] [--interval INTERVAL]
                     [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]] [--incidence-rate [INCIDENCE_RATE [INCIDENCE_RATE ...]]]
                     [--seroprevalence [SEROPREVALENCE [SEROPREVALENCE ...]]]

Initialize population with initial prevalence and seroprevalence

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.
  --incidence-rate [INCIDENCE_RATE [INCIDENCE_RATE ...]]
                        Incidence rate of the population (default to zero), which should be the probability that any individual is
                        currently affected with the virus (not necessarily show any symptom). Multipliers can be specified to set
                        incidence rate of for particular groups (e.g. --initial-incidence-rate 0.1 docter=1.2 will set incidence rate
                        to 0.12 for doctors).
  --seroprevalence [SEROPREVALENCE [SEROPREVALENCE ...]]
                        Seroprevalence of the population (default to zero). The seroprevalence should always be greater than or euqal
                        to initial incidence rate. The difference between seroprevalence and incidence rate will determine the
                        "recovered" rate of the population. Multipliers can be specified to set incidence rate of for particular
                        groups (e.g. --initial-incidence-rate 0.1 docter=1.2 will set incidence rate to 0.12 for doctors).
```

### Plugin `setparam`

```
% outbreak_simulator --plugin setparam -h

usage: --plugin setparam [-h] [--start START] [--end END] [--at AT [AT ...]] [--interval INTERVAL]
                         [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]] [--susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]]
                         [--symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]] [--asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]]
                         [--incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]]
                         [--handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]]
                         [--prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]]

Change parameters of simulation.

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.
  --susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]
                        Weight of susceptibility. The default value is 1, meaning everyone is equally susceptible. With options such as "--
                        susceptibility nurse=1.2 patients=0.8" you can give weights to different groups of people so that they have higher or
                        lower probabilities to be infected.
  --symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]
                        Production number of symptomatic infectors, should be specified as a single fixed number, or a range, and/or
                        multipliers for different groups such as A=1.2. For example "--symptomatic-r0 1.4 2.8 nurse=1.2" means a general R0
                        ranging from 1.4 to 2.8, while nursed has a range from 1.4*1.2 and 2.8*1.2.
  --asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]
                        Production number of asymptomatic infectors, should be specified as a single fixed number, or a range and/or
                        multipliers for different groups
  --incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]
                        Incubation period period, should be specified as "lognormal" followed by two numbers as mean and sigma, or "normal"
                        followed by mean and sd, and/or multipliers for different groups. Default to "lognormal 1.621 0.418"
  --handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]
                        How to handle individuals who show symptom, which should be "keep" (stay in population), "remove" (remove from
                        population), and "quarantine" (put aside until it recovers). all options can be followed by a "proportion", and
                        quarantine can be specified as "quarantine_7" etc to specify duration of quarantine. Default to "remove", meaning all
                        symptomatic cases will be removed from population.
  --prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]
                        Proportion of asymptomatic cases. You can specify a fix number, or two numbers as the lower and higher CI (95%) of
                        the proportion. Default to 0.10 to 0.40. Multipliers can be specified to set proportion of asymptomatic carriers for
                        particular groups.
```

### Plugin `stat`

```sh
% outbreak_simulator --plugin stat -h

usage: --plugin stat [-h] [--start START] [--end END] [--at AT [AT ...]] [--interval INTERVAL]
                     [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]]

Print STAT information

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.

```

### Plugin `sample`

```sh
% outbreak_simulator --plugin sample -h

usage: --plugin sample [-h] [--start START] [--end END] [--at AT [AT ...]] [--interval INTERVAL]
                       [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]] (--proportion PROPORTION | --size SIZE)

Draw random sample from the population

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.
  --proportion PROPORTION
                        Proprotion of the population to sample.
  --size SIZE           Number of individuals to sample.

```


### Plugin `insert`

```
% outbreak_simulator --plugin insert -h

usage: --plugin insert [-h] [--start START] [--end END] [--at AT [AT ...]] [--interval INTERVAL] [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]]
                       [--prop-of-infected PROP_OF_INFECTED] [--leadtime LEADTIME]
                       popsize [popsize ...]

insert new individuals to the population

positional arguments:
  popsize               Population size, which should only add to existing populations

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.
  --prop-of-infected PROP_OF_INFECTED
                        Proportion of infected. Default to 1, meaning all are infected.
  --leadtime LEADTIME   With "leadtime" infections are assumed to happen before the simulation. This option can be a fixed positive number
                        `t` when the infection happens `t` days before current time. If can also be set to 'any' for which the carrier can be
                        any time during its course of infection, or `asymptomatic` for which the leadtime is adjust so that the carrier does
                        not show any symptom at the time point (in incubation period for symptomatic case). All events triggered before
                        current time are ignored.

```

### Plugin `quarantine`


```sh
% outbreak_simulator --plugin quarantine -h

usage: --plugin quarantine [-h] [--start START] [--end END] [--at AT [AT ...]] [--interval INTERVAL]
                           [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]] [--proportion PROPORTION] [--duration DURATION]
                           [IDs [IDs ...]]

Quarantine specified or all infected individuals for specified durations.

positional arguments:
  IDs                   IDs of individuals to quarantine.

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.
  --proportion PROPORTION
                        Proportion of affected individuals to quarantine. Default to all, but can be set to a lower value to indicate
                        incomplete quarantine. This option does not apply to cases when IDs are explicitly specified.
  --duration DURATION   Days of quarantine
```

### Plugin `pcrtest`

```
% outbreak_simulator --plugin pcrtest -h

usage: --plugin pcrtest [-h] [--start START] [--end END] [--at AT [AT ...]] [--interval INTERVAL]
                        [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]] [--proportion PROPORTION] [--handle-positive HANDLE_POSITIVE]
                        [IDs [IDs ...]]

PCR-based test that can pick out all active cases.

positional arguments:
  IDs                   IDs of individuals to test.

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0 starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.
  --proportion PROPORTION
                        Proportion of individuals to test. Individuals who are tested positive will by default be quarantined.
  --handle-positive HANDLE_POSITIVE
                        How to handle individuals who are tested positive, which should be "remove" (remove from population), and
                        "quarantine" (put aside until it recovers). Quarantine can be specified as "quarantine_7" etc to specify duration of
                        quarantine. Default to "remove", meaning all symptomatic cases will be removed from population.

```

### Plugin `community_spread`

This plugin models community infection where everyone has a pre-specified probabilty
of getting affected. The probability will be multiplies by population-specific susceptibility
values if option `--susceptibility` is specified.


```
% outbreak_simulator --plugin community_spread -h

usage: --plugin community_spread [-h] [--start START] [--end END] [--at AT [AT ...]]
                                 [--interval INTERVAL]
                                 [--trigger-by [TRIGGER_BY [TRIGGER_BY ...]]]
                                 [--probability PROBABILITY]

Community infection that infect everyone in the population randomly.

optional arguments:
  -h, --help            show this help message and exit
  --start START         Start time. Default to 0 no parameter is defined so the plugin
                        will be called once at the beginning.
  --end END             End time, default to none, meaning there is no end time.
  --at AT [AT ...]      Specific time at which the plugin is applied.
  --interval INTERVAL   Interval at which plugin is applied, it will assume a 0
                        starting time if --start is left unspecified.
  --trigger-by [TRIGGER_BY [TRIGGER_BY ...]]
                        Events that triggers this plug in.
  --probability PROBABILITY
                        The probability of anyone to be affected at a given interval,
                        which is usually per day (with option --interval 1). If
                        individuals have different susceptibility specified by option
                        --susceptibility, the probability will be multiplied by the
                        susceptibility multipliers, The infection events do not have to
                        cause actual infection because the individual might be in
                        quarantine, or has been infected. The default value of this
                        parameter is 0.005.
```

## Implementation of plugins

Implementation wise, the plugins should be written as Python classes that

1. Drive from `outbreak_simulator.BasePlugin` and calls its `__init__` function. This will
  point `self.simulator`, and `self.logger` of the plugin to the simulator, population, and
  logger of the simulator. `simulator` has properties such as `simu_args`, `params`, and `model`
  so you can access command line simulator arguments, model parameters, and change simulation
  model (e.g. parameters).

2. Provide as member function:

  * `get_parser()` (optional): a function that extends the base parser to add plugin specific arguments.

  * `apply(time, population, args)` (required): A function that accepts parameters `time` (time when the plugin is called) and `args` (plugin args).

The plugin can change the status of the population or simulation parameters, write to system log `simulator.logger` or write to its own output files. It should return a list of events that can happen at a later time, or an empty list indicating no future event is triggered.

The base class will handle the logics when the plugin will be executed (parameters `--start`, `--end`, `--interval`
`--at` and `--trigger-by`). Please check the [plugins directory](https://github.com/ictr/covid19-outbreak-simulator/tree/master/covid19_outbreak_simulator/plugins) for examples on how to write plugins for the simulator.
