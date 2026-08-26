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

REPOSITORY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")

REPOSITORIES_BASE_DIRECTORY = "API/repos"
SCCS_DIRECTORY = ".sccs"
OBJECTS_DIRECTORY = "objects"
BRANCHES_DIRECTORY = "branches"
CURRENT_BRANCH_DIRECTORY = "current_branch"
CURRENT_BRANCH_FILE = "current_branch.json"
CURRENT_BRANCH_TEMPORARY_FILE = "current_branch.json.tmp"
COMMIT_MESSAGES_DIRECTORY = "commit_messages"
COMMIT_MESSAGES_FILE = "commit_messages.json"
DOCUMENT_FILE_TEMPLATE = "{repository_name}.docx"
TEMPORARY_DIRECTORY_PREFIX = "tmp_"
STATIC_FILES_NAME = "repos"
HISTORY_FILE_STEM = "history"
COMMIT_BYTE_HASH_STEM = "commit_file_hash"

MAX_FILES_IN_ZIP = 1000
MAX_TOTAL_UPLOAD_SIZE = 100 * 1024 * 1024
MAX_INDIVIDUAL_FILE_SIZE = 10 * 1024 * 1024
JSON_DUMP_INDENT = 4

EASTER_EGG_MESSAGE = "Boo!"
ERROR_INVALID_FILE_PATH = "Invalid file path"
ERROR_INVALID_REPOSITORY_NAME = "Invalid repository name"
ERROR_REPOSITORY_NOT_FOUND = "Repository not found: {repository_name}"
ERROR_INVALID_ZIP_PATH = "Invalid file path in zip"
ERROR_INVALID_JSON = "Invalid JSON data"
ERROR_REMOTE_URL_REQUIRED = "Remote URL is required"
ERROR_REPOSITORY_NAME_MISMATCH = "Repository name does not match file name"
ERROR_REPOSITORY_EXISTS = "Repository already exists"
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

CONTENT_DISPOSITION_HEADER = "attachment;filename={repository_name}.zip"
CONTENT_DISPOSITION_HEADER_SPACED = "attachment; filename={repository_name}.zip"


def validate_repository_name(repository_name: str) -> str:
    """Validate a user-provided repository name against the allowed pattern."""

    if (
        not repository_name
        or not REPOSITORY_NAME_PATTERN.fullmatch(repository_name)
        or repository_name in (".", "..")
    ):
        raise HTTPException(status_code=400, detail=ERROR_INVALID_REPOSITORY_NAME)
    return repository_name


def repository_base_directory() -> Path:
    """Return the fully-resolved base directory that holds all repositories."""

    return Path(REPOSITORIES_BASE_DIRECTORY).resolve()


def repository_directory(repository_name: str) -> Path:
    """
    Build the fully-resolved directory for a validated repository name and
    guarantee it stays inside the repositories base directory.
    """

    validate_repository_name(repository_name)
    base_directory = repository_base_directory()
    repository_path = (base_directory / repository_name).resolve()

    try:
        repository_path.relative_to(base_directory)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=ERROR_INVALID_REPOSITORY_NAME
        ) from e

    return repository_path


def ensure_repository_exists(repository_path: Path) -> None:
    """Ensure that the specified repository exists and is a directory."""

    if not repository_path.exists() or not repository_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail=ERROR_REPOSITORY_NOT_FOUND.format(
                repository_name=repository_path.name
            ),
        )


def safe_extract_zip(
    zip_archive: zipfile.ZipFile, member_path: str, destination_directory: Path
) -> None:
    destination_resolved = destination_directory.resolve()
    entry_path = Path(member_path)
    if entry_path.is_absolute() or ".." in entry_path.parts:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_ZIP_PATH)
    target_path = Path(os.path.normpath(destination_directory / entry_path)).resolve()
    try:
        target_path.relative_to(destination_resolved)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_ZIP_PATH) from e
    if zip_archive.getinfo(member_path).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with zip_archive.open(member_path) as source, open(target_path, "wb") as f:
            shutil.copyfileobj(source, f)


app = FastAPI()


@app.get("/")
async def root() -> dict:
    """Easter Egg Endpoint - Do Not Remove"""

    return {JSON_KEY_MESSAGE: EASTER_EGG_MESSAGE}


