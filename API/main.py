#!/usr/bin/env python3
"""API Endpoints for hosted SCCS Repositories"""

import io
import json
import os
import re
import shutil
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

BRANCHES_DIRECTORY = "branches"
CLONE_ENDPOINT_TEMPLATE = "/repos/{repository_name}/clone"
CONTENT_DISPOSITION_HEADER_TITLE = "Content-Disposition"
CONTENT_DISPOSITION_HEADER = "attachment;filename={repository_name}.zip"
CONTENT_DISPOSITION_HEADER_SPACED = "attachment; filename={repository_name}.zip"
CURRENT_BRANCH_DICT_KEY = "current_branch"
DOUBLE_PERIOD = ".."
EASTER_EGG_MESSAGE = "Boo!"
FILE_PUBLISHED_MESSAGE = "File published successfully"
FILE_TOO_LARGE_ERROR_MESSAGE = "File {filename} is too large"
INVALID_JSON_ERROR_MESSAGE = "Invalid JSON data"
INVALID_REPOSITORY_NAME_ERROR_MESSAGE = "Invalid repository name"
INVALID_ZIP_PATH_ERROR_MESSAGE = "Invalid file path in zip"
JSON_KEY_MESSAGE = "message"
JSON_KEY_OBJECTS = "objects"
JSON_KEY_REPOSITORY_URL = "repository_url"
LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE = (
    "Local repository has objects that the remote does not have. Run 'sccs push"
    "' to upload these objects before pulling."
)
MAX_FILES_IN_ZIP = 1000
MAX_INDIVIDUAL_FILE_SIZE = 10 * 1024 * 1024
MAX_TOTAL_UPLOAD_SIZE = 100 * 1024 * 1024
METADATA_JSON = "metadata.json"
NEWLINE = "\n"
OBJECTS_DIRECTORY = "objects"
OBJECTS_NOT_FOUND_ERROR_MESSAGE = "Repository objects not found"
OLD_ROOT_TEMPLATE = f"{{repository_name}}.old-{uuid.uuid4().hex}"
PUBLISH_ENDPOINT_TEMPLATE = "/repos/{repository_name}/publish"
PULL_ENDPOINT_TEMPLATE = "/repos/{repository_name}/pull"
PUSH_ENDPOINT_TEMPLATE = "/repos/{repository_name}/push"
PUSH_SUCCESS_MESSAGE = "changes pushed successfully"
REMOTE_KEY = "remote"
REMOTE_URL_REQUIRED_ERROR_MESSAGE = "Remote URL is required"
REPOSITORIES_BASE_DIRECTORY = "API/repos"
REPOSITORY_EXISTS_ERROR_MESSAGE = "Repository already exists"
REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE = "Repository name dos not match file name"
REPOSITORY_NOT_FOUND_ERROR_MESSAGE = "Repository not found: {repository_name}"
RGLOB_ALL_FILES_PATTERN = "*"
REPOS_MOUNT_ENDPOINT = "/repos"
ROOT_ENDPOINT = "/"
SCCS_DIRECTORY = ".sccs"
SINGLE_PERIOD = "."
STATIC_FILES_NAME = "repos"
TEMPORARY_DIRECTORY_PREFIX = "sccs_temp_"
TOO_MANY_FILES_ERROR_MESSAGE = "Too many files in the uploaded zip"
UPDATED_BRANCHES_DICT_KEY = "updated_branches"
UPLOAD_TOO_LARGE_ERROR_MESSAGE = "Uploaded fie is too large"
UTF_8 = "utf-8"
ZIP_MEDIA_TYPE = "application/zip"


@dataclass(frozen=True, slots=True)
class ValidatedRepositoryName:
    """A repository name validated against the allowed pattern."""

    value: str

    def __post_init__(self) -> None:

        if (
            not self.value
            or not re.fullmatch(r"^[A-Za-z0-9._-]+$", self.value)
            or self.value in (SINGLE_PERIOD, DOUBLE_PERIOD)
        ):
            raise HTTPException(
                status_code=400, detail=INVALID_REPOSITORY_NAME_ERROR_MESSAGE
            )

    def __str__(self) -> str:

        return self.value


def validate_repository_name(repository_name: str) -> ValidatedRepositoryName:
    """Validate a user-provided repository name against the allowed pattern."""

    return ValidatedRepositoryName(repository_name)


def repository_base_directory() -> Path:
    """Return the fully-resolved base directory that holds all repositories."""

    return Path(REPOSITORIES_BASE_DIRECTORY).resolve()


def repository_directory(repository_name: str) -> Path:
    """
    Build the fully-resolved directory for a validated repository name and
    guarantee it stays inside the repositories base directory.
    """

    safe = validate_repository_name(repository_name)  # returns ValidatedRepositoryName
    base_directory = repository_base_directory()
    repository_path = (base_directory / str(safe)).resolve()  #

    try:
        repository_path.relative_to(base_directory)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=INVALID_REPOSITORY_NAME_ERROR_MESSAGE
        ) from e

    return repository_path


