# Installation and basic usage

## Installation

This simulator is programmed using Python >= 3.6 with `numpy` and `scipy`. A conda environment is
recommended. After setting up a conda environment with Python >= 3.6 and these two packages,
please run

```sh
pip install -r requirements.txt
```

to install required packages, and then

```sh
pip install covid19-outbreak-simulator
```

to install the simulator.

## Getting help

You can then use command

```sh
outbreak_simulator -h
```

to check the usage information of the basic simulator,

```sh
outbreak_simualtor --plugin -h
```
to get decription of common parameters for plugins and a list of system plugins, and

```sh
outbreak_simulator --plugin plugin_name -h
```
to get the usage information of a particular plugin.

## Command line options of the core simulator

```sh
$ outbreak_simulator -h
usage: outbreak_simulator [-h] [--popsize POPSIZE [POPSIZE ...]]
                          [--susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]]
                          [--symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]]
                          [--asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]]
                          [--incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]] [--repeats REPEATS]
                          [--handle-symptomatic] [--pre-quarantine [PRE_QUARANTINE [PRE_QUARANTINE ...]]]
                          [--initial-incidence-rate [INITIAL_INCIDENCE_RATE [INITIAL_INCIDENCE_RATE ...]]]
                          [--initial-seroprevalence [INITIAL_SEROPREVALENCE [INITIAL_SEROPREVALENCE ...]]]
                          [--infectors [INFECTORS [INFECTORS ...]]] [--interval INTERVAL] [--logfile LOGFILE]
                          [--prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]]
                          [--stop-if [STOP_IF [STOP_IF ...]]] [--allow-lead-time] [--analyze-existing-logfile]
                          [--plugin [PLUGINS [PLUGINS ...]]] [-j JOBS] [-s STAT_INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  --popsize POPSIZE [POPSIZE ...]
                        Size of the population, including the infector that will be introduced at the beginning
                        of the simulation. It should be specified as a single number, or a serial of name=size
                        values for different groups. For example "--popsize nurse=10 patient=100". The names
                        will be used for setting group specific parameters. The IDs of these individuals will be
                        nurse0, nurse1 etc.
  --susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]
                        Weight of susceptibility. The default value is 1, meaning everyone is equally
                        susceptible. With options such as "--susceptibility nurse=1.2 patients=0.8" you can give
                        weights to different groups of people so that they have higher or lower probabilities to
                        be infected.
  --symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]
                        Production number of symptomatic infectors, should be specified as a single fixed
                        number, or a range, and/or multipliers for different groups such as A=1.2. For example "
                        --symptomatic-r0 1.4 2.8 nurse=1.2" means a general R0 ranging from 1.4 to 2.8, while
                        nursed has a range from 1.4*1.2 and 2.8*1.2.
  --asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]
                        Production number of asymptomatic infectors, should be specified as a single fixed
                        number, or a range and/or multipliers for different groups
  --incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]
                        Incubation period period, should be specified as "lognormal" followed by two numbers as
                        mean and sigma, or "normal" followed by mean and sd, and/or multipliers for different
                        groups. Default to "lognormal 1.621 0.418"
  --repeats REPEATS     Number of replicates to simulate. An ID starting from 1 will be assinged to each
                        replicate and as the first columns in the log file.
  --handle-symptomatic    Keep affected individuals in the population
  --pre-quarantine [PRE_QUARANTINE [PRE_QUARANTINE ...]]
                        Days of self-quarantine before introducing infector to the group. The simulation will be
                        aborted if the infector shows symptom before introduction. If you quarantine multiple
                        people or specified named groups, you will need to append the IDs to the parameter (e.g.
                        --pre-quarantine day nurse1 nurse2
  --initial-incidence-rate [INITIAL_INCIDENCE_RATE [INITIAL_INCIDENCE_RATE ...]]
                        Incidence rate of the population (default to zero), which should be the probability that
                        any individual is currently affected with the virus (not necessarily show any symptom).
                        Multipliers can be specified to set incidence rate of for particular groups (e.g.
                        --initial-incidence-rate 0.1 docter=1.2 will set incidence rate to 0.12 for doctors).
  --initial-seroprevalence [INITIAL_SEROPREVALENCE [INITIAL_SEROPREVALENCE ...]]
                        Seroprevalence of the population (default to zero). The seroprevalence should always be
                        greater than or euqal to initial incidence rate. The difference between seroprevalence
                        and incidence rate will determine the "recovered" rate of the population. Multipliers
                        can be specified to set incidence rate of for particular groups (e.g. --initial-
                        incidence-rate 0.1 docter=1.2 will set incidence rate to 0.12 for doctors).
  --infectors [INFECTORS [INFECTORS ...]]
                        Infectees to introduce to the population, default to '0'. If you would like to introduce
                        multiple infectees to the population, or if you have named groups, you will have to
                        specify the IDs of carrier such as --infectors nurse1 nurse2. Specifying this parameter
                        without value will not introduce any infector.
  --interval INTERVAL   Interval of simulation, default to 1/24, by hour
  --logfile LOGFILE     logfile
  --prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]
                        Proportion of asymptomatic cases. You can specify a fix number, or two numbers as the
                        lower and higher CI (95%) of the proportion. Default to 0.10 to 0.40. Multipliers can be
                        specified to set proportion of asymptomatic carriers for particular groups.
  --stop-if [STOP_IF [STOP_IF ...]]
                        Condition at which the simulation will end. By default the simulation stops when all
                        individuals are affected or all infected individuals are removed. Current you can
                        specify a time after which the simulation will stop in the format of `--stop-if "t>10"'
                        (for 10 days).
  --allow-lead-time     The seed carrier will be asumptomatic but always be at the beginning of incurbation
                        time. If allow lead time is set to True, the carrier will be anywhere in his or her
                        incubation period.
  --analyze-existing-logfile
                        Analyze an existing logfile, useful for updating the summarization procedure or
                        uncaptured output.
  --plugins [PLUGINS [PLUGINS ...]]
                        One or more name of Python modules that will be used by the simulator. The module should
                        define classes derived from outbreak_simulator.plugin.BasePlugin. Plugins should be
                        provided in the format of 'module1.plugin1` where `module` is name of the module and
                        `plugin` is the name of the class. The plugins will be triggered by specific event, or
                        once at each time epoc when any other events happen.
  -j JOBS, --jobs JOBS  Number of process to use for simulation. Default to number of CPU cores.
  -s STAT_INTERVAL, --stat-interval STAT_INTERVAL
                        Interval for statistics to be calculated, default to 1. No STAT event will happen it it
                        is set to 0.

