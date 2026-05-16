import zipfile

from fastapi import FastAPI, File, UploadFile
from pathlib import Path

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/repos", StaticFiles(directory="API/repos"), name="repos")


@app.get("/")
async def root():
    return {"Boo!"}


@app.post("/publish")
async def publish(file: UploadFile = File(...)):
    with zipfile.ZipFile(file.file, "r") as f:
        f.extractall(f"API/repos/{Path(file.filename).stem}")
    return {
        "message": "File published successfully",
        "clone_link": f"http://127.0.0.1:8000/repos/{Path(file.filename).stem}",
    }, 

