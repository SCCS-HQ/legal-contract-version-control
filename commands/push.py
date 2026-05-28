import requests
import json
import exceptions
from pathlib import Path
import utils
import shutil
import io
import zipfile
import os
from urllib.parse import urlsplit

def push_GET(remote: str) -> list:
    try:
        response = requests.get(f"{remote}/push")
    except Exception as e:
        raise exceptions.HTTPGetRequestError()

    print(f"status code: {response.status_code}\n")

    return response

def get_repo_objects(cwd: None | Path = None) -> list:
    if cwd is None:
        cwd = utils.working_directory_path
    objects_dir = cwd / ".sccs" / "objects"
    objects = list(set(f.stem for f in objects_dir.rglob("*") if f.is_file()))
    return objects


def compare_hash_lists(remote_objects, local_objects):
    obj_to_upload = list(set(local_objects) - set(remote_objects))
    if list(set(remote_objects) - set(local_objects)):
        print(
            "Warning: There are objects on the remote that are not present locally. You"
            " must pull before pushing. - Not implemented yet"
        )

    return obj_to_upload


def zip_files_to_upload(obj_to_upload: list, cwd: None | Path = None) -> io.BytesIO:
    
    if cwd is None:
        cwd = utils.working_directory_path

    repo_name = Path(cwd).name

    if cwd is None:
            cwd = utils.working_directory_path
    updated_branches = utils.get_branch_data(key="updated_branches") 
    current_branch_path = cwd / ".sccs" / "current_branch" / "current_branch.json"
    commit_msgs_path = cwd / ".sccs" / "commit_messages" / "commit_messages.json"
    objects_paths = [f.resolve() for f in (cwd / ".sccs" / "objects").rglob("*") if f.is_file() and f.stem in obj_to_upload]

    history_paths = []
    byte_hash_paths = []

    for b in updated_branches:
            history_paths.extend([f.resolve() for f in (cwd / ".sccs" / "branches" / b).rglob("*") if f.is_file() and f.stem == "commit_history"])
            byte_hash_paths.extend([f.resolve() for f in (cwd / ".sccs" / "branches" / b).rglob("*") if f.is_file() and f.stem == "commit_file_hash"])

    files_to_upload = objects_paths + history_paths + byte_hash_paths + [current_branch_path, commit_msgs_path]
    
    tmp_folder_path = Path(f"tmp_{repo_name}")
    tmp_folder_path.mkdir(parents=True, exist_ok=True)

    for f in files_to_upload:
        (tmp_folder_path / f.relative_to(cwd).parent).mkdir(parents=True, exist_ok=True)

        shutil.copy2(f, tmp_folder_path / (f.relative_to(cwd)).parent)

    buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as f:
             for root, dirs, files, in os.walk(f"./tmp_{repo_name}"):
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


def push_POST(remote, buffer):

    if not urlsplit(remote).path.endswith(
        f"/repos/{utils.working_directory_path.name}"
    ):
        raise exceptions.InvalidAPIURLError(
            "API URL must end with '/repos/<repo_name>'"
        )

    try:
        response = requests.post(
            f"{remote}/push",
            files=[
                ("file", (Path.cwd().name + ".zip", buffer, "application/zip"))
            ]
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            f"Failed to push to repository {remote}/push"
        ) from e
    
    return response


def main():
    """Run functions for the <sccs push> command."""

    remote = utils.get_key_from_config("remote")

    print(f"Getting list of objects on remote repository at {remote}...")
    GET_response = push_GET(remote)
    remote_objects = GET_response.json().get("objects", [])

    print(f"Status code: {GET_response.status_code}\n")
    if 200 <=GET_response.status_code< 300:
        print(f"Changes pushed successfully to {remote}/push")
    else:
        raise exceptions.HTTPPostRequestError(
            f"Failed to push to repository: {GET_response.text}"
        )    

    local_objects = get_repo_objects()
    obj_to_upload = compare_hash_lists(remote_objects, local_objects)
    buffer = zip_files_to_upload(obj_to_upload)

    print(f"Uploading {len(obj_to_upload)} objects to remote repository at {remote}...")
    POST_response = push_POST(remote, buffer)
    print(f"Status code: {POST_response.status_code}\n")
    if 200 <=POST_response.status_code< 300:
        print(f"Changes pushed successfully to {remote}/push")
    else:
        raise exceptions.HTTPPostRequestError(
            f"Failed to push to repository: {POST_response.text}"
        )

main()