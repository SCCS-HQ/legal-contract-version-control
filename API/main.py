#!/usr/bin/env python3
"""API Endpoints for hosted SCCS Repositories"""

import io
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

REPO_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")

REPOS_BASE_DIR = "API/repos"
SCCS_DIR = ".sccs"
OBJECTS_DIR = "objects"
BRANCHES_DIR = "branches"
CURRENT_BRANCH_DIR = "current_branch"
CURRENT_BRANCH_FILE = "current_branch.json"
CURRENT_BRANCH_TEMP_FILE = "current_branch.json.tmp"
COMMIT_MESSAGES_DIR = "commit_messages"
COMMIT_MESSAGES_FILE = "commit_messages.json"
DOCUMENT_FILE_TEMPLATE = "{repo_name}.docx"
TEMP_DIR_PREFIX = "tmp_"
STATIC_FILES_NAME = "repos"
HISTORY_FILE_STEM = "history"
COMMIT_FILE_HASH_STEM = "commit_file_hash"

MAX_FILES_IN_ZIP = 1000
MAX_TOTAL_UPLOAD_SIZE = 100 * 1024 * 1024
MAX_INDIVIDUAL_FILE_SIZE = 10 * 1024 * 1024
JSON_DUMP_INDENT = 4

EASTER_EGG_MESSAGE = "Boo!"
ERROR_INVALID_FILE_PATH = "Invalid file path"
ERROR_INVALID_REPO_NAME = "Invalid repository name"
ERROR_REPO_NOT_FOUND = "Repository not found: {repo_name}"
ERROR_INVALID_ZIP_PATH = "Invalid file path in zip"
ERROR_INVALID_JSON = "Invalid JSON data"
ERROR_REMOTE_URL_REQUIRED = "Remote URL is required"
ERROR_REPO_NAME_MISMATCH = "Repository name does not match file name"
ERROR_REPO_EXISTS = "Repository already exists"
ERROR_TOO_MANY_FILES = "Too many files in the uploaded zip"
ERROR_UPLOAD_TOO_LARGE = "Uploaded file is too large"
ERROR_FILE_TOO_LARGE = "File {filename} is too large"
ERROR_OBJECTS_NOT_FOUND = "Repository objects not found"
ERROR_LOCAL_UNKNOWN_OBJECTS = (
    "Local repository has objects that the remote does not have. Run 'sccs push"
    "' to upload these objects before pulling."
)
MESSAGE_PUSH_SUCCESS = "changes pushed successfully"
MESSAGE_FILE_PUBLISHED = "File published successfully"

JSON_KEY_MESSAGE = "message"
JSON_KEY_REPOSITORY_URL = "repository_url"
JSON_KEY_OBJECTS = "objects"
JSON_KEY_UPDATED_BRANCHES = "updated_branches"

CONTENT_DISPOSITION_HEADER = "attachment;filename={repo_name}.zip"
CONTENT_DISPOSITION_HEADER_SPACED = "attachment; filename={repo_name}.zip"


def resolve_path(path: Path) -> Path:
    """Resolve a path and ensure it is not attempting directory traversal."""

    if ".." in path.parts or path.is_absolute():
        raise HTTPException(status_code=400, detail=ERROR_INVALID_FILE_PATH)

    if not REPO_NAME_PATTERN.fullmatch(path.name):
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

    return path


def ensure_repository_exists(repo_name: Path) -> None:
    """Ensure that the specified repository exists and is a directory."""

    repo_path = Path(REPOS_BASE_DIR).resolve() / repo_name

    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(
            status_code=404, detail=ERROR_REPO_NOT_FOUND.format(repo_name=repo_name)
        )


def safe_extract_zip(zf: zipfile.ZipFile, member: str, dest: Path) -> None:
    entry_path = Path(member)
    if entry_path.is_absolute() or ".." in entry_path.parts:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_ZIP_PATH)
    target_path = Path(os.path.normpath(dest / entry_path))
    try:
        (target_path.resolve()).relative_to(Path(dest).resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_ZIP_PATH)
    if zf.getinfo(member).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
    zf.extract(member, path=dest)


app = FastAPI()


