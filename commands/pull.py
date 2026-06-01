import sys
import zipfile
from pathlib import Path
import requests
import utils
import exceptions
import io


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


def pull(remote: str, data: dict) -> requests.Response:
    """Make a GET request to 'remote'/pull, returning the response."""

    try:
        response = requests.post(f"{remote}/pull", json=data, timeout=60)
    except Exception as e:
        raise exceptions.HTTPGetRequestError() from e

    return response


def update_repo_files(
        response: requests.Response, cwd: None | Path = None
    ) -> io.BytesIO:
    """
    Unzip the file in 'response' to 'destination'.
    """

    if cwd is None:
        cwd = utils.working_directory_path


    buffer = io.BytesIO()

    for chunk in response.iter_content(chunk_size=8192):
        buffer.write(chunk)

    buffer.seek(0)

    with zipfile.ZipFile(buffer, "r") as zf:
        zf.extractall(cwd)


def main():
    """Run functions for the <sccs pull> command."""

    response = pull(
        utils.get_key_from_config("remote"), {"objects": get_repo_objects()})
    print(response.status_code)

if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
