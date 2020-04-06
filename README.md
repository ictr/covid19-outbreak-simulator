# COVID-19 Outbreak Simulator

The COVID-19 outbreak simulator simulates the outbreak of COVID-19 in a population. It was first designed to simulate
the outbreak of COVID-19 in small populations in enclosed environments, such as a FPSO (floating production storage and
offloading vessel) but it is being expanded to simulate much larger populations with dynamic parameters.

## Background

This simulator simulates the scenario in which

-   A group of individuals in a population in which everyone is susceptible
-   One virus carrier is introduced to the population, potentially after a fixed
    days of self-quarantine.
-   Infectees are by default removed from from the population (or separated, or
    quarantined, as long as he or she can no longer infect others) after they
    displayed symptoms, but options are provided to act otherwise.

The simulator simulates the epidemic of the population with the introduction
of an infector. The following questions can be answered:

1. What is the expected day and distribution for the first person to show
   symptoms?
2. How many people are expected to be removed once an outbreak starts?
3. How effective will self-quarantine before dispatch personnels to an
   enclosed environment?

The simulator uses the latest knowledge about the spread of COVID-19 and is
validated against public data. This project will be contantly updated with our
deepening knowledge on this virus.

## How to use the simulator

This simulator is programmed using Python >= 3.6 with `numpy` and `scipy`.
A conda environment is recommended. After the set up of the environment,
please run

```
pip install -r requirements.txt
```

to install required packages, and then

```
pip install covid19-outbreak-simulator
```

to install the package.

You can then use command

```
outbreak_simulator -h
```

to check the usage information.

The output file contains events that happens during the simulations.
For example, for command

```
outbreak_simulator --repeat 100 --popsize 64 --logfile result_remove_symptomatic.txt
```

You will get an output file `result_remove_symptomatic.txt` with the first few
lines resembling

```
id      time    event   target  params
1       0.00    INFECTION       0       r0=1.66,r=1,incu=7.70
1       5.73    INFECTION       62      by=0,r0=1.64,r=0,incu=6.60
1       7.70    REMOVAL 0       .
1       12.32   REMOVAL 62      .
1       12.32   END     62      popsize=62
2       0.00    INFECTION       0       r0=2.20,r=0,incu=6.36
```

which basically means

1. Individual `0` was infected at time `0.00`, who has `r0=1.66` and an incubation period of `7.70` days.
2. At day `5.73` the infector infects individual `62`, who has an incubation period of `6.60` days, but will not affect anyone else.
3. At day `7.70` the first individual showed symptom and is removed.
4. At day `12.32` individual `62` is removed.
5. The simulation ends with a remaining population size of 62.
6. Starts of the second simulation.

The columns are

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
| `INFECTION`         | Infect an non-quarantined individual, who might already been infected.                  |
| `INFECION_FAILED`   | No one left to infect                                                                   |
| `INFECTION_AVOIDED` | An infection happended during quarantine. The individual might not have showed sympton. |
| `INFECTION_IGNORED` | Infect an infected individual, which does not change anything.                          |
| `REMOVAL`           | Remove from population.                                                                 |
| `QUANTINE`          | Quarantine someone till specified time.                                                 |
| `REINTEGRATION`     | Reintroduce the quarantined individual to group.                                        |
| `ABORT`             | If the first carrier show sympton during quarantine.                                    |
| `END`               | Simulation ends.                                                                        |

Currently no built-in plot is provided but it is reasonably easy to read
the log file and generate statistics and plots using scripting languages
such as R.

## Acknowledgements

This tool has been developed and maintained by Dr. Bo Peng, associate professor at the Baylor College of Medicine, with guidance from Dr. Christopher Amos, from the [Institute for Clinical and Translational Research, Baylor College of Medicine](https://www.bcm.edu/research/office-of-research/clinical-and-translational-research). Contributions to this project are welcome. Please refer to the [LICENSE](https://github.com/ictr/outbreak_simulator/blob/master/LICENSE) file for proper use and distribution of this tool.

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage) project template.
