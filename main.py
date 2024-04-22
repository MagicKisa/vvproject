import streamlit as st
import requests
import json
import openpyxl

from utils import create_excel_by_txt, compound_excel_from_many
from zipfile import ZipFile, ZIP_DEFLATED

def get_date_from_filename(filename):
    ''' Получает дату из названия файла

    '''
    date = '-'.join(filename.split('.')[:2])
    return date


# декоратор указывает streamlit кэшировать получаемые excel-файлы, чтобы не пересчитывать
@st.cache_data
def get_excel_filename(filename, form_info, _compound_wb):
    excel_filename = create_excel_by_txt(filename, form_info, _compound_wb)

    return excel_filename

@st.cache_data
def get_compound_wb():
    compound_wb = openpyxl.Workbook()

    return compound_wb

# Выгружаем информацию об эксперименте из файла, в который её сохранили при инициализации проекта
with open('form_data.json', 'r', encoding='cp1251') as f:
    form_info = json.load(f)

st.title("Система обработки текстовых результатов labview")

# форма нужна чтобы поменять информацию об эксперименте и сохранить её в файл
st.write("Введите данные об эксперименте, датчиках")
with st.form(key='experiment_data_form'):
    for key in form_info.keys():
        form_info[key][1] = st.text_input(label=f'{form_info[key][0]}', value=f'{form_info[key][1]}')

    submitted = st.form_submit_button("Зафиксировать")
    with open('form_data.json', 'w', encoding='cp1251') as f:
        f.write(json.dumps(form_info))

compound_filename = st.text_input(label='Введите название общего файла', value='S1200d06k10L75dis25V№3')
compound_wb = get_compound_wb()

# виджет для загрузки нескольких текстовых файлов
uploaded_files = st.file_uploader("Перетащите сюда и бросьте или выберите текстовый файл экспериментов", type='txt', accept_multiple_files=True)

# инициализурем переменные в глобальной области видимости
archive_name = None
date = None

with ZipFile('data.zip', 'w', ZIP_DEFLATED) as zip:
    excel_filenames = []
    for uploaded_file in uploaded_files:
        # Записываем файлы в облаке, чтобы можно было  к ним обращаться
        with open(uploaded_file.name, 'wb') as f:
            f.write(uploaded_file.read())
    
        excel_filename = get_excel_filename(uploaded_file.name, form_info, compound_wb)
        zip.write(excel_filename)
        excel_filenames.append(excel_filename)
        date = get_date_from_filename(uploaded_file.name)
        archive_name = f"{date}.zip"

    if excel_filenames:
        compound_wb.save(f'{compound_filename}.xlsx')
        zip.write(f'{compound_filename}.xlsx')

if archive_name is not None and date is not None:
    with open('data.zip', 'rb') as zip:
        st.download_button(f'Загрузить Архив', zip, archive_name)
            
