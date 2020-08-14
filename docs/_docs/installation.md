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


You can then use command

```
outbreak_simulator -h
```

to check if you have successfully installed the simulator, and the usage information of the basic simulator,

```
outbreak_simualtor --plugin -h
```
to get decription of common parameters for plugins, and

```
outbreak_simulator --plugin plugin_name -h
```
to get the usage information of a particular plugin.



## Installation from source (for developers)


The sources for COVID-19 Outbreak Simulator can be downloaded from the `Github repo`_.

You can either clone the public repository:


```
    $ git clone git://github.com/ictr/covid19-outbreak-simulator
```


Once you have a copy of the source, you can install it with:


```
    $ pip install
```

The command

```
    $ pip install -e .
```

is very much recommended because it installs the simulator "in place" in the sense
that any change you make to the source code would be reflected when you run the
simualtor and there is no need to install again.