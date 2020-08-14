[![PyPI](https://img.shields.io/pypi/v/covid19-outbreak-simulator.svg)](https://pypi.python.org/pypi/covid19-outbreak-simulator)
[![PyPI version](https://img.shields.io/pypi/pyversions/covid19-outbreak-simulator.svg)](https://pypi.python.org/pypi/covid19-outbreak-simulator)
[![Documentation Status](https://readthedocs.org/projects/covid19-outbreak-simulator/badge/?version=latest)](https://covid19-outbreak-simulator.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/ictr/covid19-outbreak-simulator.svg?branch=master)](https://travis-ci.org/ictr/covid19-outbreak-simulator)
[![Coverage Status](https://coveralls.io/repos/github/ictr/covid19-outbreak-simulator/badge.svg?branch=master&service=github)](https://coveralls.io/github/ictr/covid19-outbreak-simulator?branch=master)
[![Documentation Status](https://readthedocs.org/projects/covid19-outbreak-simulator/badge/?version=latest)](https://covid19-outbreak-simulator.readthedocs.io/en/latest/?badge=latest)



The COVID-19 outbreak simulator simulates is an individual based stochastic simulator that simulates the outbreak of COVID-19
in a population, subject to changes of population (addition and removal of individuals), model (e.g. production number
to mimic varying level of social distancing), and various preventative (quarantine, testing) and post-outbreak
opeartions (quarantine, testing, removal of symptomatic individuals etc). With realistic modeling of the course of
infection of each individual, this simulator can be used to simulate a variety of scenarios for risk assessment and
continuity planning.

The simulator provides

* At the low level
  * A core simulator that simulates the dynamic of populations over time.
  * A plugin system that provides multiple plugins for different applications.
  * Multiple scripts and tools to analyze executed simulations and generate reports.

* At a higher level
  * Notebooks that apply the simulator for different applications, with command
    used and analysis of results.
  * Utility to execute the notebooks with different parameters, which can be considered
    a higher level interface for the simulator.

This README file contains all essential

Please feel free to [contact us](https://github.com/ictr/covid19-outbreak-simulator/issues) if you would like to simulate any particular environment.



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
