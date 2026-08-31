#!/usr/bin/env python3

import io
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import exceptions
import requests
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    TargetBranch,
)


def fetch_remote_objects(c: SCCSConstants, rd: RepositoryData) -> requests.Response:

    url = c.PUSH_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url())
    try:
        response = requests.get(url, timeout=c.HTTP_TIMEOUT_SECONDS)
    except Exception as e:
        raise exceptions.SCCSException(c.PUSH_HTTP_REQUEST_ERROR_MESSAGE) from e

    return response


def get_matching_file_paths(

    c: SCCSConstants, filename: str, ri: RepositoryIO, rp: RepositoryPaths
) -> list[Path]:

    paths = []
    updated_branches = ri.read_current_branch_data_key(c.UPDATED_BRANCHES_DICT_KEY)
    if updated_branches is None:
        raise exceptions.SCCSException(c.NO_UPDATED_BRANCHES_ERROR_MESSAGE)
    for i in updated_branches:
        branch_directory = rp.branches_path() / i
        if branch_directory.is_dir():
            f = (branch_directory / filename / filename).with_suffix(c.JSON_EXTENSION)
            if f.is_file():
                paths.append(f.resolve())
    return paths


def compare_commit_identifier_lists(

    remote_objects: list[str], rd: RepositoryData
) -> list[str]:

    local_objects = rd.repository_objects()

    object_to_upload = list(set(local_objects) - set(remote_objects))
    if list(set(remote_objects) - set(local_objects)):
        raise exceptions.SCCSException(c.MISSING_REMOTE_OBJECTS_ERROR_MESSAGE)

    return object_to_upload


def zip_files_to_upload(

    c: SCCSConstants,
    remote_objects: list[str],
    rd: RepositoryData,
    ri: RepositoryIO,
    rp: RepositoryPaths,
) -> io.BytesIO:

    document_path = [rp.document_path()]

    current_branch_path = [rp.current_branch_data_file_path()]
    commit_messages_path = [rp.commit_messages_path()]
    object_to_upload_set = set(compare_commit_identifier_lists(remote_objects, rd))
    objects_paths = [
        i.resolve()
        for i in (rp.objects_path()).rglob(c.RGLOB_ALL_FILES_PATTERN)
        if i.is_file() and i.stem in object_to_upload_set
    ]

    history_paths = get_matching_file_paths(c, c.HISTORY_DIRECTORY, ri, rp)
    byte_hash_paths = get_matching_file_paths(c, c.COMMIT_BYTE_HASH_DIRECTORY, ri, rp)

    files_to_upload = (
        objects_paths
        + history_paths
        + byte_hash_paths
        + document_path
        + current_branch_path
        + commit_messages_path
    )

    with tempfile.TemporaryDirectory() as tf:
        temporary_folder_path = Path(tf) / c.TEMPORARY_DIRECTORY_TEMPLATE.format(
            repository_name=rp.repository_name
        )
        for i in files_to_upload:
            (temporary_folder_path / i.relative_to(rp.root).parent).mkdir(
                parents=True, exist_ok=True
            )
            shutil.copy2(i, temporary_folder_path / i.relative_to(rp.root))

        buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(tf):
                    for i in files:
                        full_path = Path(root) / i
                        zf.write(full_path, arcname=full_path.relative_to(tf))
        except Exception as e:
            raise exceptions.SCCSException(c.ZIPPING_FILE_ERROR_MESSAGE) from e

        try:
            buffer.seek(0)
        except Exception as e:
            raise exceptions.SCCSException(c.ZIP_BUFFER_SEEK_ERROR_MESSAGE) from e

    return buffer


def upload_objects(

    c: SCCSConstants, buffer: io.BytesIO, rd: RepositoryData, rp: RepositoryPaths
) -> requests.Response:

    remote = rd.base_repository_url()

    remote_path = urlsplit(remote).path.rstrip(c.PATH_SEPARATOR)
    if not remote_path.endswith(
        c.REQUIRED_PATH_ENDING_TEMPLATE.format(repo_name=rp.repository_name)
    ):
        raise exceptions.SCCSException(c.INVALID_PATH_ENDING_ERROR_MESSAGE_TEMPLATE)

    try:
        response = requests.post(
            c.PUSH_ENDPOINT_TEMPLATE.format(base_url=remote),
            files=[
                (
                    c.POST_FILE_FIELD_NAME,
                    (
                        str(Path(rp.repository_name).with_suffix(c.ZIP_EXTENSION)),
                        buffer,
                        c.CONTENT_TYPE_ZIP,
                    ),
                )
            ],
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.SCCSException(
            c.PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE.format(url=remote)
        ) from e

    return response


def clear_updated_branches(

    c: SCCSConstants, ri: RepositoryIO, rp: RepositoryPaths
) -> None:

    data = ri.read_current_branch_data()
    data[c.UPDATED_BRANCHES_DICT_KEY] = []

    try:
        with open(
            rp.current_branch_data_file_path(),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise exceptions.SCCSException(c.CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE) from e


def print_push_success_message(

    c: SCCSConstants, response: requests.Response, url: str
) -> None:

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PUSH_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(

    c: SCCSConstants,
    rd: RepositoryData,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:
    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    remote = rd.base_repository_url()

    remote_objects_response = fetch_remote_objects(c, rd)

    remote_objects_response.raise_for_status()

    remote_objects = remote_objects_response.json()[c.HTTP_OBJECTS_DICT_KEY]

    buffer = zip_files_to_upload(c, remote_objects, rd, ri, rp)

    upload_response = upload_objects(c, buffer, rd, rp)

    upload_response.raise_for_status()

    clear_updated_branches(c, ri, rp)
    print_push_success_message(c, upload_response, remote)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryIO(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
    )
