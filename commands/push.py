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
from repository_layout import RepositoryLayout


def get_matching_file_paths(constants: SCCSConstants, repo: RepositoryLayout, filename: str) -> list:
    """
    Iterate through 'updated_branches' to retrieve each branch's version of 'filename'.
    """

    paths = []
    for i in repo.current_branch_data(constants.UPDATED_BRANCHES_DICT_KEY):
        branch_dir = repo.branches_path() / i
        if branch_dir.is_dir():
            f = branch_dir / filename / (filename + constants.JSON_EXTENSION)
            if f.is_file():
                paths.append(f.resolve())
    return paths


def push_GET(constants: SCCSConstants, repo: RepositoryLayout) -> requests.Response:
    """Make a GET request to 'remote'/push, returning the response."""

    url = constants.PUSH_ENDPOINT_TEMPLATE.format(base_url=repo.base_repo_url())
    try:
        response = requests.get(url, timeout=constants.HTTP_TIMEOUT_SECONDS)
    except Exception as e:
        raise exceptions.HTTPGetRequestError() from e

    return response


def compare_hash_lists(repo: RepositoryLayout, remote_objects: list) -> list:
    """
    Subtract 'remote_objects' from 'local_objects' by converting to sets to get a list
    of objects that remote is missing.

    To check if local is missing objects from remote, subract 'local_objects' from
    'remote_objects' and ensure and ensure the subsequently created list is empty,
    otherwise raise.

    Return a list of objects that remote is missing.
    """

    local_objects = repo.repo_objects()

    obj_to_upload = list(set(local_objects) - set(remote_objects))
    if list(set(remote_objects) - set(local_objects)):
        raise exceptions.MissingCommitObjectsError()

    return obj_to_upload


def zip_files_to_upload(constants: SCCSConstants, repo: RepositoryLayout, remote_objects: list) -> io.BytesIO:
    """
    Create a temporary version of the repository with only the files in 'obj_to_upload'
    and metadata files, ensuring that the folder layout is left intact. Compress said
    folder and return it as a Bytes.io memory buffer and xdelete the temporary directory.

    Return a zip archive of files in 'obj_to_upload' and metadata files using the same
    layout as a repository.
    """

    document_path = repo.document_path()

    current_branch_path = repo.current_branch_path()
    commit_messages_path = repo.commit_messages_path()
    obj_to_upload_set = set(compare_hash_lists(repo, remote_objects))
    objects_paths = [
        i.resolve()
        for i in (repo.objects_path()).rglob(constants.RGLOB_ALL_FILES_PATTERN)
        if i.is_file() and i.stem in obj_to_upload_set
    ]

    history_paths = get_matching_file_paths(constants, repo, constants.HISTORY_DIR)
    byte_hash_paths = get_matching_file_paths(constants, repo, constants.COMMIT_FILE_HASH_DIR)

    files_to_upload = (
        objects_paths
        + history_paths
        + byte_hash_paths
        + document_path
        + current_branch_path
        + commit_messages_path
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_folder_path = Path(temp_dir) / constants.TMP_DIR_TEMPLATE.format(repo_name=repo.repo_name)
        for i in files_to_upload:
            (tmp_folder_path / i.relative_to(repo.root).parent).mkdir(
                parents=True, exist_ok=True
            )
            shutil.copy2(i, tmp_folder_path / i.relative_to(repo.root))

        buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(temp_dir):
                    for i in files:
                        full_path = Path(root) / i
                        zf.write(
                            full_path, arcname=full_path.relative_to(temp_dir)
                        )
        except Exception as e:
            raise exceptions.ZippingFileError(
                constants.ZIPPING_FILE_ERROR_MESSAGE
            ) from e

        try:
            buffer.seek(0)
        except Exception as e:
            raise exceptions.BufferError(constants.BUFFER_SEEK_ERROR_MESSAGE) from e

    return buffer


def push_POST(constants: SCCSConstants, repo: RepositoryLayout, buffer: io.BytesIO) -> requests.Response:
    """
    Make a POST request to 'remote', sending 'buffer' as a file.

    Return the server response of the POST request to 'remote'.
    """

    remote = repo.base_repo_url()

    remote_path = urlsplit(remote).path.rstrip(constants.PATH_SEPARATOR)
    if not remote_path.endswith(constants.REQUIRED_PATH_ENDING_TEMPLATE.format(repo_name=repo.repo_name)):
        raise exceptions.InvalidAPIURLError(
            constants.INVALID_PATH_ENDING_ERROR_MESSAGE
        )

    try:
        response = requests.post(
            constants.PUSH_ENDPOINT_TEMPLATE.format(base_url=remote),
            files=[
                (
                    constants.POST_FILE_FIELD_NAME,
                    (
                        repo.repo_name + constants.ZIP_EXTENSION,
                        buffer,
                        constants.CONTENT_TYPE_ZIP,
                    ),
                )
            ],
            timeout=constants.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            constants.PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE.format(url=remote)
        ) from e

    return response


def clear_updated_branches(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Clear the updated branches list in the current branch file."""


    data = repo.current_branch_data()
    if data is None:
        data = {}
    data[constants.UPDATED_BRANCHES_DICT_KEY] = []

    try:
        with open(repo.current_branch_path(), "w", encoding=constants.UTF_8, newline=constants.NEWLINE) as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise exceptions.FileWriteError(
            constants.CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE
    ) from e


def print_push_success_message(constants: SCCSConstants, response: requests.Response, url: str) -> None:
    """Print a success message after pushing the repository."""

    print(constants.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(constants.PUSH_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs push> command."""
    repo.check_repository_layout()

    remote = repo.base_repo_url()

    GET_response = push_GET(constants, repo)

    GET_response.raise_for_status()

    remote_objects = GET_response.json()[constants.HTTP_OBJECTS_DICT_KEY]
    
    buffer = zip_files_to_upload(constants, repo, remote_objects)

    POST_response = push_POST(constants, repo, buffer)

    POST_response.raise_for_status()

    clear_updated_branches(constants, repo)
    print_push_success_message(constants, POST_response, remote)

if __name__ == "__main__":
    utils.run_command(main)
      