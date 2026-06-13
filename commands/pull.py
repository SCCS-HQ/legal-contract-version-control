import io
import sys
import zipfile
from pathlib import Path

import exceptions
import requests
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def get_repo_objects() -> list:
    """
    Return of list of every commit hash by iterating through the objects folder's file
    stems, and removing duplicates with a set.
    """
    
    return list(set(i.stem for i in Repository.objects_path().rglob("*") if i.is_file()))


def pull() -> requests.Response:
    """Make a POST request to 'remote'/pull, returning the response."""

    data = {"objects": get_repo_objects()}
    url = f"{Repository.config_data('remote').rstrip('/')}/pull"

    try:
        response = requests.post(url, json=data, timeout=60)
    except Exception as e:
        raise exceptions.HTTPPostRequestError() from e

    return response


def update_repo_files(response: requests.Response) -> None:
    """
    Unzip the file in 'response' to 'destination'.
    """

    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
        zf.extractall(Path.cwd())


def main():
    """Run functions for the <sccs pull> command."""
    Repository.check_repository_layout()

    remote = Repository.config_data("remote")
    
    print(f"Pulling repository from {remote}...\n")

    response = pull()

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
