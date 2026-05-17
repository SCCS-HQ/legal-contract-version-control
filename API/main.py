#!/usr/bin/env python3
"""API Endpoints for hosted SCCS Repositories"""

import io
import os
import zipfile
from pathlib import Path
import json

import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/")
async def root() -> dict:
    """Easter Egg Endpoint - Do Not Remove"""

    return {"message": "Boo!"}


@app.post("/repos/{repo_name}/publish")
async def publish(
    repo_name: str, file: UploadFile = File(...), data: str = Form(...)
) -> dict:
    """Publish a repository to the hosted API"""
    
    try: remote = json.loads(data)["remote"]
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from e

    if not remote:
        raise HTTPException(status_code=400, detail="Remote URL is required")

    if not Path(file.filename).stem == repo_name:
        raise HTTPException(
            status_code=400, detail="Repository name does not match file name"
        )
    
    if Path(file.filename).stem in os.listdir("API/repos"):
        raise HTTPException(
            status_code=400, detail="Repository already exists"
        )

    with zipfile.ZipFile(file.file, "r") as f:
        for file in f.infolist():
            if ".." in file.filename or file.filename.startswith("/"):
                raise HTTPException(
                    status_code=400, detail="Invalid file path in zip"
                )
        f.extractall(f"API/repos/{repo_name}")

    return {
        "message": "File published successfully",
        "repository_url": remote
    }


@app.get("/repos/{repo_name}/clone")
async def clone(repo_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    if ".." in repo_name or repo_name.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid repository name")

    if not os.path.exists(f"API/repos/{repo_name}"):
        raise HTTPException(status_code=404, detail="Repository not found")

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
