#reorganize.py
#takes the output of the outbreak simulator and turns it into a csv file with relevant data shown in tabular format

import pandas as pd
import re
import sys
import argparse

def identify_timestamps(dictionary):
    timestamps = [float(x.rsplit('_', 1)[1]) for x in dictionary.keys() if '_' in x]
    return timestamps

def delete_extra(dictionary):
    temp_dict = {x[0]:x[1] for x in dictionary.items() if re.search(r'\d+', x[0])}
    
    name = [x.rsplit('_', 1)[0] for x in temp_dict.keys()]
    del_list_2 = [x for x in name if name.count(x) < 3]

    return {x[0]:x[1] for x in temp_dict.items() if x[0].rsplit('_', 1)[0] not in del_list_2}
              
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

def reorganize(input,output):
    #opens txt file
    with open(input) as f:
        pq_lines = f.readlines()

    #creates dictionary
    pq_dict = {}
    for i in pq_lines:
        keyvalue = i.split("\t")
        pq_dict[keyvalue[0]] = keyvalue[1].rstrip('\n')
    num_simulations = pq_dict['n_simulation']

    #finds and deletes keys without time stamps 1. deletes anything without numbers 2. deletes anything that only occurs once
    pq_dict = delete_extra(pq_dict)

    #finds timestamp
    time_index = range(int(max(identify_timestamps(pq_dict))) + 1)

    #finds column name
    column_names = identify_columns(pq_dict,num_simulations)

    #create pandas dataframe
    pq_df = pd.DataFrame(columns = column_names, index = time_index)

    #fill cells using dictionary
    fill_cells(pq_dict, pq_df)

    #drops columns with no data
    pq_df = pq_df.astype(float)
    pq_df = pq_df.dropna(axis = 1, how = 'all')

    #prints to csv file or to standard output
    if output == '':
        pq_df.to_csv(sys.stdout)
    else:
        pq_df.to_csv(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-inp', 
        default = sys.stdin.readline().strip('\n'),
        nargs = '?',
        help = 'txt file or path to convert'
        )
    parser.add_argument(
        '-out', 
        nargs = '?',
        default = sys.stdin.readline().strip('\n'),
        help = 'file to convert to'
        )
    args = parser.parse_args()
    print(args)
    reorganize(args.inp,args.out)
