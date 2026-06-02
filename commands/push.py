import io
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import exceptions
import requests
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def get_matching_file_paths(
    filename: str,
    updated_branches: list = None,
    cwd: None | Path = None,
) -> list:
    """
    Iterate through 'updated_branches' to retrieve each branch's version of 'filename'.
    """

    if cwd is None:
        cwd = Path.cwd()
    if updated_branches is None:
        updated_branches = []
    paths = []
    for i in updated_branches:
        branch_dir = cwd / ".sccs" / "branches" / i
        if branch_dir.is_dir():
            f = branch_dir / filename / f"{filename}.json"
            if f.is_file():
                paths.append(f.resolve())
    return paths


def push_GET(remote: str) -> requests.Response:
    """Make a GET request to 'remote'/push, returning the response."""

    try:
        response = requests.get(f"{remote}/push", timeout=60)
    except Exception as e:
        raise exceptions.HTTPGetRequestError() from e

    return response


def get_repo_objects(cwd: None | Path = None) -> list:
    """
    Return of list of every commit hash by iterating through the objects folder's file
    stems, and removing duplicates with a set.
    """

    if cwd is None:
        cwd = Path.cwd()
    objects_dir = cwd / ".sccs" / "objects"
    objects = list(set(i.stem for i in objects_dir.rglob("*") if i.is_file()))
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
        raise exceptions.MissingCommitObjectsError()

    return obj_to_upload


def zip_files_to_upload(obj_to_upload: list, cwd: None | Path = None) -> io.BytesIO:
    """
    Create a temporary version of the repository with only the files in 'obj_to_upload'
    and metadata files, ensuring that the folder layout is left intact. Compress said
    folder and return it as a Bytes.io memory buffer and xdelete the temporary directory.

    Return a zip archive of files in 'obj_to_upload' and metadata files using the same
    layout as a repository.
    """

    if cwd is None:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    document_path = [cwd / f"{cwd.name}.docx"]

    repo_name = cwd.name
    updated_branches = (
        utils.get_branch_data(
            key="updated_branches",
            file_path=cwd / ".sccs" / "current_branch" / "current_branch.json",
        )
        or []
    )
    current_branch_path = [cwd / ".sccs" / "current_branch" / "current_branch.json"]
    commit_msgs_path = [cwd / ".sccs" / "commit_messages" / "commit_messages.json"]
    obj_to_upload_set = set(obj_to_upload)
    objects_paths = [
        i.resolve()
        for i in (cwd / ".sccs" / "objects").rglob("*")
        if i.is_file() and i.stem in obj_to_upload_set
    ]

    history_paths = get_matching_file_paths("history", updated_branches, cwd)
    byte_hash_paths = get_matching_file_paths("commit_file_hash", updated_branches, cwd)

    files_to_upload = (
        objects_paths
        + history_paths
        + byte_hash_paths
        + document_path
        + current_branch_path
        + commit_msgs_path
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_folder_path = Path(temp_dir) / f"tmp_{repo_name}"
        for i in files_to_upload:
            (tmp_folder_path / i.relative_to(cwd).parent).mkdir(
                parents=True, exist_ok=True
            )
            shutil.copy2(i, tmp_folder_path / i.relative_to(cwd))

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
                "Failed to zip current working directory"
            ) from e

        try:
            buffer.seek(0)
        except Exception as e:
            raise exceptions.BufferError("Failed to reset buffer position") from e

    return buffer


def push_POST(remote: str, buffer: io.BytesIO) -> requests.Response:
    """
    Make a POST request to 'remote', sending 'buffer' as a file.

    Return the server response of the POST request to 'remote'.
    """

    remote_path = urlsplit(remote).path.rstrip("/")
    if not remote_path.endswith(f"/repos/{Path.cwd().name}"):
        raise exceptions.InvalidAPIURLError(
            "API URL must end with '/repos/<repo_name>'"
        )

    try:
        response = requests.post(
            f"{remote}/push",
            files=[
                (
                    "file",
                    (
                        Path.cwd().name + ".zip",
                        buffer,
                        "application/zip",
                    ),
                )
            ],
            timeout=60,
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            f"Failed to push to repository {remote}/push"
        ) from e

    return response


def clear_updated_branches(cwd: None | Path = None) -> None:
    """Clear the updated branches list in the current branch file."""

    if cwd is None:
        cwd = Path.cwd()
    current_branch_file = cwd / ".sccs" / "current_branch" / "current_branch.json"

    data = utils.get_branch_data(file_path=current_branch_file)
    if data is None:
        data = {}
    data["updated_branches"] = []

    try:
        with open(current_branch_file, "w") as f:
            json.dump(data, f)
    except Exception as e:
        raise exceptions.FileWriteError(
            "Push successful, but failed to clear updated branches list in current "
            "branch file."
        ) from e


def main() -> None:
    """Run functions for the <sccs push> command."""
    utils.check_sccs_layout()

    remote = utils.get_key_from_config("remote").rstrip("/")

    print(f" Pushing changes to remote repository at {remote}...\n")

    GET_response = push_GET(remote)

    GET_response.raise_for_status()

    remote_objects = GET_response.json().get("objects", [])

    local_objects = get_repo_objects()
    obj_to_upload = compare_hash_lists(remote_objects, local_objects)
    buffer = zip_files_to_upload(obj_to_upload)

    POST_response = push_POST(remote, buffer)

    print(f"Status code: {POST_response.status_code}\n")

    POST_response.raise_for_status()
    print(f"Changes pushed successfully to {remote}/push\n")

    clear_updated_branches()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
