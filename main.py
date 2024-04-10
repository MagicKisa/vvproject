import pandas as pd
import sys
import xlsxwriter
import math
import numpy as np

def read_headers_list(file, skiprows):
    '''
    Read headers list from csv file in non initial position skiprows + 1
    '''
    headers_df = pd.read_csv(file, sep='\s\s+', skiprows=skiprows, header=None, nrows=1, encoding='cp1251', engine='python')
    headers_list = headers_df.values[0]
    return headers_list

def read_mean_parameters(file):
    '''
    Read mean parameters with headers from especially separated labview data files as pandas.df
    '''
    headers_list = read_headers_list(file, 1)
    values = pd.read_csv(file, sep='\s+', skiprows=2, nrows=1, header=None, encoding='cp1251')

    df = pd.DataFrame(values.values, columns=headers_list)
    return df

def read_table(file):
    '''
    Read table with headers from especially separated labview data files as pandas.df
    '''
    headers_list = read_headers_list(file, 4)
    values = pd.read_csv(file, sep='\t', skiprows=5, header=None, encoding='cp1251')

    df = pd.DataFrame(values.values, columns=headers_list)
    return df


def get_float_table(df):
    values = np.array(df.values)
    f = lambda x: float(str(x).lower().replace(',', '.'))
    values= np.vectorize(f)(values)
    #new_df = df.apply(lambda x: float(str(x).lower().replace(',', '.')))
    #new_df = new_df.apply(pd.to_numeric)
    new_df = pd.DataFrame(values, columns=df.columns)
    return new_df

def interesting_table(table):
    columns = table.columns
    num_of_columns = [0, 2, 3, 7, 11]
    
    interesting_columns = [columns[i] for i in num_of_columns]
    interesting_table = table[interesting_columns].copy()
    interesting_table['Pо-Pk'] = interesting_table[columns[2]] - interesting_table[columns[3]]
    return interesting_table

def get_period(mean_parameters):
    float_mean_parameters = get_float_table(mean_parameters)
    period = 1 / float_mean_parameters['Hk(гц)'][0]
    return period

def add_period(interesting_table, period):
    interesting_table['period'] = interesting_table['t'] / period
    interesting_table['period'] = interesting_table['period'].apply(int)
    return interesting_table

def amplitudes_table(interesting_table):
    amplitudes_table = pd.DataFrame()
    pk_min = []
    pk_max = []
    p0_min = []
    p0_max = []
    d = {'Pэкран': {'max' : [], 'min' : []}, '(Pk-Pa)': {'max' : [], 'min' : []}}
    for period in interesting_table['period'].unique():
        for p_name in d.keys():
            d[p_name]['min'].append(interesting_table[interesting_table['period'] == period][p_name].min())
            d[p_name]['max'].append(interesting_table[interesting_table['period'] == period][p_name].max())
            
    
    amplitudes_table['pэ_max'] = d['Pэкран']['max']
    amplitudes_table['pэ_min'] = d['Pэкран']['min']
    
    amplitudes_table['pk_max'] = d['(Pk-Pa)']['max']
    amplitudes_table['pk_min'] = d['(Pk-Pa)']['min']

    return amplitudes_table

mean_parameters = read_mean_parameters(sys.argv[1])
table = read_table(sys.argv[1])

writer = pd.ExcelWriter('file.xlsx', engine='xlsxwriter')

table.to_excel(writer, 'Sheet1')
mean_parameters.to_excel(writer, 'Sheet1', startcol=15, index=False)

interesting_table = interesting_table(get_float_table(table))
period = get_period(mean_parameters)
interesting_table = add_period(interesting_table, period)
print(amplitudes_table(interesting_table).head())

writer.close()

#print(mean_parameters.head())
#print(get_float_table(table).head())


#print(mean_parameters.apply(pd.to_numeric).head())


