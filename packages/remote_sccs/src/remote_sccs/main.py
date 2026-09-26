#!/usr/bin/env python3
"""API Endpoints for hosted SCCS Repositories"""

import io
import json
import os
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from remote_sccs.constants_classes import RemoteSCCSConstants


@dataclass(frozen=True, slots=True)
class ValidatedRepositoryName:
    """A repository name validated against the allowed pattern."""

    value: str

    def __post_init__(self) -> None:
        """
        Validate the repository name and reject empty names, names containing
        characters outside the allowed pattern, and relative path shorthands.
        """

        if (
            not self.value
            or not re.fullmatch(r"^[A-Za-z0-9._-]+$", self.value)
            or self.value in (rc.SINGLE_PERIOD, rc.DOUBLE_PERIOD)
        ):
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE,
            )

    def __str__(self) -> str:
        """Return the validated repository name as its string representation."""

        return self.value


def validate_repository_name(repository_name: str) -> ValidatedRepositoryName:
    """Validate a user-provided repository name against the allowed pattern."""

    return ValidatedRepositoryName(repository_name)


def repository_base_directory(rc: RemoteSCCSConstants) -> Path:
    """Return the fully-resolved base directory that holds all repositories."""

    return Path(rc.REPOSITORIES_BASE_DIRECTORY).resolve()


def repository_directory(rc: RemoteSCCSConstants, repository_name: str) -> Path:
    """
    Build the fully-resolved directory for a validated repository name and
    guarantee it stays inside the repositories base directory.
    """

    safe = validate_repository_name(repository_name)  # returns ValidatedRepositoryName
    base_directory = repository_base_directory(rc)
    repository_path = (base_directory / str(safe)).resolve()

    try:
        repository_path.relative_to(base_directory)
    except ValueError as e:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE,
        ) from e

    return repository_path


def ensure_repository_exists(rc: RemoteSCCSConstants, repository_path: Path) -> None:
    """Ensure that the specified repository exists and is a directory."""

    if not repository_path.exists() or not repository_path.is_dir():
        raise HTTPException(
            status_code=rc.HTTP_NOT_FOUND_STATUS_CODE,
            detail=rc.REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                repository_name=repository_path.name
            ),
        )


def safe_extract_zip(
    rc: RemoteSCCSConstants,
    zip_archive: zipfile.ZipFile,
    member_path: str,
    destination_directory: Path,
) -> None:
    """
    Safely extract a single member from a zip archive into the destination
    directory.

    Guards against zip slip attacks by rejecting absolute paths and any path
    containing parent-directory components, and by verifying the resolved
    target path stays inside the destination directory. Creates intermediate
    directories as needed for directory and file members.
    """

    destination_resolved = destination_directory.resolve()
    entry_path = Path(member_path)
    if entry_path.is_absolute() or rc.DOUBLE_PERIOD in entry_path.parts:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.INVALID_ZIP_PATH_ERROR_MESSAGE,
        )
    target_path = Path(os.path.normpath(destination_directory / entry_path)).resolve()
    try:
        target_path.relative_to(destination_resolved)
    except ValueError as e:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.INVALID_ZIP_PATH_ERROR_MESSAGE,
        ) from e
    if zip_archive.getinfo(member_path).is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
    else:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with zip_archive.open(member_path) as source, open(target_path, "wb") as f:
            shutil.copyfileobj(source, f)


app = FastAPI()
rc = RemoteSCCSConstants()


@app.get(rc.ROOT_ENDPOINT)
async def root() -> dict:
    """Easter Egg Endpoint - Do Not Remove"""

    return {rc.MESSAGE_DICT_KEY: rc.EASTER_EGG_MESSAGE}


