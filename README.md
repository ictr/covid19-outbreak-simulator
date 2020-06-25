[![PyPI](https://img.shields.io/pypi/v/covid19-outbreak-simulator.svg)](https://pypi.python.org/pypi/covid19-outbreak-simulator)
[![PyPI version](https://img.shields.io/pypi/pyversions/covid19-outbreak-simulator.svg)](https://pypi.python.org/pypi/covid19-outbreak-simulator)
[![Documentation Status](https://readthedocs.org/projects/covid19-outbreak-simulator/badge/?version=latest)](https://covid19-outbreak-simulator.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/ictr/covid19-outbreak-simulator.svg?branch=master)](https://travis-ci.org/ictr/covid19-outbreak-simulator)
[![Coverage Status](https://coveralls.io/repos/github/ictr/covid19-outbreak-simulator/badge.svg?branch=master&service=github)](https://coveralls.io/github/ictr/covid19-outbreak-simulator?branch=master)
[![Documentation Status](https://readthedocs.org/projects/covid19-outbreak-simulator/badge/?version=latest)](https://covid19-outbreak-simulator.readthedocs.io/en/latest/?badge=latest)





The COVID-19 outbreak simulator simulates the outbreak of COVID-19 in a population. It was first designed to simulate
the outbreak of COVID-19 in small populations in enclosed environments, such as a FPSO (floating production storage and
offloading vessel) but has since been expanded to simulate much larger populations with dynamic parameters.

This README file contains all essential information but you can also visit our [documentation](https://covid19-outbreak-simulator.readthedocs.io/en/latest/?badge=latest) for more details. Please feel free to [contact us](https://github.com/ictr/covid19-outbreak-simulator/issues) if you would like to simulate any particular environment.


<!--ts-->
   * [Background](#background)
      * [Basic assumptions](#basic-assumptions)
      * [Statistical models](#statistical-models)
      * [Simulation method](#simulation-method)
      * [Limitation of the simulator](#limitation-of-the-simulator)
   * [Installation and basic usage](#installation-and-basic-usage)
      * [Installation](#installation)
      * [Getting help](#getting-help)
      * [Command line options of the core simulator](#command-line-options-of-the-core-simulator)
   * [Plug-in system (advanced usages)](#plug-in-system-advanced-usages)
      * [Specify one or more plugins from command line](#specify-one-or-more-plugins-from-command-line)
      * [System plugins](#system-plugins)
         * [Common paramters of plugins](#common-paramters-of-plugins)
         * [Plugin init](#plugin-init)
         * [Plugin setparam](#plugin-setparam)
         * [Plugin stat](#plugin-stat)
         * [Plugin sample](#plugin-sample)
         * [Plugin insert](#plugin-insert)
         * [Plugin quarantine](#plugin-quarantine)
         * [Plugin pcrtest](#plugin-pcrtest)
      * [Implementation of plugins](#implementation-of-plugins)
   * [Output from the simulator](#output-from-the-simulator)
      * [Events tracked during the simulation](#events-tracked-during-the-simulation)
      * [Summary report from multiple replicates](#summary-report-from-multiple-replicates)
      * [Data analysis tools](#data-analysis-tools)
         * [time_vs_size.R](#time_vs_sizer)
         * [merge_summary.py](#merge_summarypy)
   * [Examples](#examples)
      * [A small population with the introduction of one carrier](#a-small-population-with-the-introduction-of-one-carrier)
      * [Evolution of a large population](#evolution-of-a-large-population)
      * [Heterogeneous situation](#heterogeneous-situation)
         * [Specigy group-specific parameters](#specigy-group-specific-parameters)
   * [Acknowledgements](#acknowledgements)
   * [Change Log](#change-log)
      * [Version 0.3.0](#version-030)
      * [Version 0.2.0](#version-020)
      * [Version 0.1.0](#version-010)

<!-- Added by: bpeng, at: Wed Jun 24 01:08:06 CDT 2020 -->

<!--te-->

# Background

## Basic assumptions

This simulator simulates the scenario in which

-   A group of individuals in a population in which everyone is susceptible. The population
    is by default free of virus, but seroprevalence and incidance rate could be specifed
    to initialize the population with virus.
-   The population can be divided into multiple subgroups with different parameters.
-   One or more virus carriers are introduced to the population, potentially after a fixed
    days of self-quarantine.
-   Infectees are by default removed from from the population (separated, quarantined,
    hospitalized, or deceased, as long as he or she can no longer infect others) after they
    displayed symptoms, but options are provided to act otherwise.
-   The simulation is by default stopped after the population is free of virus (all
    infected individuals have been removed), or everyone is infected, or after
    a pre-specified time (e.g. after 10 days).
-   More complex simulation scenarios are provided by a plugin system where actions such as
    contact tracing, sampling can be simulated.

The simulator simulates the epidemic of the population with the introduction of
infectors. Detailed statistics are captured from the simulations to answer questions
such as:

1. What is the expected day and distribution for the first person to show
   symptoms?
2. How many people are expected to be removed once an outbreak starts?
3. How effective will self-quarantine before dispatch personnels to an
   enclosed environment?

The simulator uses the latest knowledge about the spread of COVID-19 and is
validated against public data. This project will be contantly updated with our
deepening knowledge on this virus.

## Statistical models

We developed multiple statistical models to model the incubation time, serial interval,
generation time, proportion of asymptomatic transmissions, using results from
multiple publications. We validated the models with empirical data to ensure they
generate, for example, correct distributions of serial intervals and proporitons
of asymptomatic, pre-symptomatic, and symptomatic cases.

The statistical models and related references are available at

-   [Statistical models of COVID-19 outbreaks (Version 1)](https://bioworkflows.com/ictr/COVID19-outbreak-simulator-model/1)
-   [Statistical models of COVID-19 outbreaks (Version 2)](https://bioworkflows.com/ictr/COVID19-outbreak-simulator-model/2)

The models will continuously be updated as we learn more about the virus.

## Simulation method

This simulator simulations individuals in a population using an event-based model. Briefly
speaking,

1. The simulator creates an initial population with a set of initial `events` (see later section for details)

2. The events will happen at a pre-specified time and will trigger further events. For example,
  an `INFECTION` event will cause someone to be infected with the virus. The individual will be marked as `infected` and according to individualized parameters of the infectivity of the infected individual, the `INFECTION` event may trigger a series of events such as `INFECTION` to other
  individuals, `SHOW_SYMPTIOM` if he or she is symptomatic and will show symptom after an incubation
  period, `REMOVAL` or `QUARANTINE` after symptoms are detected.

3. After processing all events at a time point, the simulator will call specified plugins, which
  can perform a variety of operations to the population.

4. The simulator processes and logs the events and stops after pre-specified exit condition.


## Limitation of the simulator

* The simulator assumes a "mixed" population. Although some groups might be more suscepticle
  to the virus, people in the same group will be equally likely to be infected.

* The simulator does not simulate "contact" or "geographic locations", so it is not yet possible
  to similate scenarios such as "contact centers" such as supermarkets and subways.

# Installation and basic usage

## Installation

This simulator is programmed using Python >= 3.6 with `numpy` and `scipy`. A conda environment is
recommended. After setting up a conda environment with Python >= 3.6 and these two packages,
please run

```
pip install -r requirements.txt
```

to install required packages, and then

```
pip install covid19-outbreak-simulator
```

to install the simulator.

## Getting help

You can then use command

```
outbreak_simulator -h
```

to check the usage information of the basic simulator,

```
outbreak_simualtor --plugin -h
```
to get decription of common parameters for plugins, and

```
outbreak_simulator --plugin plugin_name -h
```
to get the usage information of a particular plugin.

## Command line options of the core simulator

```
$ outbreak_simulator -h

usage: outbreak_simulator [-h] [--popsize POPSIZE [POPSIZE ...]] [--susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]]
                          [--symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]] [--asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]]
                          [--incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]] [--repeats REPEATS]
                          [--handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]] [--infectors [INFECTORS [INFECTORS ...]]]
                          [--interval INTERVAL] [--logfile LOGFILE] [--prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]]
                          [--stop-if [STOP_IF [STOP_IF ...]]] [--leadtime LEADTIME] [--plugin ...] [-j JOBS]

optional arguments:
  -h, --help            show this help message and exit
  --popsize POPSIZE [POPSIZE ...]
                        Size of the population, including the infector that will be introduced at the beginning of the simulation. It should
                        be specified as a single number, or a serial of name=size values for different groups. For example "--popsize
                        nurse=10 patient=100". The names will be used for setting group specific parameters. The IDs of these individuals
                        will be nurse0, nurse1 etc.
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
  --repeats REPEATS     Number of replicates to simulate. An ID starting from 1 will be assinged to each replicate and as the first columns
                        in the log file.
  --handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]
                        How to handle individuals who show symptom, which should be "keep" (stay in population), "remove" (remove from
                        population), and "quarantine" (put aside until it recovers). all options can be followed by a "proportion", and
                        quarantine can be specified as "quarantine_7" etc to specify duration of quarantine.
  --infectors [INFECTORS [INFECTORS ...]]
                        Infectees to introduce to the population. If you would like to introduce multiple infectees to the population, or if
                        you have named groups, you will have to specify the IDs of carrier such as --infectors nurse1 nurse2.
  --interval INTERVAL   Interval of simulation, default to 1/24, by hour
  --logfile LOGFILE     logfile
  --prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]
                        Proportion of asymptomatic cases. You can specify a fix number, or two numbers as the lower and higher CI (95%) of
                        the proportion. Default to 0.10 to 0.40. Multipliers can be specified to set proportion of asymptomatic carriers for
                        particular groups.
  --stop-if [STOP_IF [STOP_IF ...]]
                        Condition at which the simulation will end. By default the simulation stops when all individuals are affected or all
                        infected individuals are removed. Current you can specify a time after which the simulation will stop in the format
                        of `--stop-if "t>10"' (for 10 days).
  --leadtime LEADTIME   With "leadtime" infections are assumed to happen before the simulation. This option can be a fixed positive number
                        `t` when the infection happens `t` days before current time. If can also be set to 'any' for which the carrier can be
                        any time during its course of infection, or `asymptomatic` for which the leadtime is adjust so that the carrier does
                        not show any symptom at the time point (in incubation period for symptomatic case). All events triggered before
                        current time are ignored.
  --plugin ...          One or more of "--plugin MODULE.PLUGIN [args]" to specify one or more plugins. FLUGIN will be assumed to be MODULE
                        name if left unspecified. Each plugin has its own parser and can parse its own args.
  -j JOBS, --jobs JOBS  Number of process to use for simulation. Default to number of CPU cores.

```


# Plug-in system (advanced usages)

It is very likely that for complex simulations you would have scenarios that are
not provided by the core simulator. This simulator has a plug-in system that allows
you to define your own functions that would be called by the simulator at specified
intervals or events.


## Specify one or more plugins from command line

To use plugins for a simulation, they should be specified as:

```bash
outbreak_simulator \
   # regular parameters
   -j 4 \
   # first system plugin
   --plugin contact_tracing --succ-rate 0.8  \
   # second (customied) plugin
   --plugin modulename1.plugin_name1 --start 10 --par2 val2 --par3
```
where

1. Each plugin is defined after a `--plugin` parameter and before another `--plugin` or the end of command line arguments.
2. A plugin can be a system plugin that is located under the `plugins` directory, or a cutomized plugin that you have defined.
3. A plugin can be specified by `modulename` if it is the name of the python module and the name of the plugin class, or `modulename.plugin_name` if the class has a different name.
4. Plugins accept a common set of parameters (e.g. `--start`, `--end`) to define when the plugin will be triggered.
5. The rest of the plugin parameters will be parsed by the plugin


## System plugins

### Common paramters of plugins

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

## Implementation of plugins

Implementation wise, the plugins should be written as Python classes that

1. Drive from `outbreak_simulator.BasePlugin` and calls its `__init__` function. This will point `self.simulator`, and `self.logger` of the plugin to the simulator, population, and logger of the simulator. `simulator` has properties such as `simu_args`, `params`, and `model` so you can access command line simulator arguments, model parameters, and change simulation model (e.g. parameters).

2. Provide as member function:

  * `get_parser()` (optional): a function that extends the base parser to add plugin specific arguments.

  * `apply(time, population, args)` (required): A function that accepts parameters `time` (time when the plugin is called) and `args` (plugin args).

The plugin can change the status of the population or simulation parameters, write to system log `simulator.logger` or write to its own output files. It should return a list of events that can happen at a later time, or an empty list indicating no future event is triggered.

The base class will handle the logics when the plugin will be executed (parameters `--start`, `--end`, `--interval`
`--at` and `--trigger-by`). Please check the [plugins directory](https://github.com/ictr/covid19-outbreak-simulator/tree/master/covid19_outbreak_simulator/plugins) for examples on how to write plugins for the simulator.



# Output from the simulator

## Events tracked during the simulation

The output file contains events that happens during the simulations.
For example, for command

```
outbreak_simulator --repeat 100 --popsize 64 --logfile result_remove_symptomatic.txt
```

You will get an output file `result_remove_symptomatic.txt` with the following columns:

| column   | content                                                                                                                |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| `id`     | id of the simulation.                                                                                                  |
| `time`   | time of the event in days, accurate to hour.                                                                           |
| `event`  | type of event                                                                                                          |
| `target` | subject of the event, for example the ID of the individual that has been quarantined.                                  |
| `params` | Additional parameters, mostly for the `INFECTION` event where simulated $R_0$ and incubation period will be displayed. |

Currently the following events are tracked

| Name                | Event                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------- |
| `START`             | Start up simulation.                                                                    |
| `INFECTION`         | Infect an non-quarantined individual, who might already been infected.                  |
| `INFECION_FAILED`   | No one left to infect                                                                   |
| `INFECTION_AVOIDED` | An infection happended during quarantine. The individual might not have showed sympton. |
| `INFECTION_IGNORED` | Infect an infected individual, which does not change anything.                          |
| `SHOW_SYMPTOM`      | Show symptom.                                                                           |
| `REMOVAL`           | Remove from population.                                                                 |
| `RECOVER`           | Recovered, no longer infectious                                                         |
| `QUARANTINE`          | Quarantine someone till specified time.                                                 |
| `REINTEGRATION`     | Reintroduce the quarantined individual to group.                                        |
| `STAT`              | Report population stats at specified intervals.                                         |
| `ABORT`             | If the first carrier show sympton during quarantine.                                    |
| `END`               | Simulation ends.                                                                        |
| `ERROR`             | An error was raised.                                                      |

The log file of a typical simulation would look like the following:

```
id      time    event   target  params
2       0.00    START   .       id=2,time=06/23/2020-17:51:39,args=--infector 0
2       0.00    INFECTION       0       r0=2.10,r=0,r_presym=0,r_sym=0,incu=4.99
2       4.99    SHOW_SYMPTOM    0       .
2       4.99    REMOVAL 0       popsize=63
2       11.33   RECOVER 0       recovered=0,infected=0,popsize=63,True=True
2       11.33   END     63      popsize=63,prop_asym=0.123,time=06/23/2020-17:51:39
3       0.00    START   .       id=3,time=06/23/2020-17:51:39,args=--infector 0
3       0.00    INFECTION       0       r0=1.49,r=0,r_presym=0,r_sym=0,incu=5.47
3       5.47    SHOW_SYMPTOM    0       .
3       5.47    REMOVAL 0       popsize=63
3       11.64   RECOVER 0       recovered=0,infected=0,popsize=63,True=True
3       11.64   END     63      popsize=63,prop_asym=0.220,time=06/23/2020-17:51:39
7       0.00    START   .       id=7,time=06/23/2020-17:51:39,args=--infector 0
7       0.00    INFECTION       0       r0=0.43,r=0,r_asym=0
```

which I assume would be pretty self-explanatory. Note that **the simulation IDs
are not ordered because the they are run in parallel but you can expect all events
belong to the same simulation are recorded together.**.

## Summary report from multiple replicates

At the end of each command, a report will be given to summarize key statistics from
multiple replicated simulations. The output contains the following keys and their values

| name                                  | value                                                                                                                                                                                     |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `logfile`                             | Log file of the simulation with all the events                                                                                                                                            |
| `popsize`                             | Initial population size                                                                                                                                                                   |
| `handle_symptomatic`                    | If asymptomatic infectees are kept, removed, or quarantined, at what percentage.                                                                                                                                                        |
| `prop_asym_carriers`                  | Proportion of asymptomatic carriers, also the probability of infectee who do not show any symptom                                                                                         |
| `interval`                            | Interval of time events (1/24 for hours)                                                                                                                                                  |
| `n_simulation`                        | Total number of simulations, which is the number of `END` events                                                                                                                          |
| `total_infection`                     | Number of `INFECTION` events                                                                                                                                                              |
| `total_infection_failed`              | Number of `INFECTION_FAILED` events                                                                                                                                                       |
| `total_infection_avoided`             | Number of `INFECTION_AVOIDED` events                                                                                                                                                      |
| `total_infection_ignored`             | Number of `INFECTION_IGNORED` events                                                                                                                                                      |
| `total_show_symptom`                  | Number of `SHOW_SYMPTOM` events                                                                                                                                                           |
| `total_removal`                       | Number of `REMOVAL` events                                                                                                                                                                |
| `total_quarantine`                    | Number of `QUARANTINE` events                                                                                                                                                             |
| `total_reintegration`                 | Number of `REINTEGRATION` events                                                                                                                                                          |
| `total_abort`                         | Number of `ABORT` events                                                                                                                                                                  |
| `total_asym_infection`                | Number of asymptomatic infections                                                                                                                                                         |
| `total_presym_infection`              | Number of presymptomatic infections                                                                                                                                                       |
| `total_sym_infection`                 | Number of symptomatic infections                                                                                                                                                          |
| `n_remaining_popsize_XXX`             | Number of simulations with `XXX` remaining population size                                                                                                                                |
| `n_no_outbreak`                       | Number of simulations with no outbreak (no symptom from anyone, or mission canceled)                                                                                                      |
| `n_outbreak_duration_XXX`             | Number of simulations with outbreak ends in day `XXX`. Pre-quarantine days are not counted as outbreak. Outbreak can end at day 0 if the infectee will not show symtom or infect others.  |
| `n_no_infected_by_seed`               | Number of simulations when the introduced carrier does not infect anyone                                                                                                                  |
| `n_num_infected_by_seed_XXX`          | Number of simulations with `XXX` people affected by the introduced virus carrier, `XXX > 0` .                                                                                             |
| `n_first_infected_by_seed_on_day_XXX` | Number of simulations when the introduced carrier infect the first infectee on day `XXX`, `XXX<1` is rounded to 1, and so on. Pre-quarantine time is deducted.                            |
| `n_seed_show_no_symptom`              | Number of simulations when the seed show no symptom                                                                                                                                       |
| `n_seed_show_symptom_on_day_XXX`      | Number of simulations when the carrier show symptom at day `XXX`, `XXX < 1` is rounded to 1, and so on.                                                                                   |
| `n_no_first_infection`                | Number of simualations with no infection at all.                                                                                                                                          |
| `n_first_infection_on_day_XXX`        | Number of simualations with the first infection event happens at day `XXX`. It is the same as `XXX_n_first_infected_by_seed_on_day` but is reserved when multiple seeds are introduced.   |
| `n_first_symptom`                     | Number of simulations when with at least one symptomatic case                                                                                                                             |
| `n_first_symptom_on_day_XXX`          | Number of simulations when the first symptom appear at day `XXX`, `XXX < 1` is rounded to 1, and so on. Symptom during quarantine is not considered and pre-quarantine days are deducted. |
| `n_second_symptom`                    | Number of simulations when there are a second symptomatic case symptom.                                                                                                                   |
| `n_second_symptom_on_day_XXX`         | Number of simulations when the second symptom appear at day `XXX` **after the first symptom**                                                                                             |
| `n_third_symptom`                     | Number of simulations when there are a third symptomatic case symtom                                                                                                                      |
| `n_third_symptom_on_day_XXX`          | Number of simulations when the first symptom appear at day `XXX` **after the second symptom**                                                                                             |
| `n_popsize_XXX` | Population size at time `XXX`, a list if multiple replicates |
| `n_YYY_popsize_XXX` | Population size of group YYY at time `XXX` a list if multiple replicates |
| `n_infected_XXX` | Number of infected individuals at time `XXX` a list if multiple replicates |
| `n_YYY_infected_XXX` | Number of infected individuals in group YYY at time `XXX` a list if multiple replicates |
| `n_recovered_XXX` | Number of recovered individuals at time `XXX` a list if multiple replicates |
| `n_YYY_recovered_XXX` | Number of recovered individuals in group YYY at time `XXX` a list if multiple replicates |
| `incidence_rate_XXX` | Incidence rate (infected/popsize) at time `XXX` a list if multiple replicates |
| `YYY_incidence_rate_XXX` | Incidence rate in group YYY at time `XXX` a list if multiple replicates |
| `seroprevalence_XXX` | Seroprevalence (infected + recovered)/popsize) at time `XXX` a list if multiple replicates |
| `YYY_seroprevalence_XXX` | Seroprevalence in group YYY at time `XXX` a list if multiple replicates |
| `avg_n_popsize_XXX` | Average population size at time `XXX`  if there are multiple replicates |
| `avg_n_YYY_popsize_XXX` | Average population size of group YYY at time `XXX`  if there are multiple replicates |
| `avg_n_infected_XXX` | Average number of infected individuals at time `XXX`  if there are multiple replicates |
| `avg_n_YYY_infected_XXX` | Average number of infected individuals in group YYY at time `XXX` if there are multiple replicates |
| `avg_n_recovered_XXX` | Average number of recovered individuals at time `XXX` if there are multiple replicates |
| `avg_n_YYY_recovered_XXX` | Average number of recovered individuals in group YYY at time `XXX` if there are multiple replicates |
| `avg_incidence_rate_XXX` | Average incidence rate (infected/popsize) at time `XXX` if there are multiple replicates |
| `avg_YYY_incidence_rate_XXX` | Average incidence rate in group YYY at time `XXX` if there are multiple replicates |
| `avg_seroprevalence_XXX` | Average neroprevalence (infected + recovered)/popsize) at time `XXX` if there are multiple replicates |
| `avg_YYY_seroprevalence_XXX` | Average seroprevalence in group YYY at time `XXX` if there are multiple replicates |
| `EVENT_STAT_XXX` | Reported statistics `STAT` for customized event `EVENT` at time `XXX` a list if multiple replicates |
| `avg_EVENT_STAT_XXX` | Average reported statistics `STAT` for customized event `EVENT` at time `XXX` if there are multiple replicates |

NOTE: All `avg_` fields have average over existing replicates, and all replicates. For
example, if at time 100, 8 of the replicate simulations have completed and the rest 2
have population size 5, and 10, the average population size will be reported as
`7.5` (`5+10/2`) and `0.15` (`5+10/10`).

## Data analysis tools

Because all the events have been recorded in the log files, it should not be too difficult for
you to write your own script (e.g. in R) to analyze them and produce nice figures. We however
made a small number of tools available. Please feel free to submit or own script for inclusion in the `contrib`
library.

### `time_vs_size.R`

The [`contrib/time_vs_size.R`](https://github.com/ictr/covid19-outbreak-simulator/blob/master/contrib/time_vs_size.R) script provides an example on how to process the data and produce
a figure. It can be used as follows:

```
Rscript time_vs_size.R  simulation.log 'COVID19 Outbreak Simulation with Default Paramters' time_vs_size.png
```

and produces a figure

![time_vs_size.png](https://raw.githubusercontent.com/ictr/covid19-outbreak-simulator/master/contrib/time_vs_size.png)

### `merge_summary.py`

[`contrib/merge_summary.py`](https://github.com/ictr/covid19-outbreak-simulator/blob/master/contrib/merge_summary.py) is a script to merge summary stats from multiple simulation runs.



# Examples

## A small population with the introduction of one carrier

Assuming that there is no asymptomatic carriers, we can introduce one infected
carrier to a population of size 64, and observe the development of the outbreak.

```sh
outbreak_simulator --infector 0  --rep 10000 --prop-asym-carriers 0 --logfile simu_remove_symptomatic.log
```

We can also assume from 20% to 40% of infected individuals will not show any symptom
the default parameters for `prop-asym-carriers` is `0.2` to `0.4` so it is actually
not needed.

```sh
outbreak_simulator --infector 0  --rep 10000 --prop-asym-carriers .20 .40 --logfile simu_with_asymptomatic.log
```

We can quarantine the carrier for 7 days, but here we need to use a plugin that applies at time 0

```sh
outbreak_simulator --infector 0  --rep 10000 --logfile simu_quarantine_7.log \
  --plugin quarantine --at 0 --duration 7
```

or we can try quarantine for 14 days...

```sh
outbreak_simulator --infector 0  --rep 10000 --logfile simu_quarantine_15.log \
  --plugin quarantine --at 0 --duration 14
```

The above simulation assumes that the carriers are infected right before quarantine, which is not really
realistic. The following add some `leadtime` and simulate scenarios that people enters quarantine
as long as they do not show symptom.

```
outbreak_simulator --infector 0  --rep 10000 --leadtime asymptomatic --logfile simu_leadtime_quarantine_7.log -j 1 \
  --plugin quarantine --at 0 --duration 7
```

## Evolution of a large population

Assuming a population of size `34993` with `85` total cases (in the past few months). Assuming that every case has 4
unreported (asymptomatic etc) cases, there has been `85*5` cases so the population has a seroprevalence of
`85*5/34993=0.01214`. Assuming 8 weeks outbreak duration and 2 week active window, 1/4 cases would be "active",
so the current incidence rate would be `85*5/4 / 34993 = 0.003036`.

We assume that 75% of all symptomatic cases will be quarantined (hospitalized), the rest would be able to infect
others. We only simulate 1 replicate because the population size is large. The command to simulate this population
is as follows:

```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
    --logfile pop_quarantine_all.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_quarantine_all.txt
```

The simulation shows that the last case will recover after 173 days with 4.18% seroprevalence,
a total of 1462 cases (29 deaths if we assume 2% fatality rate) at the end of the simulation.
Active cases of 104 new cases happens around the 50 days.

However, if people with mild symptoms are not hospitalized (or quarantined) and continue
to infect others, the situation will get much worse.

```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 0.75 \
    --logfile pop_quarantine_.75.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_quarantine_.75.txt
```

The simulation shows that the outbreak will last 223 days with a seroprevalence of `32%`.
A total of 11205 people will be infected (224 deaths if we assume 2% fatality rate). A peak
of 1500 cases per day happens at around 80 days.

Social distancing can slow down the spread of the disease. The current R0 for symptomatic cases
is assumed to be between 1.4 and 2.8.

Let us assume that we can tighten up social distancing to half the R0 from 0.7 to 1.4, at day 20

```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
    --logfile pop_distancing_at_20.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_distancing_at_20.txt \
    --plugin setparam --symptomatic-r0 1.2 2.4 --at 20
```

With increased social distancing, the daily number of cases starts to decline shortly after
day 20 (about 346), the outbreak still lasted 263 days but seroprevalence peaked at 4.42%.q

Now, what if we start social distancing earlier, say at day 10?


```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
    --logfile pop_distancing_at_10.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 \
    --plugin setparam --symptomatic-r0 1.2 2.4 --at 10 \
    > pop_distancing_at_10.txt
```

The peak happens after day 10 at around 200 cases per day. The outbreak stops after 80
days, with an ending seroprevalence of `2.2%`.

## Heterogeneous situation

Now, let us assume that we have a population with two subpopulations `A` and `B`, be they workers and guest, doctors and patients. Now let us assume that subpopulation `A` is more
susceptible (more contact with others), and more infectious. Let us also assume that
there is a intermediate inflow of `A` to the population, half of them would be carriers.
This simulation can be written as

```sh
outbreak_simulator --popsize A=2000 B=500 --rep 10 --handle-symptomatic quarantine_14 1 \
  --susceptibility A=1.2 --symptomatic-r0 A=1.2 B=0.8 --logfile hetero.log \
  --stop-if 't>40' \
  --plugin stat --interval 1 \
  --plugin insert A=5 --prop-of-infected 0.5 --interval 1 \
  > hetero.txt

```

because the continuous injection of cases, the outbreak will not stop by itself so we have
to use `--stop-at 't>40'` to set the duration of the simulation.

### Specigy group-specific parameters

Parameters `symptomatic-r0`, `asymptomatic-r0` and `incubation-period` can be
set to different values for each groups. These are achived by "multipliers",
which multiplies specified values to values drawn from the default distribution.

For example, if in a hospital environment nurses, once affected, tends to have
higher `R0` because he or she contact more patients, and on the other hand
patients are less mobile and should have lower `R0`. In some cases the nurses
are even less protected and are more susceptible. You can run a simulation
with two patients carrying the virus with the following options:

```
outbreak_simulator --popsize nurse=10 patient=100 \
    --symptomatic-r0 nurse=1.5 patient=0.8 \
    --asymptomatic-r0 nurse=1.5 patient=0.8 \
    --susceptibility nurse=1.2 patient=0.8 \
    --infector patient0 patient1
```

# Acknowledgements

This tool has been developed and maintained by Dr. Bo Peng, associate professor at the Baylor College of Medicine, with guidance from Dr. Christopher Amos, from the [Institute for Clinical and Translational Research, Baylor College of Medicine](https://www.bcm.edu/research/office-of-research/clinical-and-translational-research). Contributions to this project are welcome. Please refer to the [LICENSE](https://github.com/ictr/outbreak_simulator/blob/master/LICENSE) file for proper use and distribution of this tool.

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage) project template.


# Change Log

## Version 0.3.0

* A new plugin system that can be triggered by options `--begin`, `--end`, `--interval`, `--at`, and `--trigger-by`.
* Add a number of system plugins including `init`, `sample`, `setparam`, and `quarantine`, some of them are separated from the simulator core.

## Version 0.2.0

* Generate reports from log files to make it easier to generate statistics
* Add contrib directory to facilitate data analysis.

## Version 0.1.0

* Initial release
