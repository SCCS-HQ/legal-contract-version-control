#!/usr/bin/env python3
"""Clone a hosted SCCS repository with a URL"""

import io
import sys
import zipfile

import exceptions
import requests
import utils
from pathlib import Path
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())

def resolve_entered_url() -> str:
    """
    Resolve the entered URL by adding 'https://' if missing and appending '/clone'
    if missing.

    Return 'url' so it begins with 'https://' and ends with '/clone/'.
    """

    url = utils.entered_arguement(2)

    if url == "":
        print("No URL entered.\n")
        raise exceptions.InvalidArgumentError("No URL entered.")

    if not url.startswith("http://") and not url.startswith("https://"):
        raise exceptions.InvalidArgumentError(
            "Invalid remote URL provided. Please provide a valid URL starting with "
            "'http://' or 'https://'."
        )

    if not url.endswith("/clone"):
        url += "/clone"

    return url


def request_repo() -> requests.Response:
    """
    Make a GET request to 'url' and ensure that the request was successful.

    Return the server response after making a get request to 'url'.
    """

    url = resolve_entered_url()

    try:
        response = requests.get(url, timeout=60)
    except Exception as e:
        raise exceptions.HTTPGetRequestError(
            f"Failed to request repository from {url}"
        ) from e
    if response.ok:
        return response
    else:
        raise exceptions.HTTPGetRequestError(f"Failed to request repository from {url}")


def unzip_repo_file(buffer: io.BytesIO) -> None:
    """Unzip 'buffer' to 'destination'."""

    try:
        zipfile.ZipFile(buffer, "r").extractall(resolve_entered_url().split("/")[-2])
    except Exception as e:
        raise exceptions.ZippingFileError(f"Failed to unzip repository file") from e


def main() -> None:
    """Run functions for the <sccs clone> command."""
    utils.check_sccs_layout()

    response = request_repo()

    repo_name = resolve_entered_url().split("/")[-2]

    print(f"Cloning repository from {resolve_entered_url()}...\n")

    buffer = io.BytesIO(response.content)

    unzip_repo_file(buffer, repo_name)

    print(f"Status Code: {response.status_code}\n")
    response.raise_for_status()
    print(f"Repository cloned successfully to ./{repo_name}\n")


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
