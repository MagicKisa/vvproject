import streamlit as st
import requests

info = {'sensor_on': ' на демпфере', 'disk_distance': '25 мм', 'washer': '3 мм', 'interval': '1 с',
            'step': '10**-4', 'diameter': '10 мм до 6 мм с удл цч',
            'hole_diameter': '10 мм', 'nozzle_length': '50 мм + 25 мм',
            'insert_variant': 3, 'd-f_between': 'сталь 1200 мм + фланцы',
            'labview_num': 13, 'cs': '', 'compressor': '8 атм', 'sensors': 'дифференциальные датчики на 10 атм'}

absolute = {'sensor_on': 'Датчик на ', 'disk_distance': 'дистанции до диска', 'washer': 'шайба', 'interval': 'интервал',
            'step': 'шаг', 'diameter': 'Истечение из сужающегося сопла с диаметра ',
            'hole_diameter': 'Диаметр отверстия кавитатора (шайба)', 'nozzle_length': 'Длина сопла ~ ',
            'insert_variant': 'Вставка в каверну, вариант № ', 'd-f_between': ' Между демпфером и форкамерой ',
            'labview_num': ' Программа LabVIEW-', 'cs': 'Cs=', 'compressor': 'Компрессор на ', 'sensors': 'На каверне и экране стоят '}

url = "https://vvproject.onrender.com/upload"
st.title("Система обработки текстовых результатов labview")

st.write("Введите данные об эксперименте, датчиках")
with st.form(key='experiment_data_form'):
    for key in info.keys():
        info[key] = st.text_input(label=f'{absolute[key]}', value=f'{info[key]}')
    submitted = st.form_submit_button("Зафиксировать")


uploaded_files = st.file_uploader("Перетащите сюда и бросьте или выберите текстовый файл экспериментов", type='txt', accept_multiple_files=True)

for uploaded_file in uploaded_files:        
    if uploaded_file is not None:
        files = {'file': uploaded_file}
        response = requests.post(url, files=files)
        new_file_name = uploaded_file.name
        new_file_name = new_file_name.split('_')
        new_file_name = '-'.join(new_file_name[0].split('.')[:2] + new_file_name[-1].split('-')[:1])

        st.download_button(f'Загрузить {new_file_name}.xlsx', response.content, f'{new_file_name}.xlsx')
            