@app.post(rc.PUBLISH_ENDPOINT_TEMPLATE)
async def publish(
    repository_name: str, file: UploadFile = File(...), data: str = Form(...)
) -> dict:
    """Publish a repository to the hosted API"""

    repository_path = repository_directory(rc, repository_name)

    if repository_path.exists():
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.REPOSITORY_EXISTS_ERROR_MESSAGE,
        )

    staging_root = Path(
        tempfile.mkdtemp(
            prefix=rc.TEMPORARY_DIRECTORY_PREFIX, dir=repository_path.parent
        )
    )

    try:
        try:
            remote = json.loads(data)[rc.REMOTE_KEY]
        except (json.JSONDecodeError, KeyError) as e:
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.INVALID_JSON_ERROR_MESSAGE,
            ) from e

        if not remote:
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.REMOTE_URL_REQUIRED_ERROR_MESSAGE,
            )

        if not file.filename or Path(file.filename).stem != repository_name:
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE,
            )

        with zipfile.ZipFile(file.file, "r") as zf:
            if len(zf.infolist()) > rc.MAX_FILES_IN_ZIP:
                raise HTTPException(
                    status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                    detail=rc.TOO_MANY_FILES_ERROR_MESSAGE,
                )
            if sum(i.file_size for i in zf.infolist()) > rc.MAX_TOTAL_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                    detail=rc.UPLOAD_TOO_LARGE_ERROR_MESSAGE,
                )

            for i in zf.infolist():
                if i.file_size > rc.MAX_INDIVIDUAL_FILE_SIZE:
                    raise HTTPException(
                        status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                        detail=rc.FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE.format(
                            filename=i.filename
                        ),
                    )

                safe_extract_zip(rc, zf, i.filename, staging_root)

        os.replace(staging_root, repository_path)

    except Exception:
        shutil.rmtree(staging_root, ignore_errors=True)

        raise

    return {
        rc.MESSAGE_DICT_KEY: rc.FILE_PUBLISHED_MESSAGE,
        rc.REPOSITORY_URL_DICT_KEY: remote,
    }


@app.get(rc.CLONE_ENDPOINT_TEMPLATE)
async def clone(repository_name: str) -> StreamingResponse:
    """Return a zipped version of a requested repository"""

    repository_path = repository_directory(rc, repository_name)
    ensure_repository_exists(rc, repository_path)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(repository_path):
            for i in files:
                file_path = Path(root) / i
                zf.write(
                    filename=file_path, arcname=file_path.relative_to(repository_path)
                )

        if len(zf.infolist()) > rc.MAX_FILES_IN_ZIP:
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.TOO_MANY_FILES_ERROR_MESSAGE,
            )
        if sum(i.file_size for i in zf.infolist()) > rc.MAX_TOTAL_UPLOAD_SIZE:
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.UPLOAD_TOO_LARGE_ERROR_MESSAGE,
            )

        for i in zf.infolist():
            if i.file_size > rc.MAX_INDIVIDUAL_FILE_SIZE:
                raise HTTPException(
                    status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                    detail=rc.FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE.format(
                        filename=i.filename
                    ),
                )

    zip_buffer.seek(rc.FILE_START_POSITION)
    return StreamingResponse(
        zip_buffer,
        media_type=rc.CONTENT_TYPE_ZIP,
        headers={
            rc.CONTENT_DISPOSITION_HEADER_TITLE: (
                rc.CONTENT_DISPOSITION_HEADER_TEMPLATE.format(
                    repository_name=repository_name
                )
            )
        },
    )


@app.get(rc.PUSH_ENDPOINT_TEMPLATE)
async def push(repository_name: str) -> dict:
    """
    Return the folder layout of a requested repository so that the client only needs to
    upload changed files and new files.
    """

    repository_path = repository_directory(rc, repository_name)
    ensure_repository_exists(rc, repository_path)

    objects_directory = (
        repository_path / rc.SCCS_DIRECTORY / rc.OBJECTS_DIRECTORY
    ).resolve()

    if not objects_directory.exists() or not objects_directory.is_dir():
        raise HTTPException(
            status_code=rc.HTTP_NOT_FOUND_STATUS_CODE,
            detail=rc.OBJECTS_NOT_FOUND_ERROR_MESSAGE,
        )

    return {
        rc.OBJECTS_DICT_KEY: {
            i.stem
            for i in objects_directory.rglob(rc.RGLOB_ALL_FILES_PATTERN)
            if i.is_file()
        }
    }


