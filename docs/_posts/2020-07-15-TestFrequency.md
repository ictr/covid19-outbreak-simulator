---
layout: post
title:  "Testing frequency to ensure workplace safety"
author: Bo Peng
---


## Background

In a population where there is constant threat of community infection, there is a need to test everyone to ensure workplace safety.

The goal of this simulation is to determine how many in the cohort would be infected with periodic testing with specified intervals.

## Assumptions

1. Risk of community spread is `20/10,000` to `50/10,000` per day, default to 0.0022.
2. Cohort of size 10 to 40, with no virus at the beginning.
3. Test everyone in the cohor either every week, every 3 days or every 2 weeks.

## Simulations

The simulation could be performed with the following command

```
outbreak_simulator --rep 10000 --popsize {ps} --handle-symptomatic remove --stop-if 't>90' --logfile p{ps}_t{ti}.log \
        --plugin community_infection --probability 0.005 --interval 1  \
        --plugin testing --interval {ti} --proportion 1 --handle-positive remove \
        --plugin stat --at 14 90
```

where
* Simulation will last 90 days.
* Plugin `community_infection` infects everyone at a given probability at given interval
* Plugin `testing` tests everyone (`proportion=1`) and remove infected individuals.
* Plugin `stat` to output population statistics.

Here we use [`sos workflow`](https://vatlab.github.io) to execute simulations for population size (`ps`) 10, 20, 30, 40, and testing frequency (`ti`) 0 (no test at all), 3 (every 3 days), 7, and 14.


```Python3
input: for_each=[dict(ps=[10, 20, 30, 40]), dict(ti=[0, 3, 7, 14])]

task: queue='localhost'
sh: expand=True, template_name='conda', env_name='ictr'
    outbreak_simulator --rep 10000 --popsize {ps} --handle-symptomatic remove --stop-if 't>90' --logfile p{ps}_t{ti}.log \
        --plugin community_infection --probability 0.0022 --interval 1  \
        --plugin testing --interval {ti} --proportion 1 --handle-positive remove \
        --plugin stat --at 14 90

```





## Results

The log file of the simulations contains event `STAT` with population size and `INFECTION` for infections, and the `by` parameter can be used to differentiate infection within the cohort (by a certain ID) or from community.

The following table shows

1. **Average number of uninfected**: Mean remaining population size after 90 days.
2. **Std of uninfected**: Standard deviation of remaining population size.
3. **proportion of none infected**: Proportion of simulations with no infection at the end.
4. **Average number of community infection**: Average number of community infections detected.
5. **Average number of within-cohort infection**: Average number of within cohort infection.


```Python3
%preview summary.csv

import pandas as pd

def param(data, name):
    stat = data[(data['event'] == 'STAT') & (data['time'] == 90)]
    return stat.apply(lambda x: int(x['params'].split(name+'=')[1].split(',')[0]), axis=1)

def infect(data):
    infect = data[data['event'] == 'INFECTION']
    by = infect.apply(lambda x: 'by' in x['params'], axis=1)
    return infect.shape[0] - sum(by), sum(by)

with open('summary.csv', 'w') as sc:
    sc.write(','.join([
        'Cohort size',
        'Community infection rate',
        'Test frequency (0 for no test)',
        'Average number of uninfected',
        'Std of uninfected',
        'Proportion of none infected',
        'Average number of community infection',
        'Average number of within-cohort infection']) + '\n')
    for ps in [10, 20, 30, 40]:
        for ti in [0, 3, 7, 14]:
            data = pd.read_csv(f'p{ps}_t{ti}.log', sep='\t')
            es = param(data, 'n_popsize') - param(data, 'n_infected')
            pna = 100 * sum(es == ps) / 10000
            community_infect, within_infect = infect(data)
            sc.write(f'{ps}, {0.0022}, {ti}, {es.mean():.1f}, {es.std():.1f}, {pna:.2f}%, {community_infect/10000:.1f}, {within_infect/10000:.1f}\n')

```

<table  style="width:100%">
  <thead>
    <tr style="text-align: right;">
      <th>Cohort size </th>
      <th>Community infection rate </th>
      <th>Test frequency (0 for no test) </th>
      <th>Average number of uninfected </th>
      <th>Std of uninfected </th>
      <th>Proportion of none infected </th>
      <th>Average number of community infection </th>
      <th>Average number of within-cohort infection </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>10</td>
      <td>0.0022</td>
      <td>0</td>
      <td>3.7</td>
      <td>2.6</td>
      <td>1.01%</td>
      <td>2.9</td>
      <td>3.5</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.0022</td>
      <td>3</td>
      <td>5.9</td>
      <td>1.8</td>
      <td>1.14%</td>
      <td>3.6</td>
      <td>0.5</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.0022</td>
      <td>7</td>
      <td>5.2</td>
      <td>2.1</td>
      <td>1.14%</td>
      <td>3.4</td>
      <td>1.5</td>
    </tr>
    <tr>
      <td>10</td>
      <td>0.0022</td>
      <td>14</td>
      <td>4.5</td>
      <td>2.4</td>
      <td>1.15%</td>
      <td>3.1</td>
      <td>2.4</td>
    </tr>
    <tr>
      <td>20</td>
      <td>0.0022</td>
      <td>0</td>
      <td>6.2</td>
      <td>3.9</td>
      <td>0.00%</td>
      <td>5.3</td>
      <td>8.5</td>
    </tr>
    <tr>
      <td>20</td>
      <td>0.0022</td>
      <td>3</td>
      <td>11.8</td>
      <td>2.5</td>
      <td>0.02%</td>
      <td>7.1</td>
      <td>1.2</td>
    </tr>
    <tr>
      <td>20</td>
      <td>0.0022</td>
      <td>7</td>
      <td>10.1</td>
      <td>3.2</td>
      <td>0.03%</td>
      <td>6.6</td>
      <td>3.3</td>
    </tr>
    <tr>
      <td>20</td>
      <td>0.0022</td>
      <td>14</td>
      <td>8.3</td>
      <td>3.7</td>
      <td>0.00%</td>
      <td>6.1</td>
      <td>5.6</td>
    </tr>
    <tr>
      <td>30</td>
      <td>0.0022</td>
      <td>0</td>
      <td>8.5</td>
      <td>5.0</td>
      <td>0.00%</td>
      <td>7.7</td>
      <td>13.8</td>
    </tr>
    <tr>
      <td>30</td>
      <td>0.0022</td>
      <td>3</td>
      <td>17.6</td>
      <td>3.1</td>
      <td>0.00%</td>
      <td>10.6</td>
      <td>1.9</td>
    </tr>
    <tr>
      <td>30</td>
      <td>0.0022</td>
      <td>7</td>
      <td>15.0</td>
      <td>3.9</td>
      <td>0.00%</td>
      <td>9.9</td>
      <td>5.2</td>
    </tr>
    <tr>
      <td>30</td>
      <td>0.0022</td>
      <td>14</td>
      <td>12.0</td>
      <td>4.8</td>
      <td>0.00%</td>
      <td>9.0</td>
      <td>9.0</td>
    </tr>
    <tr>
      <td>40</td>
      <td>0.0022</td>
      <td>0</td>
      <td>10.8</td>
      <td>5.9</td>
      <td>0.00%</td>
      <td>10.0</td>
      <td>19.3</td>
    </tr>
    <tr>
      <td>40</td>
      <td>0.0022</td>
      <td>3</td>
      <td>23.4</td>
      <td>3.6</td>
      <td>0.00%</td>
      <td>14.2</td>
      <td>2.5</td>
    </tr>
    <tr>
      <td>40</td>
      <td>0.0022</td>
      <td>7</td>
      <td>19.9</td>
      <td>4.6</td>
      <td>0.00%</td>
      <td>13.2</td>
      <td>7.0</td>
    </tr>
    <tr>
      <td>40</td>
      <td>0.0022</td>
      <td>14</td>
      <td>15.9</td>
      <td>5.6</td>
      <td>0.00%</td>
      <td>11.9</td>
      <td>12.3</td>
    </tr>
  </tbody>
</table>


Not surprisingly, the results show that

1. Risk of infection increases with larger cohort size
2. More frequent tests will reduce the number of within-cohort infection


## Availability

This notebook is available under the `Applications` directory of the [GitHub repository](https://github.com/ictr/covid19-outbreak-simulator) of the COVID19 Outbreak Simulator. It can be executed with [`sos-papermill`](https://github.com/vatlab/sos-papermill) with the following parameters, or using a docker image `bcmictr/outbreak-simulator-notebook` as described in [here](/covid19-outbreak-simulator/docs/cli/).
