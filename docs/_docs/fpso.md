---
title: FPSO
permalink: /docs/fpso/
---


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
