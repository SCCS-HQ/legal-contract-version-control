"""API Endpoints for hosted SCCS Repositories"""

import io
import os
import zipfile

from fastapi import FastAPI, File, UploadFile
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse


app = FastAPI()


@app.get("/")
async def root():
    return {"Boo!"}


@app.post("/publish")
async def publish(file: UploadFile = File(...)):
    """Publish a repository to the hosted API"""
    with zipfile.ZipFile(file.file, "r") as f:
        f.extractall(f"API/repos/{Path(file.filename).stem}")
    return {
        "message": "File published successfully",
        "clone_link": f"http://127.0.0.1:8000/repos/{Path(file.filename).stem}/clone",
    }, 


@app.get("/repos/{repo_name}/clone")
async def clone(repo_name: str):
    """Return a zipped version of a requested repository"""

    if not os.path.exists(f"API/repos/{repo_name}"):
        return {"message": "Repository not found"}, 404

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(f"API/repos/{repo_name}"):
            for file in files:
                f.write(filename=Path(root) / file,
                arcname=os.path.relpath(
                    Path(root) / file,
                    f"API/repos/{repo_name}"
                    )
                )
            
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment;filename={repo_name}.zip"}
        )


app.mount("/repos", StaticFiles(directory="API/repos"), name="repos")
"""Mount all repositories as static files on the /repos endpoint."""