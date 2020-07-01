#reorganize.py
#takes the output of the outbreak simulator and turns it into a csv file with relevant data shown in tabular format

import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import argparse

def identify_timestamps(dictionary):
    timestamps = [float(x.rsplit('_', 1)[1]) for x in dictionary.keys()]
    return timestamps

def delete_extra(dictionary):
    del_list = [x for x in dictionary.keys() if re.search(r'\d+', x) == None]
    for i in del_list:
        del dictionary[i]
    name = [x.rsplit('_', 1)[0] for x in dictionary.keys()]

    del_list_t = []
    for x in name:
        count = 0
        for y in name:
            if x == y:
                count += 1
        if count < 3:
            del_list_t.append(x)
        
    del_list_f = [x for i in del_list_t for x in dictionary.keys() if i == x.rsplit('_', 1)[0]]
    for i in (list(set(del_list_f))):
        del dictionary[i]
              
def identify_columns(dictionary, num_simulations):
    columns = []
    temp = [sorted(list(set(x.rsplit('_',1)[0] for x in dictionary.keys())))][0]
    for x in temp:
        l_temp = [x + '_%s' %s for s in range(1, int(num_simulations) + 1)]
        columns += l_temp
    return columns

def fill_cells(dictionary,dataframe):
    for x in dictionary.keys():
        row = int(float(x.rsplit('_', 1)[1]))
        value_list = (dictionary[x].strip('\n').split(', '))
        for y in enumerate(value_list): 
            if re.search(':', y[1]):
                column = x.rsplit('_', 1)[0] + '_' + str(y[1].split(':')[0])
                value = y[1].split(':')[1]
            else:
                column = x.rsplit('_', 1)[0] + '_' + str(y[0] + 1)
                value = y[1]
            dataframe.at[row,column] = value

def reorganize(txtfile):
    #opens txt file
    with open(txtfile) as f:
        pq_lines = f.readlines()

    #creates dictionary
    pq_dict = {}
    for i in pq_lines:
        keyvalue = i.split("\t")
        pq_dict[keyvalue[0]] = keyvalue[1].rstrip('\n')
    num_simulations = pq_dict['n_simulation']

    #finds and deletes keys without time stamps 1. deletes anything without numbers 2. deletes anything that only occurs once
    delete_extra(pq_dict)

    #finds timestamp
    time_index = range(int(max(identify_timestamps(pq_dict))) + 1)

    #finds column name
    column_names = identify_columns(pq_dict,num_simulations)

    #create pandas dataframe
    pq_df = pd.DataFrame(columns = column_names, index = time_index)

    #fill cells using dictionary
    fill_cells(pq_dict, pq_df)

    #organize dataframe and print to csv
    pq_df = pq_df.astype(float)
    pq_df = pq_df.dropna(axis = 1, how = 'all')
    pq_df.to_csv('reorg_data.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="txt file to convert")
    args = parser.parse_args()
    reorganize(args.file)