def ensure_repository_exists(repository_path: Path) -> None:
    """Ensure that the specified repository exists and is a directory."""

    if not repository_path.exists() or not repository_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail=REPOSITORY_NOT_FOUND_ERROR_MESSAGE.format(
                repository_name=repository_path.name
            ),
        )


def safe_extract_zip(
    zip_archive: zipfile.ZipFile, member_path: str, destination_directory: Path
) -> None:

    destination_resolved = destination_directory.resolve()
    entry_path = Path(member_path)
    if entry_path.is_absolute() or DOUBLE_PERIOD in entry_path.parts:
        raise HTTPException(status_code=400, detail=INVALID_ZIP_PATH_ERROR_MESSAGE)
    target_path = Path(os.path.normpath(destination_directory / entry_path)).resolve()
    try:
        target_path.relative_to(destination_resolved)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=INVALID_ZIP_PATH_ERROR_MESSAGE
        ) from e
    if zip_archive.getinfo(member_path).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with zip_archive.open(member_path) as source, open(target_path, "wb") as f:
            shutil.copyfileobj(source, f)


app = FastAPI()


@app.get(ROOT_ENDPOINT)
async def root() -> dict:
    """Easter Egg Endpoint - Do Not Remove"""

    return {JSON_KEY_MESSAGE: EASTER_EGG_MESSAGE}


@app.post(PUBLISH_ENDPOINT_TEMPLATE)
async def publish(
    repository_name: str, file: UploadFile = File(...), data: str = Form(...)
) -> dict:
    """Publish a repository to the hosted API"""

    repository_path = repository_directory(repository_name)

    if repository_path.exists():
        raise HTTPException(status_code=400, detail=REPOSITORY_EXISTS_ERROR_MESSAGE)

    staging_root = Path(
        tempfile.mkdtemp(prefix=TEMPORARY_DIRECTORY_PREFIX, dir=repository_path.parent)
    )

    try:
        try:
            remote = json.loads(data)[REMOTE_KEY]
        except (json.JSONDecodeError, KeyError) as e:
            raise HTTPException(
                status_code=400, detail=INVALID_JSON_ERROR_MESSAGE
            ) from e

        if not remote:
            raise HTTPException(
                status_code=400, detail=REMOTE_URL_REQUIRED_ERROR_MESSAGE
            )

        if not file.filename or Path(file.filename).stem != repository_name:
            raise HTTPException(
                status_code=400, detail=REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE
            )

        with zipfile.ZipFile(file.file, "r") as zf:
            if len(zf.infolist()) > MAX_FILES_IN_ZIP:
                raise HTTPException(
                    status_code=400, detail=TOO_MANY_FILES_ERROR_MESSAGE
                )
            if sum(i.file_size for i in zf.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400, detail=UPLOAD_TOO_LARGE_ERROR_MESSAGE
                )

            for i in zf.infolist():
                if i.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail=FILE_TOO_LARGE_ERROR_MESSAGE.format(filename=i.filename),
                    )

                safe_extract_zip(zf, i.filename, staging_root)

        os.replace(staging_root, repository_path)

    except Exception:
        shutil.rmtree(staging_root, ignore_errors=True)

        raise

    return {JSON_KEY_MESSAGE: FILE_PUBLISHED_MESSAGE, JSON_KEY_REPOSITORY_URL: remote}


@app.get(CLONE_ENDPOINT_TEMPLATE)
async def clone(repository_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    repository_path = repository_directory(repository_name)
    ensure_repository_exists(repository_path)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(repository_path):
            for i in files:
                file_path = Path(root) / i
                zf.write(
                    filename=file_path, arcname=file_path.relative_to(repository_path)
                )

        if len(zf.infolist()) > MAX_FILES_IN_ZIP:
            raise HTTPException(status_code=400, detail=TOO_MANY_FILES_ERROR_MESSAGE)
        if sum(i.file_size for i in zf.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
            raise HTTPException(status_code=400, detail=UPLOAD_TOO_LARGE_ERROR_MESSAGE)

        for i in zf.infolist():
            if i.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=FILE_TOO_LARGE_ERROR_MESSAGE.format(filename=i.filename),
                )

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type=ZIP_MEDIA_TYPE,
        headers={
            CONTENT_DISPOSITION_HEADER_TITLE: CONTENT_DISPOSITION_HEADER.format(
                repository_name=repository_name
            )
        },
    )


@app.get(PUSH_ENDPOINT_TEMPLATE)
async def push(repository_name: str) -> dict:
    """
    Return the folder layout of a requested repository so that the client only needs to
    upload changed files and new files.
    """

    repository_path = repository_directory(repository_name)
    ensure_repository_exists(repository_path)

    objects_directory = (repository_path / SCCS_DIRECTORY / OBJECTS_DIRECTORY).resolve()

    if not objects_directory.exists() or not objects_directory.is_dir():
        raise HTTPException(status_code=404, detail=OBJECTS_NOT_FOUND_ERROR_MESSAGE)

    return {
        JSON_KEY_OBJECTS: list(
            set(
                i.stem
                for i in objects_directory.rglob(RGLOB_ALL_FILES_PATTERN)
                if i.is_file()
            )
        )
    }


