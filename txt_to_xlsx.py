import pandas as pd
import sys
import xlsxwriter
import math
import numpy as np
import json

def read_headers_list(file, skiprows):
    ''' Читает заголовки из csv файла начиная со строчки skiprows + 1 
    Read headers list from csv file in non initial position skiprows + 1
    '''
    headers_df = pd.read_csv(file, sep='\s\s+', skiprows=skiprows, header=None, nrows=1, encoding='cp1251', engine='python')
    headers_list = headers_df.values[0]
    return headers_list

def read_mean_parameters(file):
    ''' Читает осредненные значения параметров течения с первой строчки и записывает в pandas df
    Read mean parameters with headers from especially separated labview data files as pandas.df
    '''
    headers_list = read_headers_list(file, 1)
    values = pd.read_csv(file, sep='\s+', skiprows=2, nrows=1, header=None, encoding='cp1251')
    df = pd.DataFrame(values.values, columns=headers_list)
    
    return df
    
def read_table(file):
    ''' Читает осцилограммы и её заголовки и записывает в пандас датафрейм
    Read table with headers from especially separated labview data files as pandas.df
    '''
    headers_list = read_headers_list(file, 4)
    values = pd.read_csv(file, sep='\t', skiprows=5, header=None, encoding='cp1251')

    df = pd.DataFrame(values.values, columns=headers_list)
    return df


def get_float_table(df):
    '''
    на вход принимает pd.dataframe со строковыми эксопненциальными записями чисел
    на выход выдает pd.df с вещественными числами
    input: pd.dataframe with exponential string values
    output: pd.dataframe with float values
    '''
    values = np.array(df.values)
    f = lambda x: float(str(x).lower().replace(',', '.'))
    values= np.vectorize(f)(values)
    new_df = pd.DataFrame(values, columns=df.columns)
    return new_df

def get_interesting_table(table):
    '''
    на вход принимает pd.df содержащий все осцилограммы
    на выходе выдает pd.df содержащий только t(c) Po-Pa Pk-Pa Pmэкр Po-Pk Рдем столбцы
    input: all table data
    output: table with only t(c) Po-Pa Pk-Pa Pmэкр Po-Pk Рдем columns
    '''
    columns = table.columns
    num_of_columns = [0, 2, 3, 7, 11]

    # копируем только интересующие нас столбцы
    interesting_columns = [columns[i] for i in num_of_columns]
    interesting_table = table[interesting_columns].copy()

    # Po - Pk считаем как Po-Pa - Pk-Pa
    interesting_table['Pо-Pk'] = interesting_table[columns[2]] - interesting_table[columns[3]]
    return interesting_table

def get_period(mean_parameters):
    '''
    получает таблицу с осреднёнными значениями
    выдаёт период посчитанный благодаря средней частоте
    got: table with mean parameters
    return: period
    '''
    
    period = 1 / mean_parameters['Hk(гц)'][0]
    return period

def add_period(interesting_table, period):
    '''
    получает на вход таблицу с интересующими осцилограммами и значение периода
    возвращает таблицу со столбцом содержащим номер периода
    got: table without period graph
    return: table with period graph
    '''
    interesting_table['period'] = interesting_table['t'] / period
    interesting_table['period'] = interesting_table['period'].apply(int)
    return interesting_table

def get_amplitudes_table(interesting_table):
    '''
    получает таблицу с номерами периодов и осцилограммами и возвращает
    таблицу с максимальными и минимальными амплитудами осцилограмм Pэкран, Pk-Pa на каждом периоде
    got: table with interesting columns
    return: table with max, min amplitudes pэ, Pk-Pa in each period
    '''
    amplitudes_table = pd.DataFrame()
    pk_min = []
    pk_max = []
    p0_min = []
    p0_max = []
    d = {'Pэкран': {'max' : [], 'min' : []}, '(Pk-Pa)': {'max' : [], 'min' : []}}
    # считаем максимумы и минимумы амплитуд за каждый период(кроме последнего так как он незавершён) для Pэкран и Pk-Pa 
    for period in interesting_table['period'].unique()[:-1]:
        for p_name in d.keys():
            d[p_name]['min'].append(interesting_table[interesting_table['period'] == period][p_name].min())
            d[p_name]['max'].append(interesting_table[interesting_table['period'] == period][p_name].max())
            
    
    amplitudes_table['pэ_max'] = d['Pэкран']['max']
    amplitudes_table['pэ_min'] = d['Pэкран']['min']
    
    amplitudes_table['pk_max'] = d['(Pk-Pa)']['max']
    amplitudes_table['pk_min'] = d['(Pk-Pa)']['min']

    return amplitudes_table

def get_sums_table(amplitudes_table):
    '''
    получает таблицу с амплитудами
    выдает таблицу содержащую суммы её столбцов
    got: table with amplitudes
    return: table with summ amplitudes of all periods in each column
    '''
    sums_table = pd.DataFrame()

    sums_table['pэ_max'] = [amplitudes_table['pэ_max'].sum()]
    sums_table['pэ_min'] = [amplitudes_table['pэ_min'].sum()]
    sums_table['pk_max'] = [amplitudes_table['pk_max'].sum()]
    sums_table['pk_min'] = [amplitudes_table['pk_min'].sum()]

    return sums_table

