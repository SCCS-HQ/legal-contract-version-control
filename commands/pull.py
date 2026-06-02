import io
import sys
import zipfile
from pathlib import Path

import exceptions
import requests
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


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


def pull(remote: str, data: dict) -> requests.Response:
    """Make a POST request to 'remote'/pull, returning the response."""

    try:
        response = requests.post(f"{remote}/pull", json=data, timeout=60)
    except Exception as e:
        raise exceptions.HTTPPostRequestError() from e

    return response


def update_repo_files(response: requests.Response, cwd: None | Path = None) -> None:
    """
    Unzip the file in 'response' to 'destination'.
    """

    if cwd is None:
        cwd = Path.cwd()

    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
        zf.extractall(cwd)


def main():
    """Run functions for the <sccs pull> command."""
    utils.check_sccs_layout()

    remote = utils.get_key_from_config("remote")
    print(f"Pulling repository from {remote}...\n")

    response = pull(remote, {"objects": get_repo_objects()})

    print(f"Status Code: {response.status_code}\n")

    response.raise_for_status()
    print(f"Repository pulled successfully from {remote}\n")

    update_repo_files(response)


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
