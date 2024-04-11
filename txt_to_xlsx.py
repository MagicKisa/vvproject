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
    '''
    input: pd.dataframe with exponential string values
    output: pd.dataframe with float values
    '''
    values = np.array(df.values)
    f = lambda x: float(str(x).lower().replace(',', '.'))
    values= np.vectorize(f)(values)
    #new_df = df.apply(lambda x: float(str(x).lower().replace(',', '.')))
    #new_df = new_df.apply(pd.to_numeric)
    new_df = pd.DataFrame(values, columns=df.columns)
    return new_df

def interesting_table(table):
    '''
    input: all table data
    output: table with only t(c) Po-Pa Pk-Pa Pmэкр Po-Pk Рдем columns
    '''
    columns = table.columns
    num_of_columns = [0, 2, 3, 7, 11]
    
    interesting_columns = [columns[i] for i in num_of_columns]
    interesting_table = table[interesting_columns].copy()
    interesting_table['Pо-Pk'] = interesting_table[columns[2]] - interesting_table[columns[3]]
    return interesting_table

def get_period(mean_parameters):
    '''
    got: table with mean parameters
    return: period
    '''
    float_mean_parameters = get_float_table(mean_parameters)
    period = 1 / float_mean_parameters['Hk(гц)'][0]
    return period

def add_period(interesting_table, period):
    '''
    got: table without period graph
    return: table with period graph
    '''
    interesting_table['period'] = interesting_table['t'] / period
    interesting_table['period'] = interesting_table['period'].apply(int)
    return interesting_table

def amplitudes_table(interesting_table):
    '''
    got: table with interesting columns
    return: table with max, min amplitudes pэ, Pk-Pa in each period
    '''
    amplitudes_table = pd.DataFrame()
    pk_min = []
    pk_max = []
    p0_min = []
    p0_max = []
    d = {'Pэкран': {'max' : [], 'min' : []}, '(Pk-Pa)': {'max' : [], 'min' : []}}
    for period in interesting_table['period'].unique()[:-1]:
        for p_name in d.keys():
            d[p_name]['min'].append(interesting_table[interesting_table['period'] == period][p_name].min())
            d[p_name]['max'].append(interesting_table[interesting_table['period'] == period][p_name].max())
            
    
    amplitudes_table['pэ_max'] = d['Pэкран']['max']
    amplitudes_table['pэ_min'] = d['Pэкран']['min']
    
    amplitudes_table['pk_max'] = d['(Pk-Pa)']['max']
    amplitudes_table['pk_min'] = d['(Pk-Pa)']['min']

    return amplitudes_table

def sums_table(amplitudes_table):
    '''
    got: table with amplitudes
    return: table with summ amplitudes of all periods in each column
    '''
    sums_table = pd.DataFrame()
#    print(amplitudes_table['pэ_max'].sum())
    sums_table['pэ_max'] = [amplitudes_table['pэ_max'].sum()]
    sums_table['pэ_min'] = [amplitudes_table['pэ_min'].sum()]
    sums_table['pk_max'] = [amplitudes_table['pk_max'].sum()]
    sums_table['pk_min'] = [amplitudes_table['pk_min'].sum()]

    return sums_table

def answer_table(sums_table, amplitudes_table, interesting_table, mean_parameters):
    '''
    got: sums_table, amplitudes_table, interesting_table, mean_parameters
    return: table with sought-after vals
    '''
    answer_table = pd.DataFrame()
    mean_parameters = get_float_table(mean_parameters)
#    print(mean_parameters.head())
    answer_table['Qlэфф(л/с)'] = 0.638 * np.sqrt(mean_parameters['Po(кг/см**2)'] - mean_parameters['Pk(кг/см**2)'])
    answer_table['Cqэфф'] = 1000 * mean_parameters['Qg(м**3/с)'] / answer_table['Qlэфф(л/с)']
    answer_table['A(at)'] = (sums_table['pэ_max'] - sums_table['pэ_min']) / len(amplitudes_table)
    answer_table['A/Po'] = answer_table['A(at)'] / mean_parameters['Po(кг/см**2)']
    answer_table['A(atk)'] = (sums_table['pk_max'] - sums_table['pk_min']) / len(amplitudes_table)
    answer_table['A/Pk'] = answer_table['A(atk)'] / mean_parameters['Po(кг/см**2)']
    answer_table['div'] = answer_table['A(at)'] / answer_table['A(atk)']
    
    return answer_table

mean_parameters = read_mean_parameters(sys.argv[1])
table = read_table(sys.argv[1])


# create excel file
file = sys.argv[1]
new_file_name = file.split('_')
new_file_name = '-'.join(new_file_name[0].split('.')[:2] + new_file_name[-1].split('-')[:1])
writer = pd.ExcelWriter(f'{new_file_name}.xlsx', engine='xlsxwriter')

# evaluate and write all tables
table.to_excel(writer, 'Sheet1')
mean_parameters.to_excel(writer, 'Sheet1', startcol=15, index=False)

interesting_table = interesting_table(get_float_table(table))

period = get_period(mean_parameters)
interesting_table = add_period(interesting_table, period)

amplitudes_table = amplitudes_table(interesting_table)
sums_table = sums_table(amplitudes_table)

answer_table = answer_table(sums_table, amplitudes_table, interesting_table, mean_parameters)


interesting_table.to_excel(writer, 'Sheet1', startcol=40, index=False)
amplitudes_table.to_excel(writer, 'Sheet1', startcol=26, index=False)

answer_table.to_excel(writer, 'Sheet1', startcol=15, startrow=10, index=False)

workbook = writer.book
worksheet = writer.sheets['Sheet1']
worksheet.write('N1', len(interesting_table))

# add chartsheet to excel and plot charts
chartsheet = workbook.add_chartsheet()
chart1 = workbook.add_chart({'type':'line'})
chart1.add_series(
    {
        "name": 'Po-Pa',
        "values": f"=Sheet1!$AP2:$AP{len(interesting_table)}",
        "categories": f"=Sheet1!$AO2:$AO2{len(interesting_table)}",
        "line" : {'color' : 'green', 'width' : 1}
    }
)
chart1.add_series(
    {
        "name": 'Pk-Pa',
        "values": f"=Sheet1!$AQ2:$AQ{len(interesting_table)}",
        "categories": f"=Sheet1!$AO2:$AO2{len(interesting_table)}",
        "line" : {'color' : 'blue', 'width' : 1}
    }
)
chart1.add_series(
    {
        "name": 'Pmэкр',
        "values": f"=Sheet1!$AS2:$AS{len(interesting_table)}",
        "categories": f"=Sheet1!$AO2:$AO2{len(interesting_table)}",
        "line" : {'color' : 'red', 'width' : 1}
    }
)
chart1.add_series(
    {
        "name": 'Pдем',
        "values": f"=Sheet1!$AR2:$AR{len(interesting_table)}",
        "categories": f"=Sheet1!$AO2:$AO2{len(interesting_table)}",
        "line" : {'color' : '#FF9900', 'width' : 1}
    }
)
chart1.set_size({'width': 1500, 'height': 1000})
chart1.set_x_axis({"name": "Измерение"})
chart1.set_y_axis({"name": "P(kg/cm^2)"})
chart1.set_x_axis({'num_format': '0.00', 'minor_unit' : 0.1})
chartsheet.set_chart(chart1)
chartsheet.activate()

writer.close()