@app.get("/")
async def root() -> dict:
    """Easter Egg Endpoint - Do Not Remove"""

    return {JSON_KEY_MESSAGE: EASTER_EGG_MESSAGE}


@app.post("/repos/{repo_name}/publish")
async def publish(
    repo_name: str, file: UploadFile = File(...), data: str = Form(...)
) -> dict:
    """Publish a repository to the hosted API"""

    base_dir = Path(REPOS_BASE_DIR).resolve()
    repo_path = Path(base_dir / resolve_path(Path(repo_name))).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

    try:
        remote = json.loads(data)["remote"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_JSON) from e

    if not remote:
        raise HTTPException(status_code=400, detail=ERROR_REMOTE_URL_REQUIRED)

    if not file.filename or Path(file.filename).stem != repo_name:
        raise HTTPException(status_code=400, detail=ERROR_REPO_NAME_MISMATCH)

    if repo_path.exists():
        raise HTTPException(status_code=400, detail=ERROR_REPO_EXISTS)

    with zipfile.ZipFile(file.file, "r") as zf:
        if len(zf.infolist()) > MAX_FILES_IN_ZIP:
            raise HTTPException(status_code=400, detail=ERROR_TOO_MANY_FILES)
        if sum(i.file_size for i in zf.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=ERROR_UPLOAD_TOO_LARGE)

        for i in zf.infolist():
            if i.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=ERROR_FILE_TOO_LARGE.format(filename=i.filename),
                )

            safe_extract_zip(zf, i.filename, repo_path)

    return {
        JSON_KEY_MESSAGE: MESSAGE_FILE_PUBLISHED,
        JSON_KEY_REPOSITORY_URL: remote,
    }


@app.get("/repos/{repo_name}/clone")
async def clone(repo_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    resolved_repo_name = resolve_path(Path(repo_name))
    ensure_repository_exists(resolved_repo_name)
    base_dir = Path(REPOS_BASE_DIR).resolve()
    repo_path = (base_dir / resolved_repo_name).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

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
        headers={
            "Content-Disposition": CONTENT_DISPOSITION_HEADER.format(
                repo_name=resolved_repo_name
            )
        },
    )


@app.get("/repos/{repo_name}/push")
async def push(repo_name: str) -> dict:
    """
    Return the folder layout of a requested repository so that the client only needs to
    upload changed files and new files.
    """

    resolved_repo_name = resolve_path(Path(repo_name))

    ensure_repository_exists(resolved_repo_name)
    base_dir = Path(REPOS_BASE_DIR).resolve()
    repo_path = (base_dir / resolved_repo_name / SCCS_DIR).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

    objects_dir = repo_path / OBJECTS_DIR

    if not objects_dir.exists() or not objects_dir.is_dir():
        raise HTTPException(status_code=404, detail=ERROR_OBJECTS_NOT_FOUND)

    return {
        JSON_KEY_OBJECTS: list(
            set(i.stem for i in objects_dir.rglob("*") if i.is_file())
        )
    }


