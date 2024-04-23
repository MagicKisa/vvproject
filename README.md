# Приложение поднято по ссылке

https://vvproject.streamlit.app/

# Поднять у себя

```
pip install -r requirements.txt
streamlit run main.py
```

далее открываем ссылку, которая будет выведена в консоль

# Как это работает?

https://docs.streamlit.io/get-started

# За что отвечают файлы в директории?

## form_data.json - содержит данные по умолчанию из этой формы

![image](https://github.com/MagicKisa/vvproject/assets/105859497/eae82ffd-4b72-4b28-bd25-5e5ed5633ef1)

**Если открыть файл в текстовом редакторе вместо русских букв будут числа - это кодировка, так и должно быть**

## main.py - основной файл, содержит графический интерфейс, позволяет скачивать и закачивать файлы и вызывает вспомогательные функции из utils.py

## utils.py - содержит вспомогательные функции которые нужны для обработки входящих файлов и создания результата

## requirements.txt - содержит названия библиотек необходимых для работы

## .gitignore - содержит команды позволяющие git не отслеживать некоторые файлы/директории и т.д.


