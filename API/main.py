#!/usr/bin/env python3
"""API Endpoints for hosted SCCS Repositories"""

import io
import json
import os
import re
import tempfile
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


def ensure_repository_exists(repo_name: Path) -> None:
    """Ensure that the specified repository exists and is a directory."""

    repo_path = Path("API/repos").resolve() / repo_name

    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(
            status_code=404, detail=f"Repository not found: {repo_name}"
        )


def safe_extract_zip(zf, member, dest):
    entry_path = Path(member)
    if entry_path.is_absolute() or ".." in entry_path.parts:
        raise HTTPException(status_code=400, detail="Invalid file path in zip")
    target_path = Path(os.path.normpath(dest / entry_path))
    try:
        target_path.relative_to(Path(dest).resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path in zip")
    if zf.getinfo(member).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
    zf.extract(member, path=dest)


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
    repo_path = Path(base_dir / repo_name).resolve()

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

    with zipfile.ZipFile(file.file, "r") as zf:
        total_size = sum(i.file_size for i in zf.infolist())
        if len(zf.infolist()) > 1000:
            raise HTTPException(
                status_code=400, detail="Too many files in the uploaded zip"
            )
        if total_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Uploaded file is too large")

        for i in zf.infolist():
            if i.file_size > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400, detail=f"File {i.filename} is too large"
                )

            safe_extract_zip(zf, i.filename, repo_path)

    return {"message": "File published successfully", "repository_url": remote}


@app.get("/repos/{repo_name}/clone")
async def clone(repo_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    repo_name = resolve_path(Path(repo_name))
    ensure_repository_exists(repo_name)
    base_dir = Path("API/repos").resolve()
    repo_path = (base_dir / repo_name).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository name")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(repo_path):
            for i in files:
                file_path = Path(root) / i
                zf.write(filename=file_path, arcname=file_path.relative_to(repo_path))

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment;filename={repo_name}.zip"},
    )


@app.get("/repos/{repo_name}/push")
async def push(repo_name: str) -> dict:
    """
    Return the folder layout of a requested repository so that the client only needs to
    upload changed files and new files.
    """

    repo_name = resolve_path(Path(repo_name))
    ensure_repository_exists(repo_name)
    base_dir = Path("API/repos").resolve()
    repo_path = (base_dir / repo_name / ".sccs").resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository name")

    objects_dir = repo_path / "objects"

    if not objects_dir.exists() or not objects_dir.is_dir():
        raise HTTPException(status_code=404, detail="Repository objects not found")

    objects = list(set(i.stem for i in objects_dir.rglob("*") if i.is_file()))

    return {"objects": objects}


@app.post("/repos/{repo_name}/push")
async def push_upload(repo_name: str, file: UploadFile = File(...)) -> dict:
    """
    Accept a zip archives of new objects to upload to the selected repository, and a zip
    archive of the updated metadata files. Extract the files from the archives, defend
    against zip slip attacks, and copy the files to the repository atomically.
    """

    repo_name = resolve_path(Path(repo_name))
    ensure_repository_exists(repo_name)
    base_dir = Path("API/repos").resolve()
    repo_path = (base_dir / repo_name).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository name")

    if not file.filename or Path(Path(file.filename).stem) != repo_name:
        raise HTTPException(
            status_code=400, detail="Repository name does not match file name"
        )

    with zipfile.ZipFile(file.file, "r") as zf:
        buffer_dir = Path(os.path.join(tempfile.gettempdir(), f"tmp_{repo_name}"))
        buffer_dir.mkdir(parents=True, exist_ok=True)
        total_size = sum(i.file_size for i in zf.infolist())
        if total_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Uploaded file is too large")
        if len(zf.infolist()) > 1000:
            raise HTTPException(
                status_code=400, detail="Too many files in the uploaded zip"
            )
        for info in zf.infolist():
            if info.file_size > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400, detail=f"File {info.filename} is too large"
                )

            safe_extract_zip(zf, info.filename, buffer_dir)

        # Copy extracted files from temp buffer into repository
        for root, dirs, files in os.walk(buffer_dir):
            for file_name in files:
                src_file = Path(root) / file_name
                rel_path = src_file.relative_to(buffer_dir)
                dest_file = repo_path / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(str(src_file), str(dest_file))
        # Preserve directory structures from zip
        for root, dirs, files in os.walk(buffer_dir):
            for d in dirs:
                dir_path = Path(root) / d
                rel_dir = dir_path.relative_to(buffer_dir)
                (repo_path / rel_dir).mkdir(parents=True, exist_ok=True)

    with open(
        repo_path / ".sccs" / "current_branch" / "current_branch.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    temp_file = repo_path / ".sccs" / "current_branch" / "current_branch.json.tmp"
    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as f:
        data["updated_branches"] = []
        json.dump(data, f, indent=4)
    temp_file.replace(repo_path / ".sccs" / "current_branch" / "current_branch.json")

    return {"message": "changes pushed successfully"}


@app.post("/repos/{repo_name}/pull")
async def pull(repo_name: str, data: dict) -> StreamingResponse:
    """
    Send a zip archive of commit objects and metadata files that the local repository
    (caller) is missing by accepting a list of commit objects that the local doesn't
    have.
    """

    repo_name = resolve_path(Path(repo_name))
    ensure_repository_exists(repo_name)

    repo_path = (Path("API/repos").resolve() / repo_name).resolve()

    if (
        not isinstance(data, dict)
        or "objects" not in data
        or not isinstance(data["objects"], list)
    ):
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    local_objects = set(data["objects"])

    objects_paths = Path(os.path.normpath(repo_path / ".sccs" / "objects"))

    try:
        objects_paths.relative_to(repo_path)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository name")

    remote_objects = set(i.stem for i in (objects_paths).rglob("*") if i.is_file())

    obj_to_upload = remote_objects - local_objects

    if local_objects - remote_objects:
        raise HTTPException(
            status_code=400,
            detail=(
                "Local repository has objects that the remote does not have. Run 'sccs push"
                "' to upload these objects before pulling."
            ),
        )

    document_path = [repo_path / f"{repo_path.name}.docx"]
    current_branch_path = [
        repo_path / ".sccs" / "current_branch" / "current_branch.json"
    ]
    commit_msgs_path = [
        repo_path / ".sccs" / "commit_messages" / "commit_messages.json"
    ]

    individual_objects_paths = [
        i.resolve()
        for i in (objects_paths).rglob("*")
        if i.is_file() and i.stem in obj_to_upload
    ]

    branches_path = Path(os.path.normpath(repo_path / ".sccs" / "branches"))

    try:
        branches_path.relative_to(repo_path)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid repository name")

    history_paths = [
        i.resolve()
        for i in (branches_path).rglob("*")
        if i.is_file() and i.stem == "history"
    ]
    byte_hash_paths = [
        i.resolve()
        for i in (branches_path).rglob("*")
        if i.is_file() and i.stem == "commit_file_hash"
    ]

    files_to_upload = (
        i
        for i in individual_objects_paths
        + history_paths
        + byte_hash_paths
        + document_path
        + current_branch_path
        + commit_msgs_path
        if i.is_file()
    )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in files_to_upload:
            zf.write(filename=i, arcname=i.relative_to(repo_path))
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={repo_name}.zip"},
    )


app.mount("/repos", StaticFiles(directory="API/repos"), name="repos")
"""Mount all repositories as static files on the /repos endpoint."""
