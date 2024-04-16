from txt_to_xlsx import create_excel_by_txt, read_mean_parameters
from fastapi import FastAPI, Request
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json

'''
Здесь находится бэкенд-часть приложения, она получает текстовые файлы пользователя от Streamlit с помощью пост запроса
далее с помощью процедуры create_excel_by_txt на основе текстового файла создаётся xlsx файл, удовлетворяющий требованиям научного сотрудника.
Полученный файл возвращается streamlit-у ответом на пост запрос 
'''


class Info(BaseModel):
    sensor_on: str
    disk_distance: str
    washer: str
    interval: str
    step: str
    diameter: str
    hole_diameter: str
    nozzle_length: str
    insert_variant: str
    d_f_between: str
    labview_num: str
    cs: str
    compressor: str
    sensors: str


app = FastAPI()
app.state.experiment_info = {}

@app.post("/upload")
async def upload(file: UploadFile):
    try:
        contents = await file.read()
        with open(f"{file.filename}", 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

#    app.state.files[file.filename] = file

    return FileResponse(x)

@app.get("/download/{filename}")
async def download(filename: str):
    x = create_excel_by_txt(filename, app.state.experiment_info)
    return FileResponse(x)

@app.post('/info')
async def update_info(data: Info):
    app.state.experiment_info = json.loads(data.json())
    return app.state.experiment_info


@app.get('/')
async def root():
    return {'message': "it's up"}
