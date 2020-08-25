---
layout: post
title:  "Social distancing and sampling effect"
author: Bo Peng
---


## Background

This example tries to simulate a decent sized population with

1. Effect of increased social distancing following government guidelines.
2. Estimation of population incidence rate and seroprevalence through sampling.

## Assumptions

1. The population has size `popsize` in which everyone is equally susceptible.
2. Initial seroprevalence is `initial_seroprevalence`, with `initial_incidence_rate` active cases.
3. Incomplete social distancing in that while 80% of symptomatic cases are quarantined for 14-days, the rest of 20% of symptomatic cases are not, perhaps due to the mildness of symptoms.
4. Starting from day 15, stronger social distancing was adviced, which reduces the effective production number of everyone by `distancing`.
5. Although sampling in real world would be far less frequent, we sample `sample_size` individuals from the population every day to estimate the true incidence and seroprevalence of the population.

## Simulation of sampling


```Python3
# this is a papermill parameter cell.

# 50k population size
popsize = 50000
# 0.6% reported cases
initial_incidence_rate = 0.006
# assuming that seoprevalence is 5 times higher than incidence rate
initial_seroprevalence = 0.03
# effect of social distancing
distancing = 0.5
# 1% population size
sample_size = 500
```

This scenario can be simulated with the following command:

```
outbreak_simulator --popsize {popsize} --handle-symptomatic quarantine_14 0.8 --stop-if 't>45' --logfile distancing.log \
    --plugin init --at 0 --seroprevalence {seroprevalance} --incidence-rate {incidence_rate} --leadtime any \
    --plugin sample --interval 1 --size {sample_size} \
    --plugin stat --interval 1 \
    --plugin setparam --at 15 --symptomatic-r0 {1.4 * distancing} {2.8 * distancing} --asymptomatic-r0 {0.28 * distancing} {0.56 * distancing} \
    > distancing.txt
```

where plugins `init` and `sample` are used to initialize and sample from the population, `setparam` is used to set $R_0$ for sympatomatic and asymptomatic cases at day 15, and `stat` is to report true population incidence rate and seroprevalence every day.


```Bash
%expand
outbreak_simulator --popsize {popsize} --handle-symptomatic quarantine_14 0.8 \
    --stop-if 't>45' --repeat 10 --logfile distancing.log \
    --plugin init --at 0 --leadtime any --seroprevalence {initial_seroprevalence} --incidence-rate {initial_incidence_rate} \
    --plugin setparam --at 15 --symptomatic-r0 {1.4 * distancing} {2.8 * distancing} --asymptomatic-r0 {0.28 * distancing} {0.56 * distancing} \
    --plugin sample --interval 1 --size {sample_size} \
    --plugin stat --interval 1 \
    > distancing.txt
```

    100%|███████████████████████████████████████████| 10/10 [01:08<00:00,  6.81s/it]



## Results

Although a large number of statistics such as number of affected, recovered, seroprevalence are reported, we extract the following statistics from the output of the simulations (`distancing.txt`) for this report:

1. `incidence_rate_0.00` to `incidence_rate_45.00` as population incidence rate for 10 replicate simulations.
2. `sample_incidence_rate_0.00` to `sample_incidence_rate_45.00` as sample incidence rate for 10 replicate simulations.


```Python3
import pandas as pd
def get_seq(filename, field_name):
    result = {}
    with open(filename) as stat:
        for line in stat:
            if line.startswith(field_name):
                key, value = line.strip().split('\t')
                t = int(key[len(field_name)+1:].split('.')[0])
                if ':' in value:
                    value = eval('{' + value + '}')
                else:
                    value = {idx+1:value for idx, value in enumerate(eval(value))}
                result[t] = value

    return pd.DataFrame(result).transpose()[[x for x in range(1, 11)]]
```


```Python3
%preview incidence_rate
incidence_rate = get_seq('distancing.txt', 'incidence_rate')
sample_incidence_rate = get_seq('distancing.txt', 'sample_incidence_rate')
```