@app.post("/repos/{repository_name}/publish")
async def publish(
    repository_name: str, file: UploadFile = File(...), data: str = Form(...)
) -> dict:
    """Publish a repository to the hosted API"""

    repository_path = repository_directory(repository_name)

    try:
        remote = json.loads(data)["remote"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=ERROR_INVALID_JSON) from e

    if not remote:
        raise HTTPException(status_code=400, detail=ERROR_REMOTE_URL_REQUIRED)

    if not file.filename or Path(file.filename).stem != repository_name:
        raise HTTPException(status_code=400, detail=ERROR_REPOSITORY_NAME_MISMATCH)

    if repository_path.exists():
        raise HTTPException(status_code=400, detail=ERROR_REPOSITORY_EXISTS)

    with zipfile.ZipFile(file.file, "r") as zip_archive:
        if len(zip_archive.infolist()) > MAX_FILES_IN_ZIP:
            raise HTTPException(status_code=400, detail=ERROR_TOO_MANY_FILES)
        if sum(i.file_size for i in zip_archive.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=ERROR_UPLOAD_TOO_LARGE)

        for i in zip_archive.infolist():
            if i.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=ERROR_FILE_TOO_LARGE.format(filename=i.filename),
                )

            safe_extract_zip(zip_archive, i.filename, repository_path)

    return {
        JSON_KEY_MESSAGE: MESSAGE_FILE_PUBLISHED,
        JSON_KEY_REPOSITORY_URL: remote,
    }


@app.get("/repos/{repository_name}/clone")
async def clone(repository_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    repository_path = repository_directory(repository_name)
    ensure_repository_exists(repository_path)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive:
        for root, dirs, files in os.walk(repository_path):
            for i in files:
                file_path = Path(root) / i
                zip_archive.write(
                    filename=file_path, arcname=file_path.relative_to(repository_path)
                )

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": CONTENT_DISPOSITION_HEADER.format(
                repository_name=repository_name
            )
        },
    )


@app.get("/repos/{repository_name}/push")
async def push(repository_name: str) -> dict:
    """
    Return the folder layout of a requested repository so that the client only needs to
    upload changed files and new files.
    """

    repository_path = (
        repository_directory(repository_name) / SCCS_DIRECTORY
    ).resolve()

    objects_directory = repository_path / OBJECTS_DIRECTORY

    if not objects_directory.exists() or not objects_directory.is_dir():
        raise HTTPException(status_code=404, detail=ERROR_OBJECTS_NOT_FOUND)

    return {
        JSON_KEY_OBJECTS: list(
            set(i.stem for i in objects_directory.rglob("*") if i.is_file())
        )
    }


