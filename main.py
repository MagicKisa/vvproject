import streamlit as st
import requests
import json
from txt_to_xlsx import create_excel_by_txt
from zipfile import ZipFile

def get_date_from_filename(filename):
    date = '-'.join(filename.split('.')[:2])
    return date

def create_excel_filename(filename):
    date = get_date_from_filename(filename)
    
    num_of_experiment = filename.split('-')[0].split('_')[-1]
    excel_filename = f'{date}-{num_of_experiment}.xlsx'

    return excel_filename

with open('form_data.json', 'r', encoding='cp1251') as f:
    form_info = json.load(f)

st.title("Система обработки текстовых результатов labview")

st.write("Введите данные об эксперименте, датчиках")
with st.form(key='experiment_data_form'):
    for key in form_info.keys():
        form_info[key][1] = st.text_input(label=f'{form_info[key][0]}', value=f'{form_info[key][1]}')
    submitted = st.form_submit_button("Зафиксировать")
    with open('form_data.json', 'w', encoding='cp1251') as f:
        f.write(json.dumps(form_info))

uploaded_files = st.file_uploader("Перетащите сюда и бросьте или выберите текстовый файл экспериментов", type='txt', accept_multiple_files=True)
archive_name = None
date = None

if uploaded_files is not None:
    with ZipFile('data.zip', 'w') as zip:
        for uploaded_file in uploaded_files:
            if uploaded_file is not None:
                # create xlsx name from txt
                with open(uploaded_file.name, 'wb') as f:
                    f.write(uploaded_file)
                excel_file = create_excel_by_txt(uploaded_file.name, form_info)
                excel_filename = create_excel_filename(uploaded_file.name)

                zip.write(excel_file)
                date = get_date_from_filename(uploaded_file.name)
        if date is not None:
            archive_name = f"{date}.zip"

if archive_name is not None:
    with open('data.zip', 'rb') as zip:
        st.download_button(f'Загрузить Архив', zip, archive_name, mime="application/zip")
            
