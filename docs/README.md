

.. image:: https://img.shields.io/pypi/v/covid19-outbreak-simulator.svg
   :target: https://pypi.python.org/pypi/covid19-outbreak-simulator
   :alt: PyPI


.. image:: https://img.shields.io/pypi/pyversions/covid19-outbreak-simulator.svg
   :target: https://pypi.python.org/pypi/covid19-outbreak-simulator
   :alt: PyPI version


.. image:: https://readthedocs.org/projects/covid19-outbreak-simulator/badge/?version=latest
   :target: https://covid19-outbreak-simulator.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


.. image:: https://travis-ci.org/ictr/covid19-outbreak-simulator.svg?branch=master
   :target: https://travis-ci.org/ictr/covid19-outbreak-simulator
   :alt: Build Status


COVID-19 Outbreak Simulator
===========================

The COVID-19 outbreak simulator simulates the outbreak of COVID-19 in a population. It was first designed to simulate
the outbreak of COVID-19 in small populations in enclosed environments, such as a FPSO (floating production storage and
offloading vessel) but has since been expanded to simulate much larger populations with dynamic parameters.

This README file contains all essential information but you can also visit our `documentation <https://covid19-outbreak-simulator.readthedocs.io/en/latest/?badge=latest>`_ for more details.

Background
----------

This simulator simulates the scenario in which


* A group of individuals in a population in which everyone is susceptible.
* The population can be divided into multiple subgroups with different parameters.
* One or more virus carriers are introduced to the population, potentially after a fixed
  days of self-quarantine.
* Infectees are by default removed from from the population (or separated, or
  quarantined, as long as he or she can no longer infect others) after they
  displayed symptoms, but options are provided to act otherwise.

The simulator simulates the epidemic of the population with the introduction of
infectors. Detailed statistics are captured from the simulations to answer questions
such as:


#. What is the expected day and distribution for the first person to show
   symptoms?
#. How many people are expected to be removed once an outbreak starts?
#. How effective will self-quarantine before dispatch personnels to an
   enclosed environment?

The simulator uses the latest knowledge about the spread of COVID-19 and is
validated against public data. This project will be contantly updated with our
deepening knowledge on this virus.

Modeling the outbreak of COVID-19
---------------------------------

We developed multiple statistical models to model the incubation time, serial interval,
generation time, proportion of asymptomatic transmissions, using results from
multiple publications. We validated the models with empirical data to ensure they
generate, for example, correct distributions of serial intervals and proporitons
of asymptomatic, pre-symptomatic, and symptomatic cases.

The statistical models and related references are available at


* `Statistical models of COVID-19 outbreaks (Version 1) <https://bioworkflows.com/ictr/COVID19-outbreak-simulator-model/1>`_
* `Statistical models of COVID-19 outbreaks (Version 2) <https://bioworkflows.com/ictr/COVID19-outbreak-simulator-model/2>`_

The models will continuously be updated as we learn more about the virus.