<div class="sos_hint">> incidence_rate: DataFrame of shape (46, 10)</div>




    <div class='dataframe_container' style="max-height:400px">
    <input type="text" class='dataframe_input' id="search_w7a5t6w4" onkeyup="filterDataFrame('w7a5t6w4')" placeholder="Search for names..">
    <table border="1" id="dataframe_w7a5t6w4" class="sos_dataframe dataframe">
  <thead>
    <tr style="text-align: right;">
      <th> &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 0, 'alphabetic')"></th>
      <th>1 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 1, 'numeric')"></th>
      <th>2 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 2, 'numeric')"></th>
      <th>3 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 3, 'numeric')"></th>
      <th>4 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 4, 'numeric')"></th>
      <th>5 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 5, 'numeric')"></th>
      <th>6 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 6, 'numeric')"></th>
      <th>7 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 7, 'numeric')"></th>
      <th>8 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 8, 'numeric')"></th>
      <th>9 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 9, 'numeric')"></th>
      <th>10 &nbsp; <i class="fa fa-sort" style="color:lightgray" onclick="sortDataFrame('w7a5t6w4', 10, 'numeric')"></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0060</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.0056</td>
      <td>0.0057</td>
      <td>0.0055</td>
      <td>0.0058</td>
      <td>0.0058</td>
      <td>0.0057</td>
      <td>0.0059</td>
      <td>0.0057</td>
      <td>0.0059</td>
      <td>0.0057</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.0056</td>
      <td>0.0055</td>
      <td>0.0053</td>
      <td>0.0057</td>
      <td>0.0058</td>
      <td>0.0055</td>
      <td>0.0059</td>
      <td>0.0058</td>
      <td>0.0058</td>
      <td>0.0056</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.0057</td>
      <td>0.0054</td>
      <td>0.0054</td>
      <td>0.0055</td>
      <td>0.0058</td>
      <td>0.0057</td>
      <td>0.0060</td>
      <td>0.0058</td>
      <td>0.0058</td>
      <td>0.0057</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.0055</td>
      <td>0.0056</td>
      <td>0.0053</td>
      <td>0.0052</td>
      <td>0.0057</td>
      <td>0.0059</td>
      <td>0.0061</td>
      <td>0.0057</td>
      <td>0.0060</td>
      <td>0.0059</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0.0059</td>
      <td>0.0055</td>
      <td>0.0053</td>
      <td>0.0050</td>
      <td>0.0058</td>
      <td>0.0060</td>
      <td>0.0060</td>
      <td>0.0058</td>
      <td>0.0061</td>
      <td>0.0060</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0.0059</td>
      <td>0.0057</td>
      <td>0.0059</td>
      <td>0.0054</td>
      <td>0.0058</td>
      <td>0.0060</td>
      <td>0.0063</td>
      <td>0.0061</td>
      <td>0.0063</td>
      <td>0.0065</td>
    </tr>
    <tr>
      <th>7</th>
      <td>0.0062</td>
      <td>0.0057</td>
      <td>0.0063</td>
      <td>0.0052</td>
      <td>0.0058</td>
      <td>0.0064</td>
      <td>0.0066</td>
      <td>0.0060</td>
      <td>0.0064</td>
      <td>0.0068</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0.0067</td>
      <td>0.0058</td>
      <td>0.0066</td>
      <td>0.0055</td>
      <td>0.0060</td>
      <td>0.0065</td>
      <td>0.0069</td>
      <td>0.0063</td>
      <td>0.0067</td>
      <td>0.0072</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0.0071</td>
      <td>0.0059</td>
      <td>0.0071</td>
      <td>0.0055</td>
      <td>0.0059</td>
      <td>0.0067</td>
      <td>0.0072</td>
      <td>0.0065</td>
      <td>0.0069</td>
      <td>0.0077</td>
    </tr>
    <tr>
      <th>10</th>
      <td>0.0072</td>
      <td>0.0062</td>
      <td>0.0077</td>
      <td>0.0056</td>
      <td>0.0061</td>
      <td>0.0068</td>
      <td>0.0077</td>
      <td>0.0065</td>
      <td>0.0072</td>
      <td>0.0080</td>
    </tr>
    <tr>
      <th>11</th>
      <td>0.0074</td>
      <td>0.0064</td>
      <td>0.0086</td>
      <td>0.0058</td>
      <td>0.0062</td>
      <td>0.0071</td>
      <td>0.0082</td>
      <td>0.0066</td>
      <td>0.0080</td>
      <td>0.0084</td>
    </tr>
    <tr>
      <th>12</th>
      <td>0.0076</td>
      <td>0.0067</td>
      <td>0.0096</td>
      <td>0.0063</td>
      <td>0.0065</td>
      <td>0.0075</td>
      <td>0.0086</td>
      <td>0.0067</td>
      <td>0.0082</td>
      <td>0.0090</td>
    </tr>
    <tr>
      <th>13</th>
      <td>0.0082</td>
      <td>0.0070</td>
      <td>0.0106</td>
      <td>0.0069</td>
      <td>0.0067</td>
      <td>0.0080</td>
      <td>0.0091</td>
      <td>0.0070</td>
      <td>0.0085</td>
      <td>0.0096</td>
    </tr>
    <tr>
      <th>14</th>
      <td>0.0087</td>
      <td>0.0072</td>
      <td>0.0116</td>
      <td>0.0074</td>
      <td>0.0071</td>
      <td>0.0085</td>
      <td>0.0097</td>
      <td>0.0073</td>
      <td>0.0089</td>
      <td>0.0101</td>
    </tr>
    <tr>
      <th>15</th>
      <td>0.0091</td>
      <td>0.0074</td>
      <td>0.0125</td>
      <td>0.0077</td>
      <td>0.0073</td>
      <td>0.0089</td>
      <td>0.0098</td>
      <td>0.0076</td>
      <td>0.0091</td>
      <td>0.0103</td>
    </tr>
    <tr>
      <th>16</th>
      <td>0.0094</td>
      <td>0.0077</td>
      <td>0.0133</td>
      <td>0.0079</td>
      <td>0.0072</td>
      <td>0.0089</td>
      <td>0.0100</td>
      <td>0.0078</td>
      <td>0.0093</td>
      <td>0.0106</td>
    </tr>
    <tr>
      <th>17</th>
      <td>0.0094</td>
      <td>0.0078</td>
      <td>0.0142</td>
      <td>0.0085</td>
      <td>0.0072</td>
      <td>0.0093</td>
      <td>0.0103</td>
      <td>0.0076</td>
      <td>0.0093</td>
      <td>0.0110</td>
    </tr>
    <tr>
      <th>18</th>
      <td>0.0096</td>
      <td>0.0080</td>
      <td>0.0148</td>
      <td>0.0086</td>
      <td>0.0071</td>
      <td>0.0096</td>
      <td>0.0103</td>
      <td>0.0076</td>
      <td>0.0094</td>
      <td>0.0110</td>
    </tr>
    <tr>
      <th>19</th>
      <td>0.0097</td>
      <td>0.0080</td>
      <td>0.0154</td>
      <td>0.0084</td>
      <td>0.0070</td>
      <td>0.0095</td>
      <td>0.0103</td>
      <td>0.0073</td>
      <td>0.0093</td>
      <td>0.0107</td>
    </tr>
    <tr>
      <th>20</th>
      <td>0.0095</td>
      <td>0.0083</td>
      <td>0.0158</td>
      <td>0.0082</td>
      <td>0.0068</td>
      <td>0.0095</td>
      <td>0.0100</td>
      <td>0.0070</td>
      <td>0.0091</td>
      <td>0.0107</td>
    </tr>
    <tr>
      <th>21</th>
      <td>0.0092</td>
      <td>0.0080</td>
      <td>0.0159</td>
      <td>0.0079</td>
      <td>0.0064</td>
      <td>0.0093</td>
      <td>0.0097</td>
      <td>0.0067</td>
      <td>0.0087</td>
      <td>0.0102</td>
    </tr>
    <tr>
      <th>22</th>
      <td>0.0091</td>
      <td>0.0074</td>
      <td>0.0154</td>
      <td>0.0078</td>
      <td>0.0062</td>
      <td>0.0090</td>
      <td>0.0095</td>
      <td>0.0063</td>
      <td>0.0084</td>
      <td>0.0099</td>
    </tr>
    <tr>
      <th>23</th>
      <td>0.0087</td>
      <td>0.0071</td>
      <td>0.0152</td>
      <td>0.0076</td>
      <td>0.0058</td>
      <td>0.0087</td>
      <td>0.0089</td>
      <td>0.0060</td>
      <td>0.0081</td>
      <td>0.0090</td>
    </tr>
    <tr>
      <th>24</th>
      <td>0.0086</td>
      <td>0.0070</td>
      <td>0.0148</td>
      <td>0.0071</td>
      <td>0.0054</td>
      <td>0.0080</td>
      <td>0.0083</td>
      <td>0.0056</td>
      <td>0.0079</td>
      <td>0.0085</td>
    </tr>
    <tr>
      <th>25</th>
      <td>0.0080</td>
      <td>0.0066</td>
      <td>0.0140</td>
      <td>0.0067</td>
      <td>0.0050</td>
      <td>0.0074</td>
      <td>0.0077</td>
      <td>0.0050</td>
      <td>0.0074</td>
      <td>0.0079</td>
    </tr>
    <tr>
      <th>26</th>
      <td>0.0076</td>
      <td>0.0062</td>
      <td>0.0133</td>
      <td>0.0063</td>
      <td>0.0044</td>
      <td>0.0068</td>
      <td>0.0070</td>
      <td>0.0044</td>
      <td>0.0067</td>
      <td>0.0073</td>
    </tr>
    <tr>
      <th>27</th>
      <td>0.0070</td>
      <td>0.0056</td>
      <td>0.0126</td>
      <td>0.0057</td>
      <td>0.0039</td>
      <td>0.0062</td>
      <td>0.0066</td>
      <td>0.0038</td>
      <td>0.0063</td>
      <td>0.0067</td>
    </tr>
    <tr>
      <th>28</th>
      <td>0.0063</td>
      <td>0.0052</td>
      <td>0.0118</td>
      <td>0.0051</td>
      <td>0.0035</td>
      <td>0.0055</td>
      <td>0.0061</td>
      <td>0.0034</td>
      <td>0.0057</td>
      <td>0.0059</td>
    </tr>
    <tr>
      <th>29</th>
      <td>0.0058</td>
      <td>0.0047</td>
      <td>0.0107</td>
      <td>0.0047</td>
      <td>0.0032</td>
      <td>0.0047</td>
      <td>0.0054</td>
      <td>0.0030</td>
      <td>0.0052</td>
      <td>0.0051</td>
    </tr>
    <tr>
      <th>30</th>
      <td>0.0052</td>
      <td>0.0040</td>
      <td>0.0098</td>
      <td>0.0042</td>
      <td>0.0026</td>
      <td>0.0043</td>
      <td>0.0048</td>
      <td>0.0025</td>
      <td>0.0046</td>
      <td>0.0045</td>
    </tr>
    <tr>
      <th>31</th>
      <td>0.0046</td>
      <td>0.0033</td>
      <td>0.0087</td>
      <td>0.0039</td>
      <td>0.0024</td>
      <td>0.0037</td>
      <td>0.0043</td>
      <td>0.0021</td>
      <td>0.0041</td>
      <td>0.0040</td>
    </tr>
    <tr>
      <th>32</th>
      <td>0.0043</td>
      <td>0.0030</td>
      <td>0.0078</td>
      <td>0.0035</td>
      <td>0.0020</td>
      <td>0.0030</td>
      <td>0.0038</td>
      <td>0.0017</td>
      <td>0.0037</td>
      <td>0.0037</td>
    </tr>
    <tr>
      <th>33</th>
      <td>0.0040</td>
      <td>0.0027</td>
      <td>0.0073</td>
      <td>0.0032</td>
      <td>0.0018</td>
      <td>0.0027</td>
      <td>0.0035</td>
      <td>0.0015</td>
      <td>0.0034</td>
      <td>0.0032</td>
    </tr>
    <tr>
      <th>34</th>
      <td>0.0035</td>
      <td>0.0024</td>
      <td>0.0067</td>
      <td>0.0026</td>
      <td>0.0016</td>
      <td>0.0022</td>
      <td>0.0033</td>
      <td>0.0013</td>
      <td>0.0030</td>
      <td>0.0027</td>
    </tr>
    <tr>
      <th>35</th>
      <td>0.0032</td>
      <td>0.0021</td>
      <td>0.0060</td>
      <td>0.0024</td>
      <td>0.0013</td>
      <td>0.0019</td>
      <td>0.0030</td>
      <td>0.0011</td>
      <td>0.0025</td>
      <td>0.0024</td>
    </tr>
    <tr>
      <th>36</th>
      <td>0.0028</td>
      <td>0.0018</td>
      <td>0.0055</td>
      <td>0.0021</td>
      <td>0.0011</td>
      <td>0.0016</td>
      <td>0.0025</td>
      <td>0.0009</td>
      <td>0.0022</td>
      <td>0.0020</td>
    </tr>
    <tr>
      <th>37</th>
      <td>0.0026</td>
      <td>0.0015</td>
      <td>0.0050</td>
      <td>0.0019</td>
      <td>0.0010</td>
      <td>0.0014</td>
      <td>0.0023</td>
      <td>0.0008</td>
      <td>0.0018</td>
      <td>0.0017</td>
    </tr>
    <tr>
      <th>38</th>
      <td>0.0024</td>
      <td>0.0014</td>
      <td>0.0044</td>
      <td>0.0016</td>
      <td>0.0009</td>
      <td>0.0013</td>
      <td>0.0022</td>
      <td>0.0007</td>
      <td>0.0016</td>
      <td>0.0014</td>
    </tr>
    <tr>
      <th>39</th>
      <td>0.0022</td>
      <td>0.0013</td>
      <td>0.0041</td>
      <td>0.0015</td>
      <td>0.0007</td>
      <td>0.0011</td>
      <td>0.0019</td>
      <td>0.0006</td>
      <td>0.0014</td>
      <td>0.0012</td>
    </tr>
    <tr>
      <th>40</th>
      <td>0.0020</td>
      <td>0.0011</td>
      <td>0.0038</td>
      <td>0.0013</td>
      <td>0.0005</td>
      <td>0.0009</td>
      <td>0.0016</td>
      <td>0.0005</td>
      <td>0.0012</td>
      <td>0.0010</td>
    </tr>
    <tr>
      <th>41</th>
      <td>0.0019</td>
      <td>0.0010</td>
      <td>0.0037</td>
      <td>0.0013</td>
      <td>0.0004</td>
      <td>0.0008</td>
      <td>0.0013</td>
      <td>0.0004</td>
      <td>0.0010</td>
      <td>0.0009</td>
    </tr>
    <tr>
      <th>42</th>
      <td>0.0017</td>
      <td>0.0009</td>
      <td>0.0034</td>
      <td>0.0012</td>
      <td>0.0003</td>
      <td>0.0006</td>
      <td>0.0012</td>
      <td>0.0004</td>
      <td>0.0009</td>
      <td>0.0007</td>
    </tr>
    <tr>
      <th>43</th>
      <td>0.0015</td>
      <td>0.0008</td>
      <td>0.0032</td>
      <td>0.0010</td>
      <td>0.0002</td>
      <td>0.0006</td>
      <td>0.0011</td>
      <td>0.0003</td>
      <td>0.0007</td>
      <td>0.0007</td>
    </tr>
    <tr>
      <th>44</th>
      <td>0.0013</td>
      <td>0.0007</td>
      <td>0.0029</td>
      <td>0.0008</td>
      <td>0.0002</td>
      <td>0.0005</td>
      <td>0.0010</td>
      <td>0.0003</td>
      <td>0.0007</td>
      <td>0.0006</td>
    </tr>
    <tr>
      <th>45</th>
      <td>0.0012</td>
      <td>0.0006</td>
      <td>0.0027</td>
      <td>0.0007</td>
      <td>0.0002</td>
      <td>0.0005</td>
      <td>0.0008</td>
      <td>0.0003</td>
      <td>0.0006</td>
      <td>0.0005</td>
    </tr>
  </tbody>
