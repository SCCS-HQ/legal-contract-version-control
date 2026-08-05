#!/usr/bin/env python3
"""Push the repository to the remote server."""

import io
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

from constants_classes import SCCSConstants
import exceptions
import requests

import utils
from repository_layout import (
    RepositoryPaths,
    RepositoryIO,
    RepositoryData,
    RepositoryStatus,
    TargetBranch,
)


def get_matching_file_paths(
    c: SCCSConstants, filename: str, ri: RepositoryIO, rp: RepositoryPaths
) -> list[Path]:
    """
    Iterate through 'updated_branches' to retrieve each branch's version of 'filename'.
    """

    paths = []
    updated_branches = ri.read_current_branch_data_key(c.UPDATED_BRANCHES_DICT_KEY)
    if updated_branches is None: raise exceptions.InvalidMetadataError()
    for i in updated_branches:
        branch_dir = rp.branches_path() / i
        if branch_dir.is_dir():
            f = (branch_dir / filename / filename).with_suffix(c.JSON_EXTENSION)
            if f.is_file():
                paths.append(f.resolve())
    return paths


def push_GET(c: SCCSConstants, rd: RepositoryData) -> requests.Response:
    """Make a GET request to 'remote'/push, returning the response."""

    url = c.PUSH_ENDPOINT_TEMPLATE.format(base_url=rd.base_repo_url())
    try:
        response = requests.get(url, timeout=c.HTTP_TIMEOUT_SECONDS)
    except Exception as e:
        raise exceptions.HTTPGetRequestError() from e

    return response


def compare_hash_lists(remote_objects: list[str], rd: RepositoryData) -> list[str]:
    """
    Subtract 'remote_objects' from 'local_objects' by converting to sets to get a list
    of objects that remote is missing.

    To check if local is missing objects from remote, subract 'local_objects' from
    'remote_objects' and ensure and ensure the subsequently created list is empty,
    otherwise raise.

    Return a list of objects that remote is missing.
    """

    local_objects = rd.repo_objects()

    obj_to_upload = list(set(local_objects) - set(remote_objects))
    if list(set(remote_objects) - set(local_objects)):
        raise exceptions.MissingCommitObjectsError()

    return obj_to_upload


def zip_files_to_upload(
    c: SCCSConstants,
    remote_objects: list[str],
    rp: RepositoryPaths,
    ri: RepositoryIO,
    rd: RepositoryData,
) -> io.BytesIO:
    """
    Create a temporary version of the repository with only the files in 'obj_to_upload'
    and metadata files, ensuring that the folder layout is left intact.
    Compress said folder and return it as a Bytes.io memory buffer and
    xdelete the temporary directory.

    Return a zip archive of files in 'obj_to_upload' and metadata files using the same
    layout as a repository.
    """

    document_path = [rp.document_path()]

    current_branch_path = [rp.current_branch_data_file_path()]
    commit_messages_path = [rp.commit_messages_path()]
    obj_to_upload_set = set(compare_hash_lists(remote_objects, rd))
    objects_paths = [
        i.resolve()
        for i in (rp.objects_path()).rglob(c.RGLOB_ALL_FILES_PATTERN)
        if i.is_file() and i.stem in obj_to_upload_set
    ]

    history_paths = get_matching_file_paths(c, c.HISTORY_DIR, ri, rp)
    byte_hash_paths = get_matching_file_paths(c, c.COMMIT_FILE_HASH_DIR, ri, rp)

    files_to_upload = (
        objects_paths
        + history_paths
        + byte_hash_paths
        + document_path
        + current_branch_path
        + commit_messages_path
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_folder_path = Path(temp_dir) / c.TMP_DIR_TEMPLATE.format(
            repo_name=rp.repo_name
        )
        for i in files_to_upload:
            (tmp_folder_path / i.relative_to(rp.root).parent).mkdir(
                parents=True, exist_ok=True
            )
            shutil.copy2(i, tmp_folder_path / i.relative_to(rp.root))

        buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(temp_dir):
                    for i in files:
                        full_path = Path(root) / i
                        zf.write(
                            full_path, arcname=full_path.relative_to(temp_dir)
                        )
        except Exception as e:
            raise exceptions.ZippingFileError(
                c.ZIPPING_FILE_ERROR_MESSAGE
            ) from e

        try:
            buffer.seek(0)
        except Exception as e:
            raise exceptions.BufferError(c.BUFFER_SEEK_ERROR_MESSAGE) from e

    return buffer


def push_POST(
    c: SCCSConstants, buffer: io.BytesIO, rd: RepositoryData, rp: RepositoryPaths
) -> requests.Response:
    """
    Make a POST request to 'remote', sending 'buffer' as a file.

    Return the server response of the POST request to 'remote'.
    """

    remote = rd.base_repo_url()

    remote_path = urlsplit(remote).path.rstrip(c.PATH_SEPARATOR)
    if not remote_path.endswith(
        c.REQUIRED_PATH_ENDING_TEMPLATE.format(repo_name=rp.repo_name)
    ):
        raise exceptions.InvalidAPIURLError(
            c.INVALID_PATH_ENDING_ERROR_MESSAGE
        )

    try:
        response = requests.post(
            c.PUSH_ENDPOINT_TEMPLATE.format(base_url=remote),
            files=[
                (
                    c.POST_FILE_FIELD_NAME,
                    (
                        str(Path(rp.repo_name).with_suffix(c.ZIP_EXTENSION)),
                        buffer,
                        c.CONTENT_TYPE_ZIP,
                    ),
                )
            ],
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            c.PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE.format(url=remote)
        ) from e

    return response


def clear_updated_branches(
    c: SCCSConstants, ri: RepositoryIO, rp: RepositoryPaths
) -> None:
    """Clear the updated branches list in the current branch file."""


    data = ri.read_current_branch_data()
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError()
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
        raise exceptions.FileWriteError(
            c.CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE
    ) from e


def print_push_success_message(
    c: SCCSConstants, response: requests.Response, url: str
) -> None:
    """Print a success message after pushing the repository."""

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PUSH_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rp: RepositoryPaths,
    ri: RepositoryIO,
) -> None:
    """Run functions for the <sccs push> command."""
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    remote = rd.base_repo_url()

    GET_response = push_GET(c, rd)

    GET_response.raise_for_status()

    remote_objects = GET_response.json()[c.HTTP_OBJECTS_DICT_KEY]

    buffer = zip_files_to_upload(c, remote_objects, rp, ri, rd)

    POST_response = push_POST(c, buffer, rd, rp)

    POST_response.raise_for_status()

    clear_updated_branches(c, ri, rp)
    print_push_success_message(c, POST_response, remote)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryIO(Path.cwd(), c, target),
    )