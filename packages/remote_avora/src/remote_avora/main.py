"""API Endpoints for hosted Avora Repositories"""

import asyncio
import io
import json
import os
import re
import shutil
import tempfile
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from filelock import FileLock
from remote_avora.constants_classes import RemoteAvoraConstants


@dataclass(frozen=True, slots=True)
class ValidatedRepositoryName:
    """A repository name validated against the allowed pattern."""

    value: str

    def __post_init__(self) -> None:
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
        return self.value


def validate_repository_name(repository_name: str) -> ValidatedRepositoryName:
    return ValidatedRepositoryName(repository_name)


def repository_base_directory(rc: RemoteAvoraConstants) -> Path:
    return Path(rc.REPOSITORIES_BASE_DIRECTORY).resolve()


def repository_directory(rc: RemoteAvoraConstants, repository_name: str) -> Path:
    safe = validate_repository_name(repository_name)
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


def ensure_repository_exists(rc: RemoteAvoraConstants, repository_path: Path) -> None:
    if not repository_path.exists() or not repository_path.is_dir():
        raise HTTPException(
            status_code=rc.HTTP_NOT_FOUND_STATUS_CODE,
            detail=rc.REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                repository_name=repository_path.name
            ),
        )


@contextmanager
def repository_lock(rc: RemoteAvoraConstants, repository_path: Path):
    lock_directory = (repository_base_directory(rc) / rc.LOCKS_DIRECTORY_NAME).resolve()
    lock_directory.mkdir(parents=True, exist_ok=True)
    lock = FileLock(lock_directory / f"{repository_path.name}{rc.LOCKFILE_NAME}")
    with lock:
        yield


def safe_extract_zip(rc, zip_archive, member_path, destination_directory):
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
rc = RemoteAvoraConstants()


@app.get(rc.ROOT_ENDPOINT)
async def root() -> dict:
    return {rc.MESSAGE_DICT_KEY: rc.EASTER_EGG_MESSAGE}


def _publish(rc, repository_name, file_bytes, filename, data):
    repository_path = repository_directory(rc, repository_name)
    with repository_lock(rc, repository_path):
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
            if not filename or Path(filename).stem != repository_name:
                raise HTTPException(
                    status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                    detail=rc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE,
                )
            import io as _io

            with zipfile.ZipFile(_io.BytesIO(file_bytes), "r") as zf:
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


@app.post(rc.PUBLISH_ENDPOINT_TEMPLATE)
async def publish(
    repository_name: str, file: UploadFile = File(...), data: str = Form(...)
) -> dict:
    repository_directory(rc, repository_name)
    contents = await file.read()
    return await asyncio.to_thread(
        _publish, rc, repository_name, contents, file.filename, data
    )


def _clone(rc, repository_name):
    repository_path = repository_directory(rc, repository_name)
    with repository_lock(rc, repository_path):
        ensure_repository_exists(rc, repository_path)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(repository_path):
                for i in files:
                    file_path = Path(root) / i
                    zf.write(
                        filename=file_path,
                        arcname=file_path.relative_to(repository_path),
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
        buffer.seek(rc.FILE_START_POSITION)
        return buffer.getvalue(), repository_name


@app.get(rc.CLONE_ENDPOINT_TEMPLATE)
async def clone(repository_name: str) -> StreamingResponse:
    data, name = await asyncio.to_thread(_clone, rc, repository_name)
    buffer = io.BytesIO(data)
    return StreamingResponse(
        buffer,
        media_type=rc.CONTENT_TYPE_ZIP,
        headers={
            rc.CONTENT_DISPOSITION_HEADER_TITLE: (
                rc.CONTENT_DISPOSITION_HEADER_TEMPLATE.format(repository_name=name)
            )
        },
    )


def _push_get(rc, repository_name):
    repository_path = repository_directory(rc, repository_name)
    with repository_lock(rc, repository_path):
        ensure_repository_exists(rc, repository_path)
        objects_directory = (
            repository_path / rc.AVORA_DIRECTORY / rc.OBJECTS_DIRECTORY
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


@app.get(rc.PUSH_ENDPOINT_TEMPLATE)
async def push(repository_name: str) -> dict:
    return await asyncio.to_thread(_push_get, rc, repository_name)


def _push_upload(rc, repository_name, file_bytes, filename):
    repository_path = repository_directory(rc, repository_name)
    if not filename or Path(filename).stem != repository_name:
        raise HTTPException(
            status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
            detail=rc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE,
        )
    with repository_lock(rc, repository_path):
        ensure_repository_exists(rc, repository_path)
        staging_root = Path(
            tempfile.mkdtemp(
                prefix=rc.TEMPORARY_DIRECTORY_PREFIX, dir=repository_path.parent
            )
        )
        try:
            shutil.copytree(repository_path, staging_root, dirs_exist_ok=True)
            import io as _io

            with zipfile.ZipFile(_io.BytesIO(file_bytes), "r") as zf:
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
                (staging_root / rc.AVORA_DIRECTORY / rc.METADATA_JSON).resolve(),
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
            shutil.rmtree(staging_root, ignore_errors=True)
            raise
    return {rc.MESSAGE_DICT_KEY: rc.PUSH_SUCCESS_MESSAGE}


@app.post(rc.PUSH_ENDPOINT_TEMPLATE)
async def push_upload(repository_name: str, file: UploadFile = File(...)) -> dict:
    contents = await file.read()
    return await asyncio.to_thread(
        _push_upload, rc, repository_name, contents, file.filename
    )


def _pull(rc, repository_name, data):
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
    repository_path = repository_directory(rc, repository_name)
    with repository_lock(rc, repository_path):
        ensure_repository_exists(rc, repository_path)
        local_objects = set(data[rc.OBJECTS_DICT_KEY])
        objects_paths = (
            repository_path / rc.AVORA_DIRECTORY / rc.OBJECTS_DIRECTORY
        ).resolve()
        try:
            objects_paths.relative_to(repository_path)
        except ValueError as e:
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE,
            ) from e
        remote_objects = {
            i.stem
            for i in objects_paths.rglob(rc.RGLOB_ALL_FILES_PATTERN)
            if i.is_file()
        }
        if local_objects - remote_objects:
            raise HTTPException(
                status_code=rc.HTTP_BAD_REQUEST_STATUS_CODE,
                detail=rc.LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE,
            )
        branches_path = (
            repository_path / rc.AVORA_DIRECTORY / rc.BRANCHES_DIRECTORY
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
            + [(repository_path / rc.AVORA_DIRECTORY / rc.METADATA_JSON).resolve()]
            if i.is_file()
        ]
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i in files_to_upload:
                zf.write(filename=i, arcname=i.relative_to(repository_path))
        buffer.seek(rc.FILE_START_POSITION)
        return buffer.getvalue(), repository_name


@app.post(rc.PULL_ENDPOINT_TEMPLATE)
async def pull(repository_name: str, data: dict) -> StreamingResponse:
    payload, name = await asyncio.to_thread(_pull, rc, repository_name, data)
    buffer = io.BytesIO(payload)
    return StreamingResponse(
        buffer,
        media_type=rc.CONTENT_TYPE_ZIP,
        headers={
            rc.CONTENT_DISPOSITION_HEADER_TITLE: (
                rc.CONTENT_DISPOSITION_HEADER_SPACED_TEMPLATE.format(
                    repository_name=name
                )
            )
        },
    )
