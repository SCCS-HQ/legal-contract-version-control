#!/usr/bin/env python3
"""Clone a hosted SCCS repository with a URL"""

import io
import sys
import zipfile

import exceptions
import requests
import utils
from pathlib import Path
from urllib.parse import urlsplit

CLONE_ENDPOINT = "clone"

def resolve_entered_url(url: str | None = None) -> str:
    """
    Resolve the entered URL by adding 'https://' if missing and appending '/clone'
    if missing.

    Return 'url' so it begins with 'https://' and ends with '/clone/'.
    """

    if url is None:
        url = utils.entered_arguement(2)

    if not url :
        raise exceptions.InvalidArgumentError("No URL entered.")

    if not url.startswith("http://") and not url.startswith("https://"):
        raise exceptions.InvalidArgumentError(
            "Invalid remote URL provided. Please provide a valid URL starting with "
            "'http://' or 'https://'."
        )

    if not url.endswith(CLONE_ENDPOINT):
       raise exceptions.InvalidArgumentError(
            "Invalid remote URL provided. Please provide a valid URL ending with "
            f"'{CLONE_ENDPOINT}'."
        )

    return url


def request_repo(url: str | None = None) -> requests.Response:
    """
    Make a GET request to 'url' and ensure that the request was successful.

    Return the server response after making a get request to 'url'.
    """

    if url is None:
        url = resolve_entered_url()

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.RequestException as e:
        raise exceptions.HTTPGetRequestError(
            f"Failed to request repository from {url}"
    ) from e
    
    return response


def unzip_repo_file(buffer: io.BytesIO, url: str | None = None) -> None:
    """Unzip 'buffer'."""

    if url is None:
        url = resolve_entered_url()

    path_parts = [p for p in urlsplit(url).path.split("/") if p]

    if not path_parts or path_parts[-1] != ("/" + CLONE_ENDPOINT):
        raise exceptions.InvalidArgumentError(
            f"Invalid remote URL provided. Please provide a valid URL ending with "
            f"'{CLONE_ENDPOINT}'."
        )
    
    if len(path_parts) < 2:
        raise exceptions.InvalidArgumentError("URL must include a repository name before '/clone'.")
    
    repo_name = path_parts[-2]

    try:
        zipfile.ZipFile(buffer, "r").extractall(repo_name)
    except Exception as e:
        raise exceptions.ZippingFileError("Failed to unzip repository file") from e


def print_clone_success_message(response: requests.Response) -> None:
    """Print a success message after cloning the repository."""

    print(f"Status Code: {response.status_code}\n")
    response.raise_for_status()
    print("Repository cloned successfully.\n")


def main() -> None:
    """Run functions for the <sccs clone> command."""
    url = resolve_entered_url()

    response = request_repo(url)

    buffer = io.BytesIO(response.content)

    unzip_repo_file(buffer, url)

    print_clone_success_message(response)


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
