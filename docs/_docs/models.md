---
title: Simulation Method
permalink: /docs/models/
---


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