```

## Example usages

### Homogeneous and heterogeneous populations

```sh
outbreak_simulator
```

simulates the outbreak of COVID-19 in a population with 64 individuals, with one
introduced infector.

```sh
outbreak_simulator --popsize nurse=10 patient=100 --infector patient0
```

simulates a population with `10` nurses and `100` patients when the first patient
carries the virus.

### Change number of infectors

```sh
outbreak_simulator --infector 0 1 --pre-quarantine 7 0 1
```

simulates the introduction of two infectors, both after 7 days of quarantine. Here
`0` and `1` are IDs of individuals

### Changing model parameters

```sh
outbreak_simulator --prop-asym-carriers 0.10
```

runs the simulation with a fixed ratio of asymptomatic carriers.

```sh
outbreak_simulator --incubation-period normal 4 2
```

runs the simulation incubation period sampled from a normal distribution with
mean 4 and standard deviation of 2.

### Specigy group-specific parameters

Parameters `symptomatic-r0`, `asymptomatic-r0` and `incubation-period` can be
set to different values for each groups. These are achived by "multipliers",
which multiplies specified values to values drawn from the default distribution.

For example, if in a hospital environment nurses, once affected, tends to have
higher `R0` because he or she contact more patients, and on the other hand
patients are less mobile and should have lower `R0`. In some cases the nurses
are even less protected and are more susceptible. You can run a simulation
with two patients carrying the virus with the following options:

```sh
outbreak_simulator --popsize nurse=10 patient=100 \
    --symptomatic-r0 nurse=1.5 patient=0.8 \
    --asymptomatic-r0 nurse=1.5 patient=0.8 \
    --susceptibility nurse=1.2 patient=0.8 \
    --infector patient0 patient1
```
