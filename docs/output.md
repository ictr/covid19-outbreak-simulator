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

The log file of a typical simulation would look like the following:

```
id      time    event   target  params
5       0.00    INFECTION       0       r0=0.53,r=0,r_asym=0
5       0.00    END     64      popsize=64,prop_asym=0.276
2       0.00    INFECTION       0       r0=2.42,r=1,r_presym=1,r_sym=0,incu=5.51
2       4.10    INFECTION       62      by=0,r0=1.60,r=2,r_presym=2,r_sym=0,incu=5.84
2       5.51    SHOW_SYMPTOM    0       .
2       5.51    REMOVAL 0       popsize=63
2       9.59    INFECTION       9       by=62,r0=2.13,r=2,r_presym=2,r_sym=0,incu=3.34
2       9.84    INFECTION_IGNORED       9       by=62
2       9.94    SHOW_SYMPTOM    62      .
2       9.94    REMOVAL 62      popsize=62
2       10.76   INFECTION       30      by=9,r0=1.96,r=2,r_presym=2,r_sym=0,incu=4.85
2       11.64   INFECTION       57      by=9,r0=0.39,r=0,r_asym=0
2       12.23   INFECTION       56      by=30,r0=1.65,r=1,r_presym=1,r_sym=0,incu=4.26
2       12.93   SHOW_SYMPTOM    9       .
2       12.93   REMOVAL 9       popsize=61
2       14.37   INFECTION       6       by=30,r0=1.60,r=0,r_presym=0,r_sym=0,incu=2.63
2       15.61   SHOW_SYMPTOM    30      .
2       15.61   REMOVAL 30      popsize=60
2       16.37   INFECTION       1       by=56,r0=1.57,r=1,r_presym=1,r_sym=0,incu=5.14
2       16.49   SHOW_SYMPTOM    56      .
2       16.49   REMOVAL 56      popsize=59
2       16.99   SHOW_SYMPTOM    6       .
2       16.99   REMOVAL 6       popsize=58
2       18.42   INFECTION       8       by=1,r0=2.45,r=1,r_presym=1,r_sym=0,incu=3.74
2       20.35   INFECTION       44      by=8,r0=2.37,r=1,r_presym=1,r_sym=0,incu=3.92
2       21.51   SHOW_SYMPTOM    1       .
2       21.51   REMOVAL 1       popsize=57
2       22.16   SHOW_SYMPTOM    8       .
2       22.16   REMOVAL 8       popsize=56
2       22.62   INFECTION       42      by=44,r0=1.49,r=0,r_presym=0,r_sym=0,incu=4.30
2       24.27   SHOW_SYMPTOM    44      .
2       24.27   REMOVAL 44      popsize=55
2       26.92   SHOW_SYMPTOM    42      .
2       26.92   REMOVAL 42      popsize=54
2       26.92   END     54      popsize=54,prop_asym=0.216
1       0.00    INFECTION       0       r0=2.00,r=2,r_presym=2,r_sym=0,incu=4.19
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
| `pre_quarantine`                      | If the first carrier is pre-quarantined, if so, for how many days                                                                                                                         |
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
