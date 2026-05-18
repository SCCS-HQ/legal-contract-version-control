#!/usr/bin/env python3
"""API Endpoints for hosted SCCS Repositories"""

import io
import json
import os
import re
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

REPO_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def resolve_path(path: Path) -> Path:
    """Resolve a path and ensure it is not attempting directory traversal."""

    if ".." in path.parts or path.is_absolute():
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not REPO_NAME_PATTERN.fullmatch(path.name):
        raise HTTPException(status_code=400, detail="Invalid repository name")

    return path


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
    repo_name = resolve_path(Path(repo_name))
    base_dir = Path("API/repos").resolve()
    repo_path = (base_dir / repo_name).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository name")

    try:
        remote = json.loads(data)["remote"]
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from e

    if not remote:
        raise HTTPException(status_code=400, detail="Remote URL is required")

    if not Path(Path(file.filename).stem) == repo_name:
        raise HTTPException(
            status_code=400, detail="Repository name does not match file name"
        )

    if repo_path.exists():
        raise HTTPException(status_code=400, detail="Repository already exists")

    with zipfile.ZipFile(file.file, "r") as f:
        total_size = sum(file.file_size for file in f.infolist())
        if total_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Uploaded file is too large")
        total_num_files = len(f.infolist())
        for file in f.infolist():
            if file.file_size > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400, detail=f"File {file.filename} is too large"
                )
        if total_num_files > 1000:
            raise HTTPException(
                status_code=400, detail="Too many files in the uploaded zip"
            )

        for file in f.infolist():
            path = Path(base_dir / repo_name / file.filename).resolve()
            try:
                Path(file.filename).relative_to(Path(repo_path))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid file path in zip")

            if file.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "wb") as f_out:

                    f_out.write(f.read(file))
                    while True:
                        chunk = f_out.read(1024 * 1024)
                        if not chunk:
                            break
                        f_out.write(chunk)

    return {"message": "File published successfully", "repository_url": remote}


@app.get("/repos/{repo_name}/clone")
async def clone(repo_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    repo_name = resolve_path(Path(repo_name))
    base_dir = Path("API/repos").resolve()
    repo_path = (base_dir / repo_name).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository name")

    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(status_code=404, detail="Repository not found")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = Path(root) / file
                f.write(filename=file_path, arcname=file_path.relative_to(repo_path))

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment;filename={repo_name}.zip"},
    )


app.mount("/repos", StaticFiles(directory="API/repos"), name="repos")
"""Mount all repositories as static files on the /repos endpoint."""