@app.post("/repos/{repo_name}/push")
async def push_upload(repo_name: str, file: UploadFile = File(...)) -> dict:
    """
    Accept a zip archives of new objects to upload to the selected repository, and a zip
    archive of the updated metadata files. Extract the files from the archives, defend
    against zip slip attacks, and copy the files to the repository atomically.
    """

    resolved_repo_name = resolve_path(Path(repo_name))
    ensure_repository_exists(resolved_repo_name)
    base_dir = Path(REPOS_BASE_DIR).resolve()
    repo_path = (base_dir / resolved_repo_name).resolve()

    try:
        repo_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

    if not file.filename or Path(file.filename).stem != repo_name:
        raise HTTPException(status_code=400, detail=ERROR_REPO_NAME_MISMATCH)

    with zipfile.ZipFile(file.file, "r") as zf:
        buffer_dir = Path(
            os.path.join(tempfile.gettempdir(), f"{TEMP_DIR_PREFIX}{repo_name}")
        )

        print(zf.infolist())

        if sum(i.file_size for i in zf.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
            shutil.rmtree(buffer_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=ERROR_UPLOAD_TOO_LARGE)
        if len(zf.infolist()) > MAX_FILES_IN_ZIP:
            shutil.rmtree(buffer_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=ERROR_TOO_MANY_FILES)
        buffer_dir.mkdir(parents=True, exist_ok=True)
        for info in zf.infolist():
            if info.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                shutil.rmtree(buffer_dir, ignore_errors=True)
                raise HTTPException(
                    status_code=400,
                    detail=ERROR_FILE_TOO_LARGE.format(filename=info.filename),
                )
            safe_extract_zip(zf, info.filename, buffer_dir)

        try:
            for root, dirs, files in os.walk(buffer_dir):
                for i in files:
                    src_file = Path(root) / i
                    dest_file = Path(
                        *[
                            i
                            for i in Path(
                                repo_path / src_file.relative_to(buffer_dir)
                            ).parts
                            if not i.startswith(TEMP_DIR_PREFIX)
                        ]
                    )
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(src_file), str(dest_file))
        finally:
            shutil.rmtree(buffer_dir, ignore_errors=True)

    with open(
        repo_path / SCCS_DIR / CURRENT_BRANCH_DIR / CURRENT_BRANCH_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    temp_file = repo_path / SCCS_DIR / CURRENT_BRANCH_DIR / CURRENT_BRANCH_TEMP_FILE
    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as f:
        data[JSON_KEY_UPDATED_BRANCHES] = []
        json.dump(data, f, indent=JSON_DUMP_INDENT)
    temp_file.replace(repo_path / SCCS_DIR / CURRENT_BRANCH_DIR / CURRENT_BRANCH_FILE)

    return {JSON_KEY_MESSAGE: MESSAGE_PUSH_SUCCESS}


@app.post("/repos/{repo_name}/pull")
async def pull(repo_name: str, data: dict) -> StreamingResponse:
    """
    Send a zip archive of commit objects and metadata files that the local repository
    (caller) is missing by accepting a list of commit objects that the local doesn't
    have.
    """

    resolved_repo_name = resolve_path(Path(repo_name))
    ensure_repository_exists(resolved_repo_name)

    repo_path = (Path(REPOS_BASE_DIR).resolve() / resolved_repo_name).resolve()

    if (
        not isinstance(data, dict)
        or JSON_KEY_OBJECTS not in data
        or not isinstance(data[JSON_KEY_OBJECTS], list)
    ):
        raise HTTPException(status_code=400, detail=ERROR_INVALID_JSON)

    local_objects = set(data[JSON_KEY_OBJECTS])

    objects_paths = Path(os.path.normpath(repo_path / SCCS_DIR / OBJECTS_DIR))

    try:
        objects_paths.relative_to(repo_path)
    except ValueError:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

    remote_objects = set(i.stem for i in (objects_paths).rglob("*") if i.is_file())

    if local_objects - remote_objects:
        raise HTTPException(
            status_code=400,
            detail=ERROR_LOCAL_UNKNOWN_OBJECTS,
        )

    branches_path = Path(os.path.normpath(repo_path / SCCS_DIR / BRANCHES_DIR))

    try:
        branches_path.relative_to(repo_path)
    except ValueError:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPO_NAME)

    files_to_upload = (
        i
        for i in [
            i.resolve()
            for i in objects_paths.rglob("*")
            if i.is_file() and i.stem in remote_objects - local_objects
        ]
        + [
            i.resolve()
            for i in (branches_path).rglob("*")
            if i.is_file() and i.stem == HISTORY_FILE_STEM
        ]
        + [
            i.resolve()
            for i in (branches_path).rglob("*")
            if i.is_file() and i.stem == COMMIT_FILE_HASH_STEM
        ]
        + [repo_path / DOCUMENT_FILE_TEMPLATE.format(repo_name=repo_path.name)]
        + [repo_path / SCCS_DIR / CURRENT_BRANCH_DIR / CURRENT_BRANCH_FILE]
        + [repo_path / SCCS_DIR / COMMIT_MESSAGES_DIR / COMMIT_MESSAGES_FILE]
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
        headers={
            "Content-Disposition": CONTENT_DISPOSITION_HEADER_SPACED.format(
                repo_name=repo_name
            )
        },
    )


app.mount("/repos", StaticFiles(directory=REPOS_BASE_DIR), name=STATIC_FILES_NAME)
"""Mount all repositories as static files on the /repos endpoint."""