@app.post(PUSH_ENDPOINT_TEMPLATE)
async def push_upload(repository_name: str, file: UploadFile = File(...)) -> dict:
    """
    Accept a zip archives of new objects to upload to the selected repository, and a zip
    archive of the updated metadata files. Extract the files from the archives, defend
    against zip slip attacks, and copy the files to the repository atomically.
    """

    repository_path = repository_directory(repository_name)
    ensure_repository_exists(repository_path)

    if not file.filename or Path(file.filename).stem != repository_name:
        raise HTTPException(
            status_code=400, detail=REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE
        )

    staging_root = Path(
        tempfile.mkdtemp(prefix=TEMPORARY_DIRECTORY_PREFIX, dir=repository_path.parent)
    )

    try:
        shutil.copytree(repository_path, staging_root, dirs_exist_ok=True)

        with zipfile.ZipFile(file.file, "r") as zf:
            if sum(i.file_size for i in zf.infolist()) > MAX_TOTAL_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400, detail=UPLOAD_TOO_LARGE_ERROR_MESSAGE
                )
            if len(zf.infolist()) > MAX_FILES_IN_ZIP:
                raise HTTPException(
                    status_code=400, detail=TOO_MANY_FILES_ERROR_MESSAGE
                )
            for i in zf.infolist():
                if i.file_size > MAX_INDIVIDUAL_FILE_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail=FILE_TOO_LARGE_ERROR_MESSAGE.format(filename=i.filename),
                    )

            for i in zf.infolist():
                safe_extract_zip(zf, i.filename, staging_root)

        with open(
            (staging_root / SCCS_DIRECTORY / METADATA_JSON).resolve(),
            "r+",
            encoding=UTF_8,
            newline=NEWLINE,
        ) as f:
            data = json.load(f)
            data[CURRENT_BRANCH_DICT_KEY][UPDATED_BRANCHES_DICT_KEY] = []
            f.seek(0)
            json.dump(data, f)
            f.truncate()

        old_root = repository_path.with_name(
            OLD_ROOT_TEMPLATE.format(repository_name=repository_path.name)
        )

        os.rename(repository_path, old_root)

        try:
            os.replace(staging_root, repository_path)
        except Exception:
            os.replace(old_root, repository_path)

        shutil.rmtree(old_root)

    except Exception:
        shutil.rmtree(staging_root)

        raise

    return {JSON_KEY_MESSAGE: PUSH_SUCCESS_MESSAGE}


@app.post(PULL_ENDPOINT_TEMPLATE)
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
        or not all(isinstance(i, str) for i in data[JSON_KEY_OBJECTS])
        or not data[JSON_KEY_OBJECTS]
    ):
        raise HTTPException(status_code=400, detail=INVALID_JSON_ERROR_MESSAGE)

    local_objects = set(data[JSON_KEY_OBJECTS])

    objects_paths = (repository_path / SCCS_DIRECTORY / OBJECTS_DIRECTORY).resolve()

    try:
        objects_paths.relative_to(repository_path)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=INVALID_REPOSITORY_NAME_ERROR_MESSAGE
        ) from e

    remote_objects = set(
        i.stem for i in (objects_paths).rglob(RGLOB_ALL_FILES_PATTERN) if i.is_file()
    )

    if local_objects - remote_objects:
        raise HTTPException(
            status_code=400,
            detail=LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE,
        )

    branches_path = (repository_path / SCCS_DIRECTORY / BRANCHES_DIRECTORY).resolve()

    try:
        branches_path.relative_to(repository_path)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=INVALID_REPOSITORY_NAME_ERROR_MESSAGE
        ) from e

    files_to_upload = [
        i
        for i in [
            i.resolve()
            for i in objects_paths.rglob(RGLOB_ALL_FILES_PATTERN)
            if i.is_file() and i.stem in remote_objects - local_objects
        ]
        + [(repository_path / SCCS_DIRECTORY / METADATA_JSON).resolve()]
        if i.is_file()
    ]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in files_to_upload:
            zf.write(filename=i, arcname=i.relative_to(repository_path))
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type=ZIP_MEDIA_TYPE,
        headers={
            CONTENT_DISPOSITION_HEADER_TITLE: CONTENT_DISPOSITION_HEADER_SPACED.format(
                repository_name=repository_name
            )
        },
    )


app.mount(
    REPOS_MOUNT_ENDPOINT,
    StaticFiles(directory=REPOSITORIES_BASE_DIRECTORY),
    name=STATIC_FILES_NAME,
)
"""Mount all repositories as static files on the /repos endpoint."""
