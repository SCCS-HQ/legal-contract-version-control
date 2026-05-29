import io
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import exceptions
import requests
import utils


def get_matching_file_paths(
    filename: str,
    updated_branches: list = None,
    cwd: None | Path = None,
) -> list:
    """
    Iterate through 'updated_branches' to retrieve each branch's version of 'filename'.
    """

    if cwd is None:
        cwd = utils.working_directory_path
    paths = []
    for b in updated_branches:
        paths.extend(
            [
                f.resolve()
                for f in (cwd / ".sccs" / "branches" / b).rglob("*")
                if f.is_file() and f.stem == filename
            ]
        )
    return paths


def push_GET(remote: str) -> requests.Response:
    """Make a GET request to 'remote'/push, returning the response."""

    try:
        response = requests.get(f"{remote}/push")
    except Exception as e:
        raise exceptions.HTTPGetRequestError() from e

    return response


def get_repo_objects(cwd: None | Path = None) -> list:
    """
    Return of list of every commit hash by iterating through the objects folder's file
    stems, and removing duplicates with a set.
    """

    if cwd is None:
        cwd = utils.working_directory_path
    objects_dir = cwd / ".sccs" / "objects"
    objects = list(set(f.stem for f in objects_dir.rglob("*") if f.is_file()))
    return objects


def compare_hash_lists(remote_objects: list, local_objects: list) -> list:
    """
    Subtract 'remote_objects' from 'local_objects' by converting to sets to get a list
    of objects that remote is missing.

    To check if local is missing objects from remote, subract 'local_objects' from
    'remote_objects' and ensure and ensure the subsequently created list is empty,
    otherwise raise.

    Return a list of objects that remote is missing.
    """

    obj_to_upload = list(set(local_objects) - set(remote_objects))
    if list(set(remote_objects) - set(local_objects)):
        print(
            "Warning: There are objects on the remote that are not present locally. You"
            " must pull before pushing. - Not implemented yet"
        )

    return obj_to_upload


def zip_files_to_upload(obj_to_upload: list, cwd: None | Path = None) -> io.BytesIO:
    """
    Create a temporary version of the repository with only the files in 'obj_to_upload'
    and metadata files, ensuring that the folder layout is left intact. Compress said
    folder and return it as a Bytes.io memory buffer and delete the temporary directory.

    Return a zip archive of files in 'obj_to_upload' and metadata files using the same
    layout as a repository.
    """

    if cwd is None:
        cwd = utils.working_directory_path

    repo_name = Path(cwd).name

    if cwd is None:
        cwd = utils.working_directory_path
    updated_branches = utils.get_branch_data(key="updated_branches") or []
    current_branch_path = cwd / ".sccs" / "current_branch" / "current_branch.json"
    commit_msgs_path = cwd / ".sccs" / "commit_messages" / "commit_messages.json"
    objects_paths = [
        f.resolve()
        for f in (cwd / ".sccs" / "objects").rglob("*")
        if f.is_file() and f.stem in obj_to_upload
    ]

    history_paths = []
    byte_hash_paths = []

    for b in updated_branches:
        history_paths.extend(get_matching_file_paths([b], "commit_history", cwd))
        byte_hash_paths.extend(get_matching_file_paths([b], "commit_file_hash", cwd))

    files_to_upload = (
        objects_paths
        + history_paths
        + byte_hash_paths
        + [current_branch_path, commit_msgs_path]
    )

    tmp_folder_path = Path(f"tmp_{repo_name}")
    tmp_folder_path.mkdir(parents=True, exist_ok=True)

    for f in files_to_upload:
        (tmp_folder_path / f.relative_to(cwd).parent).mkdir(parents=True, exist_ok=True)

        shutil.copy2(f, tmp_folder_path / (f.relative_to(cwd)).parent)

    buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as f:
            for (
                root,
                dirs,
                files,
            ) in os.walk(f"./tmp_{repo_name}"):
                for file in files:
                    f.write(Path(root) / file)
    except Exception as e:
        raise exceptions.ZippingFileError(
            "Failed to zip current working directory"
        ) from e

    try:
        buffer.seek(0)
    except Exception as e:
        raise exceptions.BufferError("Failed to reset buffer position") from e

    try:
        shutil.rmtree(tmp_folder_path)
    except Exception as e:
        raise exceptions.FileDeletionError(
            f"Failed to delete temporary folder at {tmp_folder_path}"
        ) from e

    return buffer


def push_POST(remote: str, buffer: io.BytesIO) -> requests.Response:
    """
    Make a POST request to 'remote', sending 'buffer' as a file.

    Return the server response of the POST request to 'remote'.
    """

    if not urlsplit(remote).path.endswith(
        f"/repos/{utils.working_directory_path.name}"
    ):
        raise exceptions.InvalidAPIURLError(
            "API URL must end with '/repos/<repo_name>'"
        )

    try:
        response = requests.post(
            f"{remote}/push",
            files=[("file", (Path.cwd().name + ".zip", buffer, "application/zip"))],
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            f"Failed to push to repository {remote}/push"
        ) from e

    return response


def main() -> None:
    """Run functions for the <sccs push> command."""

    remote = utils.get_key_from_config("remote")

    print(f"Getting list of objects on remote repository at {remote}...\n")
    GET_response = push_GET(remote)
    remote_objects = GET_response.json().get("objects", [])

    print(f"Status code: {GET_response.status_code}\n")
    if 200 <= GET_response.status_code < 300:
        print(f"Changes pushed successfully to {remote}/push\n")
    else:
        raise exceptions.HTTPPostRequestError(
            f"Failed to push to repository: {GET_response.text}"
        )

    local_objects = get_repo_objects()
    obj_to_upload = compare_hash_lists(remote_objects, local_objects)
    buffer = zip_files_to_upload(obj_to_upload)

    print(
        f"Uploading {len(obj_to_upload)} objects to remote repository at {remote}...\n"
    )
    POST_response = push_POST(remote, buffer)
    print(f"Status code: {POST_response.status_code}\n")
    if 200 <= POST_response.status_code < 300:
        print(f"Changes pushed successfully to {remote}/push\n")
    else:
        raise exceptions.HTTPPostRequestError(
            f"Failed to push to repository: {POST_response.text}"
        )


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
