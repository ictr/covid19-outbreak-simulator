# reorganize.py
# this program takes the output of the outbreak simulator and converts it into a csv file with relevant data shown in tabular format 
# average values are given first, and individual results for each parameter for each simulation are given

#imports needed libraries
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

# opens dataset and creates new file for reorganized data
with open("pop_quarantine_all.txt") as f:
    pq_lines = f.readlines()

# convert txt file to dictionary
pq_dict = {}
for i in range(0, len(pq_lines)):
    split = pq_lines[i].split("\t")
    key = split[0]
    value = split[1]
    pq_dict[key] = value
print('Dictionary Created')

# delete keys that can't be turned into table form
del_list = [
'logfile',
'popsize',
'handle_symptomatic',
'interval',
'prop_asym_carriers',
'leadtime',
'n_simulation',
'total_infection',
'total_infection_failed',
'total_infection_avoided',
'total_infection_ignored',
'total_show_symptom',
'total_removal',
'total_recover',
'total_quarantine',
'total_reintegration',
'total_abort',
'total_asym_infection',
'total_presym_infection',
'total_sym_infection',
'n_remaining_popsize_3499',
'n_no_outbreak',
'n_no_infected_by_seed',
'n_seed_show_no_symptom',
'n_no_first_infection',
'n_first_infection_on_day_1',
'n_first_infection_on_day_2',
'n_first_symptom',
'n_first_symptom_on_day_1',
'n_second_symptom',
'n_second_symptom_on_day_1',
'n_third_symptom',
'n_third_symptom_on_day_1',
]

for i in del_list:
    del pq_dict[i]
print('Extraneous Deleted')

# find max number of days and create column with days from 0 - whatever
l = []
seperator = ''
for x in pq_dict.keys():
    result = (seperator.join(re.findall(r'[1-9]', x)))
    if result.isdigit():
        l.append(int(result))

dayslist = list(range(max(l) + 1)) 
print('Max Duration Found: '+ str(max(l)))

# create headers for relevant average data and dataframe list
avg_header_list = [
'n_outbreak_duration',
'avg_n_recovered',
'avg_n_recovered_1',
'avg_n_infected',
'avg_n_infected_1',
'avg_n_active',
'avg_n_active_1',
'avg_n_popsize',
'avg_n_popsize_1',
'avg_incidence_rate',
'avg_incidence_rate_1',
'avg_seroprevalence',
'avg_seroprevalence_1',
]
rec_list = ['n_recovered_%s' % s for s in range(1,101)]
inf_list = ['n_infected_%s' % s for s in range(1,101)]
act_list = ['n_active_%s' % s for s in range(1,101)]
pop_list = ['n_popsize_%s' % s for s in range(1,101)]
inc_list = ['incidence_rate_%s' % s for s in range(1,101)]
ser_list = ['seroprevalence_%s' % s for s in range(1,101)]

# creating Pandas dataframes 
pq_df = pd.DataFrame(None)
pq_df = pd.DataFrame(columns=avg_header_list + rec_list + inf_list + act_list + pop_list + inc_list + ser_list, index=dayslist)
print('Created Dataframes')

# fills in cells given dict key; exception case checking for n_outbreak_duration because it has a list of 1 element
def cellFill(key):
    keysplit = key.split('_')
    row = int(float(keysplit.pop()))
    column = '_'.join(keysplit)
    if column in avg_header_list:
        avg_value = pq_dict[key].strip('\n').split(',')
        pq_df.at[row,column] = avg_value[0]
        if len(avg_value) > 1: 
            pq_df.at[row,column + '_1'] = avg_value[1]
    if column == 'n_recovered':
        l_value = (pq_dict[key].strip('\n').split(', '))
        for i in l_value:
            rec_value = i.split(':')
            pq_df.at[row,'n_recovered_'+ rec_value[0]] = rec_value[1]
    if column == 'n_infected':
        l_value = (pq_dict[key].strip('\n').split(', '))
        for i in l_value:
            inf_value = i.split(':')
            pq_df.at[row,'n_infected_'+ inf_value[0]] = inf_value[1]
    if column == 'n_active':
        l_value = (pq_dict[key].strip('\n').split(', '))
        for i in l_value:
            act_value = i.split(':')
            pq_df.at[row,'n_active_'+ act_value[0]] = act_value[1]
    if column == 'n_popsize':
        l_value = (pq_dict[key].strip('\n').split(', '))
        for i in l_value:
            pop_value = i.split(':')
            pq_df.at[row,'n_popsize_'+ pop_value[0]] = pop_value[1]
    if column == 'incidence_rate':
        l_value = (pq_dict[key].strip('\n').split(', '))
        for i in l_value:
            inc_value = i.split(':')
            pq_df.at[row,'incidence_rate_'+ inc_value[0]] = inc_value[1]
    if column == 'seroprevalence':
        l_value = (pq_dict[key].strip('\n').split(', '))
        for i in l_value:
            ser_value = i.split(':')
            pq_df.at[row,'seroprevalence_'+ ser_value[0]] = ser_value[1]
           
# fills in cells
for x in pq_dict.keys():
    cellFill(x)
print('Cells Filled')

# writes to csv and creates plots

pq_df = pq_df.astype(float)
lines = pq_df.plot.line()
plt.show()
pq_df.to_csv('reorg_data.csv')
print('Converted to CSV')
