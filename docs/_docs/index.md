---
title: COVID-19 Outbreak Simulator
permalink: /docs/home/
redirect_from: /docs/index.html
---


This COVID-19 outbreak simulator is a popolation-based stochastic simulator that simulates the outbreak of COVID-19
in a population, subject to changes of population (addition and removal of individuals), model (e.g. change of production number
to mimic varying level of social distancing), and various preventative (quarantine, testing) and post-outbreak
opeartions (quarantine, testing, removal of symptomatic individuals etc). With realistic modeling of the course of
infection of a large number of individuals in the population,
this simulator can be used to simulate a variety of scenarios, and answer questions such as

1. What is the expected day and distribution for the first person to show symptoms?
2. How many people are expected to be removed once an outbreak starts?
3. How effective will self-quarantine be? Is 7-day quarantine good enough? How about 14 days?
4. How frequently should we test everyone in a high-risk environment?


## Command line and notebook interfaces

At the low level, this simulator provides

* A core simulator that simulates the dynamic of populations over time.
* A plugin system that provides multiple plugins for different applications.
* Multiple scripts and tools to analyze executed simulations and generate reports.

At a higher level, this simulator provides

* Notebooks that simulate different scenarios for different applications and analyze results.
* Utility to execute the notebooks with different parameters to create your own reports

## Contact us

The development of this simulator was largely driven by requests from various industrial, governmental, and academic collaborators. Please feel free to report any bug to our [issue tracker](https://github.com/ictr/covid19-outbreak-simulator), [contribute plugins or analysis scripts](http://127.0.0.1:4000/covid19-outbreak-simulator/docs/contributing/), or [contact us](https://github.com/ictr/covid19-outbreak-simulator/issues) if you would like to simulate any particular scenarios.
