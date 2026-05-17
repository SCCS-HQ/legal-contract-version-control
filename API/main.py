#!/usr/bin/env python3
"""API Endpoints for hosted SCCS Repositories"""

import io
import os
import zipfile
from pathlib import Path

import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/")
async def root() -> dict:
    """Easter Egg Endpoint - Do Not Remove"""

    return {"message": "Boo!"}


@app.post("/repos/{repo_name}/publish")
async def publish(
    repo_name: str, file: UploadFile = File(...)
) -> dict:
    """Publish a repository to the hosted API"""

    if not Path(file.filename).stem == repo_name:
        return {"message": "Repository name mismatch"}, 400
    
    if Path(file.filename).stem in os.listdir("API/repos"):
        return {"message": "Repository already exists"}, 400

    with zipfile.ZipFile(file.file, "r") as f:
        for file in f.infolist():
            if ".." in file.filename or file.filename.startswith("/"):
                return {"message": "Invalid file path in zip"}, 400

        f.extractall(f"API/repos/{Path(file.filename).stem}")
    return {
        "message": "File published successfully",
        "repository_url": f"http://127.0.0.1:8000/repos/{Path(file.filename).stem}",
    }


@app.get("/repos/{repo_name}/clone")
async def clone(repo_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    if ".." in repo_name or repo_name.startswith("/"):
        return {"message": "Invalid repository name"}, 400

    if not os.path.exists(f"API/repos/{repo_name}"):
        return {"message": "Repository not found"}, 404

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(f"API/repos/{repo_name}"):
            for file in files:
                f.write(
                    filename=Path(root) / file,
                    arcname=os.path.relpath(
                        Path(root) / file, f"API/repos/{repo_name}"
                    ),
                )

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment;filename={repo_name}.zip"},
    )


app.mount("/repos", StaticFiles(directory="API/repos"), name="repos")
"""Mount all repositories as static files on the /repos endpoint."""
