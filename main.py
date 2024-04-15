import streamlit as st
import requests
import json
from zipfile import ZipFile


info = {'sensor_on': ' на демпфере', 'disk_distance': '25 мм', 'washer': '3 мм', 'interval': '1 с',
            'step': '10**-4', 'diameter': '10 мм до 6 мм с удл цч',
            'hole_diameter': '10 мм', 'nozzle_length': '50 мм + 25 мм',
            'insert_variant': '3', 'd_f_between': 'сталь 1200 мм + фланцы',
            'labview_num': '13', 'cs': '', 'compressor': '8 атм', 'sensors': 'дифференциальные датчики на 10 атм'}

absolute = {'sensor_on': 'Датчик', 'disk_distance': 'дистанции до диска', 'washer': 'шайба', 'interval': 'интервал',
            'step': 'шаг', 'diameter': 'Истечение из сужающегося сопла с диаметра ',
            'hole_diameter': 'Диаметр отверстия кавитатора (шайба)', 'nozzle_length': 'Длина сопла ~ ',
            'insert_variant': 'Вставка в каверну, вариант № ', 'd_f_between': ' Между демпфером и форкамерой ',
            'labview_num': ' Программа LabVIEW-', 'cs': 'Cs=', 'compressor': 'Компрессор на ', 'sensors': 'На каверне и экране стоят '}

url = "https://vvproject.onrender.com/"
# url = "http://127.0.0.1:8000/"
st.title("Система обработки текстовых результатов labview")

st.write("Введите данные об эксперименте, датчиках")
with st.form(key='experiment_data_form'):
    for key in info.keys():
        info[key] = st.text_input(label=f'{absolute[key]}', value=f'{info[key]}')
    submitted = st.form_submit_button("Зафиксировать")

# deliver form information to backend
r = requests.post(f"{url}info", json=info)

uploaded_files = st.file_uploader("Перетащите сюда и бросьте или выберите текстовый файл экспериментов", type='txt', accept_multiple_files=True)
archive_name = None
date = None

if uploaded_files is not None:
    with ZipFile('data.zip', 'w') as zip:
        for uploaded_file in uploaded_files:
            if uploaded_file is not None:
                files = {'file': uploaded_file}
                response = requests.post(f"{url}upload", files=files)
                # create xlsx name from txt
                new_file_name = uploaded_file.name
                new_file_name = new_file_name.split('_')
                date = '-'.join(new_file_name[0].split('.')[:2])
                num_of_experiment = new_file_name[-1].split('-')[0]
                new_file_name = f'{date}-{num_of_experiment}'

                with open(f'{new_file_name}.xlsx', 'wb') as f:
                    f.write(response.content)

                zip.write(f'{new_file_name}.xlsx')

        if date is not None:
            archive_name = f"{date}.zip"

if archive_name is not None:
    with open('data.zip', 'rb') as zip:
        st.download_button(f'Загрузить Архив', zip, archive_name, mime="application/zip")
            
