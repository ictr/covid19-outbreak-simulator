---
title: Installation
permalink: /docs/installation/
---


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