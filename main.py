import streamlit as st
import requests
import json
'''
В этом файле находится streamlit часть приложения. Она получает файлы и информацию об эксперименте от пользователя. Если пользователь не вводит информацию
используется информация по умолчанию. Далее файлы экспериментов загружаются на fastapi backend. Где обрабатываются и результат обработки возвращается
фронтенду в виде файлов. Эти файлы стримлит отдаёт пользователю.
'''

info = {'sensor_on': ' на демпфере', 'disk_distance': '25 мм', 'washer': '3 мм', 'interval': '1 с',
            'step': '10**-4', 'diameter': '10 мм до 6 мм с удл цч',
            'hole_diameter': '10 мм', 'nozzle_length': '50 мм + 25 мм',
            'insert_variant': '3', 'd_f_between': 'сталь 1200 мм + фланцы',
            'labview_num': '13', 'cs': '', 'compressor': '8 атм', 'sensors': 'дифференциальные датчики на 10 атм'}

absolute = {'sensor_on': 'Датчик на ', 'disk_distance': 'дистанции до диска', 'washer': 'шайба', 'interval': 'интервал',
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

r = requests.post(f"{url}info", json=info)
# print(r.content.encode('cp1251'))
print(r.status_code)
if r.status_code == 200:
    string = r.content.decode('utf-8')
    # print(r.content.decode('utf-8'))

    dictionary = json.loads(string)
    # print(dictionary)
uploaded_files = st.file_uploader("Перетащите сюда и бросьте или выберите текстовый файл экспериментов", type='txt', accept_multiple_files=True)

for uploaded_file in uploaded_files:        
    if uploaded_file is not None:
        files = {'file': uploaded_file}
        response = requests.post(f"{url}upload", files=files)
        new_file_name = uploaded_file.name
        new_file_name = new_file_name.split('_')
        new_file_name = '-'.join(new_file_name[0].split('.')[:2] + new_file_name[-1].split('-')[:1])

        st.download_button(f'Загрузить {new_file_name}.xlsx', response.content, f'{new_file_name}.xlsx')
            
