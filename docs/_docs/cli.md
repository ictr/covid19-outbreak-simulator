---
title: Runing the simulator
permalink: /docs/cli/
---

## Running in Docker

If you have docker installed, you can execute the outbreak simulator directly with command

```shell
$ docker run -it -v `pwd`:/home/bcmictr bcmictr/outbreak_simulator [OPTIONS]
```
Here option `-v` is used to map your current directory to the working directory of
the container so that all output will be written to the current directory.

To make the command easier to use and be consistent with a local installation, you can
create an alias

```shell
$ alias outbreak_simulator="docker run -it -v `pwd`:/home/bcmictr bcmictr/outbreak_simulator"
```

so that you can execute the docker image directly with command `outbreak_simulator`.

## Running the application notebook

We record [applications of the outbreak simulator](/covid19-outbreak-simulator/applications/TestFrequency/)
in [SoS notebooks](https://vatlab.github.io/sos-docs/) which is an extension of [Jupyter notebooks](https://jupyter.org/) that allows
the use of multiple kernels (e.g. `Python` and `R`) in the same reports.

If you have a Jupyter notebook with SoS kernel installed, you can open the notebooks,
modify, and run them. Otherwise, you can start a notebook server using

```shell
$ docker run -v `pwd`:/home/jovyan -p 8888:8888 bcmictr/outbreak_simulator_notebook
```

You should see a URL from the output of the command similar to the following

```
    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://localhost:8888/?token=754a646651c82657725be887a1a2579ab69a702ba80ae4b3
```

You can then enter the URL in the log message to a browser and start working with a complete
SoS environment and the simulator installed.

If you simply want to execute the notebook, you can execute them with command

```
$ docker run -v `pwd`:/home/jovyan --entrypoint sos bcmictr/outbreak_simulator_notebook \
  convert [NOTEBOOK] [OUTPUT] [OPTIONS] --execute [PARAMETERS]
```

The command executes the same docker image `bcmictr/outbreak_simulator_notebook`, however, instead of
starting a notebook server, it overrides the `entrypoint` to execute command

```
sos convert [NOTEBOOK] [OUTPUT] [OPTIONS] [--execute [PARAMETERS]]
```

from the container. Here

* `NOTEBOOK` is the notebook you would like to execute or convert
* `OUTPUT` is the output notebook, or HTML file if you would like to convert the generated notebook
  to `HTML` format.
* `--execute` tells command `sos execute` to execute the notebook with
  [`sos-papermill`](https://github.com/vatlab/sos-papermill)
* `OPTIONS` are options to command `sos execute`, which is usually `--template sos-report-only`
  or `--template sos-report-toc-v2` to specify the style of the output HTML file.
* `PARAMETERS` are [papermill parameters](https://papermill.readthedocs.io/en/latest/usage-execute.html)
  if the notebook accept parameters. The parameters should be specified as `key=value` pairs.

For example, if you would like to rerun the notebook `Enclosed.ipynb` with a larger population
size, you can

* Download FPSO.ipynb from the `applications` folder of [our github repository](https://github.com/ictr/covid19-outbreak-simulator/]
  or checkout the entire repository with command

  ```
  git clone https://github.com/ictr/covid19-outbreak-simulator.git
  ```

* Execute the notebook and optionally convert it to HTML format.

  ```
  $ cd covid19-outbreak-simulator/applications
  $ docker run -v `pwd`:/home/jovyan --entrypoint sos \
    bcmictr/outbreak_simulator_notebook convert \
    Enclosed.ipynb Enclosed_100.html --template sos-report-only \
    --execute popsize=100
  ```

As you can see, the `--execute` option essentially provides a higher level command line
interface for `COVID19 Outbreak Simulator` for particular types of applications.


## Running the simulator locally

If you have installed COVID19 Outbreak Simulator locally, or have created an alias
for the docker command, you can get a list of options with option `-h` as follows:

```
$  outbreak_simulator -h

usage: outbreak_simulator [-h] [--popsize POPSIZE [POPSIZE ...]]
                          [--susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]]
                          [--symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]]
                          [--asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]]
                          [--incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]]
                          [--repeats REPEATS]
                          [--handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]]
                          [--infectors [INFECTORS [INFECTORS ...]]]
                          [--interval INTERVAL] [--logfile LOGFILE]
                          [--prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]]
                          [--stop-if [STOP_IF [STOP_IF ...]]]
                          [--leadtime LEADTIME] [--plugin ...] [-j JOBS]

optional arguments:
  -h, --help            show this help message and exit
  --popsize POPSIZE [POPSIZE ...]
                        Size of the population, including the infector that
                        will be introduced at the beginning of the simulation.
                        It should be specified as a single number, or a serial
                        of name=size values for different groups. For example
                        "--popsize nurse=10 patient=100". The names will be
                        used for setting group specific parameters. The IDs of
                        these individuals will be nurse0, nurse1 etc.
  --susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]
                        Weight of susceptibility. The default value is 1,
                        meaning everyone is equally susceptible. With options
                        such as "--susceptibility nurse=1.2 patients=0.8" you
                        can give weights to different groups of people so that
                        they have higher or lower probabilities to be
                        infected.
  --symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]
                        Production number of symptomatic infectors, should be
                        specified as a single fixed number, or a range, and/or
                        multipliers for different groups such as A=1.2. For
                        example "--symptomatic-r0 1.4 2.8 nurse=1.2" means a
                        general R0 ranging from 1.4 to 2.8, while nursed has a
                        range from 1.4*1.2 and 2.8*1.2.
  --asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]
                        Production number of asymptomatic infectors, should be
                        specified as a single fixed number, or a range and/or
                        multipliers for different groups
  --incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]
                        Incubation period period, should be specified as
                        "lognormal" followed by two numbers as mean and sigma,
                        or "normal" followed by mean and sd, and/or
                        multipliers for different groups. Default to
                        "lognormal 1.621 0.418"
  --repeats REPEATS     Number of replicates to simulate. An ID starting from
                        1 will be assinged to each replicate and as the first
                        columns in the log file.
  --handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]
                        How to handle individuals who show symptom, which
                        should be "keep" (stay in population), "remove"
                        (remove from population), and "quarantine" (put aside
                        until it recovers). all options can be followed by a
                        "proportion", and quarantine can be specified as
                        "quarantine_7" etc to specify duration of quarantine.
                        Default to "remove", meaning all symptomatic cases
                        will be removed from population.
  --infectors [INFECTORS [INFECTORS ...]]
                        Infectees to introduce to the population. If you would
                        like to introduce multiple infectees to the
                        population, or if you have named groups, you will have
                        to specify the IDs of carrier such as --infectors
                        nurse1 nurse2.
  --interval INTERVAL   Interval of simulation, default to 1/24, by hour
  --logfile LOGFILE     logfile
  --prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]
                        Proportion of asymptomatic cases. You can specify a
                        fix number, or two numbers as the lower and higher CI
                        (95%) of the proportion. Default to 0.10 to 0.40.
                        Multipliers can be specified to set proportion of
                        asymptomatic carriers for particular groups.
  --stop-if [STOP_IF [STOP_IF ...]]
                        Condition at which the simulation will end. By default
                        the simulation stops when all individuals are affected
                        or all infected individuals are removed. Current you
                        can specify a time after which the simulation will
                        stop in the format of `--stop-if "t>10"' (for 10
                        days).
  --leadtime LEADTIME   With "leadtime" infections are assumed to happen
                        before the simulation. This option can be a fixed
                        positive number `t` when the infection happens `t`
                        days before current time. If can also be set to 'any'
                        for which the carrier can be any time during its
                        course of infection, or `asymptomatic` for which the
                        leadtime is adjust so that the carrier does not show
                        any symptom at the time point (in incubation period
                        for symptomatic case). All events triggered before
                        current time are ignored.
  --plugin ...          One or more of "--plugin MODULE.PLUGIN [args]" to
                        specify one or more plugins. FLUGIN will be assumed to
                        be MODULE name if left unspecified. Each plugin has
                        its own parser and can parse its own args.
  -j JOBS, --jobs JOBS  Number of process to use for simulation. Default to
                        number of CPU cores.
```

## Specification for subpopulation-specific parameters

`outbreak_simulator` allows the simulation of multiple subpopulations using
parameter `--popsize`. For example,

```
--popsize A=100 B=200
```

specifies two subpopulations `A` and `B` with sizes `100` and `200` respectively.

Subpopulations can have their own parameters (e.g. `--susceptibility`) and they
are specified by `multipliers` in the format of

```
--param [default values] name=multiplier
```

For example,

```
--symptomatic-r0 1.5 A=1.2 B=0.8
```
specifies individuals in subpopulation `A` with symptomatic r0 `1.5*1.2` and
`1.5*0.8` in subpopulation `B`. `1.5` will be used for unspecified subpopulations.

If you would like to specify value for each subpopulation, you can use

```
--symptomatic-r0 1 A=1.2 B=0.8
```

but this would not work for parameters that receive more than one values when
the multiplier is applied to more than one values.


## Example commands

### A small population with the introduction of one carrier

Assuming that there is no asymptomatic carriers, you can introduce one infected
carrier to a population of size 64, and observe the development of the outbreak.

```sh
$ outbreak_simulator --infector 0  --rep 10000 --prop-asym-carriers 0 \
  --logfile simu_remove_symptomatic.log
```

You can set the proportion of asymptomatic cases to be from 20% to 60% (vary from
replicate to replicate, but the same probability of asymptomatic cases within a
simulation) by setting parameters `prop-asym-carriers`:

```sh
$ outbreak_simulator --infector 0  --rep 10000 --prop-asym-carriers .20 .60 \
    --logfile simu_with_asymptomatic.log
```

You can quarantine the carrier for 7 days, but here you need to use a plugin that
applies the policy at time 0

```sh
$ outbreak_simulator --infector 0  --rep 10000 --logfile simu_quarantine_7.log \
  --plugin quarantine --at 0 --duration 7
```

or you can try quarantine for 14 days...

```sh
$ outbreak_simulator --infector 0  --rep 10000 --logfile simu_quarantine_15.log \
  --plugin quarantine --at 0 --duration 14
```

The above simulation assumes that the carriers are infected right before quarantine, which is not really
realistic. The following add some `leadtime` and simulate scenarios that people enters quarantine
as long as they do not show symptom.

```
$ outbreak_simulator --infector 0  --rep 10000 --leadtime asymptomatic \
  --logfile simu_leadtime_quarantine_7.log -j 1 \
  --plugin quarantine --at 0 --duration 7
```

###  A larger population

Assuming a population of size `34993` with `85` total cases (in the past few months). Assuming that
every case has 4 unreported (asymptomatic etc) cases, there has been `85*5` cases so the population has
a seroprevalence of `85*5/34993=0.01214`. Assuming 8 weeks outbreak duration and 2 week active window,
1/4 cases would be "active", so the current incidence rate would be `85*5/4 / 34993 = 0.003036`.

Assuming that 75% of all symptomatic cases will be quarantined (hospitalized), the rest would be able to
infect others. We simulate only 1 replicate because the population size is large. The command to simulate this population is as follows:

```sh
$ outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
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
$ outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 0.75 \
    --logfile pop_quarantine_.75.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_quarantine_.75.txt
```

You can change the R0 value at day 20 to reflect perhaps a government warning that increases
social distancing

```sh
$ outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
    --logfile pop_distancing_at_20.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_distancing_at_20.txt \
    --plugin setparam --symptomatic-r0 1.2 2.4 --at 20
```

### Heterogeneous situation

Now, let us assume that we have a population with two subpopulations `A` and `B`, be they workers and guest, doctors and patients. Now let us assume that subpopulation `A` is more
susceptible (more contact with others), and more infectious. Let us also assume that
there is a intermediate inflow of `A` to the population, half of them would be carriers.
This simulation can be written as

```sh
$ outbreak_simulator --popsize A=2000 B=500 --rep 10 --handle-symptomatic quarantine_14 1 \
  --susceptibility B=0.8 --symptomatic-r0 A=1.2 B=0.8 --logfile hetero.log \
  --stop-if 't>40' \
  --plugin stat --interval 1 \
  --plugin insert A=5 --prop-of-infected 0.5 --interval 1 \
  > hetero.txt

```

because the continuous injection of cases, the outbreak will not stop by itself so we have
to use `--stop-at 't>40'` to set the duration of the simulation.

Parameters `symptomatic-r0`, `asymptomatic-r0` and `incubation-period` can be
set to different values for each groups. These are achived by "multipliers",
which multiplies specified values to values drawn from the default distribution.

For example, if in a hospital environment nurses, once affected, tends to have
higher `R0` because he or she contact more patients, and on the other hand
patients are less mobile and should have lower `R0`. In some cases the nurses
are even less protected and are more susceptible. You can run a simulation
with two patients carrying the virus with the following options:

```
$ outbreak_simulator --popsize nurse=10 patient=100 \
    --symptomatic-r0 nurse=1.5 patient=0.8 \
    --asymptomatic-r0 nurse=1.5 patient=0.8 \
    --susceptibility nurse=0.8 patient=1 \
    --infector patient0 patient1
```