@app.post(rc.PUSH_ENDPOINT_TEMPLATE)
async def push_upload(repository_name: str, file: UploadFile = File(...)) -> dict:
    """
    Accept a zip archive of new objects to upload to the selected repository.

    The uploaded zip must be named after the repository. Its contents are
    extracted into a staging copy of the repository (defending against zip
    slip attacks), the metadata file's updated-branches list is reset, and the
    staging copy replaces the repository atomically. On failure, the original
    repository is left untouched.
    """

    repository_path = repository_directory(rc, repository_name)
    ensure_repository_exists(rc, repository_path)

    if not file.filename or Path(file.filename).stem != repository_name:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE,
        )

    staging_root = Path(
        tempfile.mkdtemp(
            prefix=rc.TEMPORARY_DIRECTORY_PREFIX, dir=repository_path.parent
        )
    )

    try:
        shutil.copytree(repository_path, staging_root, dirs_exist_ok=True)

        with zipfile.ZipFile(file.file, "r") as zf:
            if sum(i.file_size for i in zf.infolist()) > rc.MAX_TOTAL_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                    detail=rc.UPLOAD_TOO_LARGE_ERROR_MESSAGE,
                )
            if len(zf.infolist()) > rc.MAX_FILES_IN_ZIP:
                raise HTTPException(
                    status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                    detail=rc.TOO_MANY_FILES_ERROR_MESSAGE,
                )
            for i in zf.infolist():
                if i.file_size > rc.MAX_INDIVIDUAL_FILE_SIZE:
                    raise HTTPException(
                        status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                        detail=rc.FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE.format(
                            filename=i.filename
                        ),
                    )

            for i in zf.infolist():
                safe_extract_zip(rc, zf, i.filename, staging_root)

        with open(
            (staging_root / rc.SCCS_DIRECTORY / rc.METADATA_JSON).resolve(),
            "r+",
            encoding=rc.UTF_8,
            newline=rc.NEWLINE,
        ) as f:
            data = json.load(f)
            data[rc.CURRENT_BRANCH_DICT_KEY][rc.UPDATED_BRANCHES_DICT_KEY] = []
            f.seek(rc.FILE_START_POSITION)
            json.dump(data, f)
            f.truncate()

        old_root = repository_path.with_name(
            rc.OLD_ROOT_TEMPLATE.format(repository_name=repository_path.name)
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

    return {rc.MESSAGE_DICT_KEY: rc.PUSH_SUCCESS_MESSAGE}


@app.post(rc.PULL_ENDPOINT_TEMPLATE)
async def pull(repository_name: str, data: dict) -> StreamingResponse:
    """
    Send a zip archive of commit objects and metadata files that the local repository
    (caller) is missing by accepting a list of commit objects that the local doesn't
    have.
    """

    repository_path = repository_directory(rc, repository_name)
    ensure_repository_exists(rc, repository_path)

    if (
        not isinstance(data, dict)
        or rc.OBJECTS_DICT_KEY not in data
        or not isinstance(data[rc.OBJECTS_DICT_KEY], list)
        or not all(isinstance(i, str) for i in data[rc.OBJECTS_DICT_KEY])
        or not data[rc.OBJECTS_DICT_KEY]
    ):
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.INVALID_JSON_ERROR_MESSAGE,
        )

    local_objects = set(data[rc.OBJECTS_DICT_KEY])

    objects_paths = (
        repository_path / rc.SCCS_DIRECTORY / rc.OBJECTS_DIRECTORY
    ).resolve()

    try:
        objects_paths.relative_to(repository_path)
    except ValueError as e:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE,
        ) from e

    remote_objects = {
        i.stem for i in (objects_paths).rglob(rc.RGLOB_ALL_FILES_PATTERN) if i.is_file()
    }

    if local_objects - remote_objects:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE,
        )

    branches_path = (
        repository_path / rc.SCCS_DIRECTORY / rc.BRANCHES_DIRECTORY
    ).resolve()

    try:
        branches_path.relative_to(repository_path)
    except ValueError as e:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE,
        ) from e

    files_to_upload = [
        i
        for i in [
            i.resolve()
            for i in objects_paths.rglob(rc.RGLOB_ALL_FILES_PATTERN)
            if i.is_file() and i.stem in remote_objects - local_objects
        ]
        + [(repository_path / rc.SCCS_DIRECTORY / rc.METADATA_JSON).resolve()]
        if i.is_file()
    ]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in files_to_upload:
            zf.write(filename=i, arcname=i.relative_to(repository_path))
    zip_buffer.seek(rc.FILE_START_POSITION)
    return StreamingResponse(
        zip_buffer,
        media_type=rc.CONTENT_TYPE_ZIP,
        headers={
            rc.CONTENT_DISPOSITION_HEADER_TITLE: (
                rc.CONTENT_DISPOSITION_HEADER_SPACED_TEMPLATE.format(
                    repository_name=repository_name
                )
            )
        },
    )


app.mount(
    RemoteSCCSConstants.REPOS_MOUNT_ENDPOINT,
    StaticFiles(directory=RemoteSCCSConstants.REPOSITORIES_BASE_DIRECTORY),
    name=RemoteSCCSConstants.STATIC_FILES_NAME,
)
