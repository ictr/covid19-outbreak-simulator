---
title: Installation
permalink: /docs/installation/
---

## Using Docker

If you have docker, you can execute COVID19 Outbreak Simulator directly without installing
it locally. Please see [Running COVID19 Outbreak Simulator](/docs/cli/) for details.

## Local installation

This simulator is programmed using Python >= 3.6 with `numpy` and `scipy`. With a Python 3.6+
environment, you can install the simulator with command

```
$ pip install covid19-outbreak-simulator
```

You can then use command

```
$ outbreak_simulator -h
```

to check if you have successfully installed the simulator, and the usage information of the basic simulator,


## Installation from source (for developers)


The sources for COVID-19 Outbreak Simulator can be downloaded from the [`Github repo`](https://github.com/ictr/covid19-outbreak-simulator). After cloning the repo to a local directory with command

```
$ git clone git://github.com/ictr/covid19-outbreak-simulator
```

you can install it with:

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