</table></div>


The following figure shows the change of incidence rate for 10 replicate simulations. As you can see, the incidence rates increase rapidly at first. After day 15, due to the increase of social distancing, reflected by lowered production number, the population incidence rates start to decline after a few days of lag.


```Python3
incidence_rate.plot(xlabel='days', ylabel='incidence rate')
```




    <AxesSubplot:xlabel='days', ylabel='incidence rate'>




![png](/covid19-outbreak-simulator/assets/img/distancing_12_1.png)


The following figure shows sample incidence rates from 3 of the simulations, estimated from sampling 10% of the population (~ 500 people). Due to the overall low incidence rate, the estimates from the samples vary greatly.


```Python3
sample_incidence_rate[[1, 2, 3]].plot(xlabel='days', ylabel='sample incidence rate')
```




    <AxesSubplot:xlabel='days', ylabel='sample incidence rate'>




![png](/covid19-outbreak-simulator/assets/img/distancing_14_1.png)


## Availability


```Python3

```

This notebook is available under the `Applications` directory of the [GitHub repository](https://github.com/ictr/covid19-outbreak-simulator) of the COVID19 Outbreak Simulator. It can be executed with [`sos-papermill`](https://github.com/vatlab/sos-papermill) with the following parameters, or using a docker image `bcmictr/outbreak-simulator-notebook` as described in [here](/covid19-outbreak-simulator/docs/cli/).