@app.post("/repos/{repository_name}/push")
async def push_upload(repository_name: str, file: UploadFile = File(...)) -> dict:
    """
    Accept a zip archives of new objects to upload to the selected repository, and a zip
    archive of the updated metadata files. Extract the files from the archives, defend
    against zip slip attacks, and copy the files to the repository atomically.
    """

    repository_path = repository_directory(repository_name)

    if not file.filename or Path(file.filename).stem != repository_name:
        raise HTTPException(status_code=400, detail=ERROR_REPOSITORY_NAME_MISMATCH)

    zip_buffer_directory = Path(
        tempfile.gettempdir(),
        TEMPORARY_DIRECTORY_PREFIX + repository_name,
    )

    with zipfile.ZipFile(file.file, "r") as zip_archive:
        if sum(i.file_size for i in zip_archive.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
            shutil.rmtree(zip_buffer_directory, ignore_errors=True)
            raise HTTPException(status_code=400, detail=ERROR_UPLOAD_TOO_LARGE)
        if len(zip_archive.infolist()) > MAX_FILES_IN_ZIP:
            shutil.rmtree(zip_buffer_directory, ignore_errors=True)
            raise HTTPException(status_code=400, detail=ERROR_TOO_MANY_FILES)
        zip_buffer_directory.mkdir(parents=True, exist_ok=True)
        for info in zip_archive.infolist():
            if info.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                shutil.rmtree(zip_buffer_directory, ignore_errors=True)
                raise HTTPException(
                    status_code=400,
                    detail=ERROR_FILE_TOO_LARGE.format(filename=info.filename),
                )
            safe_extract_zip(zip_archive, info.filename, zip_buffer_directory)

        try:
            for root, dirs, files in os.walk(zip_buffer_directory):
                for i in files:
                    source_file = Path(root) / i
                    destination_file = Path(
                        *[
                            i
                            for i in Path(
                                repository_path
                                / source_file.relative_to(zip_buffer_directory)
                            ).parts
                            if not i.startswith(TEMPORARY_DIRECTORY_PREFIX)
                        ]
                    ).resolve()
                    try:
                        destination_file.relative_to(repository_path)
                    except ValueError as e:
                        raise HTTPException(
                            status_code=400, detail=ERROR_INVALID_ZIP_PATH
                        ) from e
                    destination_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(source_file), str(destination_file))
        finally:
            shutil.rmtree(zip_buffer_directory, ignore_errors=True)

    with open(
        repository_path
        / SCCS_DIRECTORY
        / CURRENT_BRANCH_DIRECTORY
        / CURRENT_BRANCH_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    temporary_file = (
        repository_path
        / SCCS_DIRECTORY
        / CURRENT_BRANCH_DIRECTORY
        / CURRENT_BRANCH_TEMPORARY_FILE
    )
    with open(
        temporary_file,
        "w",
        encoding="utf-8",
    ) as f:
        data[JSON_KEY_UPDATED_BRANCHES] = []
        json.dump(data, f, indent=JSON_DUMP_INDENT)
    temporary_file.replace(
        repository_path
        / SCCS_DIRECTORY
        / CURRENT_BRANCH_DIRECTORY
        / CURRENT_BRANCH_FILE
    )

    return {JSON_KEY_MESSAGE: MESSAGE_PUSH_SUCCESS}


@app.post("/repos/{repository_name}/pull")
async def pull(repository_name: str, data: dict) -> StreamingResponse:
    """
    Send a zip archive of commit objects and metadata files that the local repository
    (caller) is missing by accepting a list of commit objects that the local doesn't
    have.
    """

    repository_path = repository_directory(repository_name)
    ensure_repository_exists(repository_path)

    if (
        not isinstance(data, dict)
        or JSON_KEY_OBJECTS not in data
        or not isinstance(data[JSON_KEY_OBJECTS], list)
    ):
        raise HTTPException(status_code=400, detail=ERROR_INVALID_JSON)

    local_objects = set(data[JSON_KEY_OBJECTS])

    objects_paths = (repository_path / SCCS_DIRECTORY / OBJECTS_DIRECTORY).resolve()

    try:
        objects_paths.relative_to(repository_path)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=ERROR_INVALID_REPOSITORY_NAME
        ) from e

    remote_objects = set(i.stem for i in (objects_paths).rglob("*") if i.is_file())

    if local_objects - remote_objects:
        raise HTTPException(
            status_code=400,
            detail=ERROR_LOCAL_UNKNOWN_OBJECTS,
        )

    branches_path = (repository_path / SCCS_DIRECTORY / BRANCHES_DIRECTORY).resolve()

    try:
        branches_path.relative_to(repository_path)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=ERROR_INVALID_REPOSITORY_NAME
        ) from e

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
            if i.is_file() and i.stem == COMMIT_BYTE_HASH_STEM
        ]
        + [
            repository_path
            / DOCUMENT_FILE_TEMPLATE.format(repository_name=repository_path.name)
        ]
        + [
            repository_path
            / SCCS_DIRECTORY
            / CURRENT_BRANCH_DIRECTORY
            / CURRENT_BRANCH_FILE
        ]
        + [
            repository_path
            / SCCS_DIRECTORY
            / COMMIT_MESSAGES_DIRECTORY
            / COMMIT_MESSAGES_FILE
        ]
        if i.is_file()
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive:
        for i in files_to_upload:
            zip_archive.write(filename=i, arcname=i.relative_to(repository_path))
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": CONTENT_DISPOSITION_HEADER_SPACED.format(
                repository_name=repository_name
            )
        },
    )


app.mount(
    "/repos", StaticFiles(directory=REPOSITORIES_BASE_DIRECTORY), name=STATIC_FILES_NAME
)
"""Mount all repositories as static files on the /repos endpoint."""