def get_answer_table(sums_table, amplitudes_table, interesting_table, mean_parameters):
    '''
    получает на вход все посчитанные до этого таблицы
    используя их по формулам считает необходимые значения и возвращает их
    got: sums_table, amplitudes_table, interesting_table, mean_parameters
    return: table with sought-after vals
    '''
    answer_table = pd.DataFrame()
    
    answer_table['Qlэфф(л/с)'] = 0.638 * np.sqrt(mean_parameters['Po(кг/см**2)'] - mean_parameters['Pk(кг/см**2)'])
    answer_table['Cqэфф'] = 1000 * mean_parameters['Qg(м**3/с)'] / answer_table['Qlэфф(л/с)']
    answer_table['Am'] = (sums_table['pэ_max'] - sums_table['pэ_min']) / len(amplitudes_table)
    answer_table['Am/Po'] = answer_table['Am'] / mean_parameters['Po(кг/см**2)']
    answer_table['Ak'] = (sums_table['pk_max'] - sums_table['pk_min']) / len(amplitudes_table)
    answer_table['Ak/Po'] = answer_table['Ak'] / mean_parameters['Po(кг/см**2)']
    answer_table['Am/Ak'] = answer_table['Am'] / answer_table['Ak']
    
    return answer_table

def get_voo_table():
    '''необходима для записи формул в итоговый excel файл,
    при записи в файл на основе уже записанных в книгу excel данных считает по формулам необходимые значения
    '''
    columns = ['Voo(м/с)', 'Cq', 'Cd', 'Kp', 'T(s)', 'Std', 'Stdо']
    data = [['=SQRT(2 * A2 * 100)', '=1000 * D2/C2', '=B2/A2', '=C2/(1000 * M2 * 0.025 * 0.009)', '=1/J2', '=J2*0.025/M2', '=K2*0.025/M2']]
    voo_table = pd.DataFrame(data=data, columns=columns)
    return voo_table

def create_excel_by_txt(file, info):
    '''
    На вход принимает название файла содержащего текстовые данные эксперимента и таблицу с данными об экспериментальной установке 
    проводит расчёт интересующих значений записывает их в excel и строит необходимые графики
    '''

    # чтение исходных данных
    mean_parameters = read_mean_parameters(file)
    table = read_table(file)
    mean_parameters = get_float_table(mean_parameters)
    table = get_float_table(table)

    # create excel file
    # создание excel файла
    new_file_name = file.split('_')
    new_file_name = '-'.join(new_file_name[0].split('.')[:2] + new_file_name[-1].split('-')[:1])
    writer = pd.ExcelWriter(f'{new_file_name}.xlsx', engine='xlsxwriter')

    # evaluate and write all tables
    # вычисление и запись всех таблиц
    table.to_excel(writer, sheet_name='Sheet1', startrow=3)
    mean_parameters.to_excel(writer, sheet_name='Sheet1', index=False)

    interesting_table = get_interesting_table(table)

    period = get_period(mean_parameters)
    interesting_table = add_period(interesting_table, period)

    amplitudes_table = get_amplitudes_table(interesting_table)
    sums_table = get_sums_table(amplitudes_table)
    voo_table = get_voo_table()
    answer_table = get_answer_table(sums_table, amplitudes_table, interesting_table, mean_parameters)

    interesting_table.to_excel(writer, sheet_name='Sheet1', startcol=32, startrow=5, index=False)
    amplitudes_table.to_excel(writer, sheet_name='Sheet1', startrow=5, startcol=26, index=False)
    voo_table.to_excel(writer, sheet_name='Sheet1', startcol=12, index=False)
    answer_table.to_excel(writer, sheet_name='Sheet1', startcol=23, index=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # добавление страницы с графиками и графиков на неё, форматирования
    chartsheet = workbook.add_chartsheet()
    chart1 = workbook.add_chart({'type':'line'})

    chart_dict = {'Po-Pa': ['H', 'green'], 'Pk-Pa': ['I', 'blue'], 'Pmэкр': ['K', 'red'], 'Pдем': ['J', '#FF9900']}
    for key in chart_dict:
        letter = chart_dict[key][0]
        color = chart_dict[key][1]
        chart1.add_series(
            {
                "name": key,
                "values": f"=Sheet1!$A{letter}2:$A{letter}{len(interesting_table)}",
                "categories": f"=Sheet1!$AG2:$AG2{len(interesting_table)}",
                "line" : {'color' : color, 'width' : 1},
                "smooth": True
            }
        )

    chart1.set_size({'width': 1500, 'height': 1000})
    chart1.set_x_axis({"name": "Измерение"})
    chart1.set_y_axis({"name": "P(kg/cm^2)"})
    chart1.set_x_axis({'num_format': '0.00', 'minor_unit' : 0.1})
    chart1.set_legend({'position': 'bottom'})
    chartsheet.set_chart(chart1)
    chartsheet.activate()
    cell_format = workbook.add_format({'bold': True, 'font_color': 'red'})
    cell_format.set_font_size(20)

    # Добавление на числовую страницу описания установки
    for i, key in enumerate(info.keys()):
        worksheet.write(f'P{i + 14}', f' {info[key][0]} {info[key][1]}', cell_format)        

    writer.close()

    return f"{new_file_name}.xlsx"

