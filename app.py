from txt_to_xlsx import create_excel_by_txt, read_mean_parameters
from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()
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

    x = create_excel_by_txt(file.filename)

    return FileResponse(x)

@app.get("/download")
async def download():
    return FileResponse('file.xlsx')

@app.get('/')
async def root():
    return {'message': "it's up"}
