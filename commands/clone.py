#!/usr/bin/env python3
"""Clone a hosted SCCS repository with a URL"""

import io
import sys
import zipfile

import exceptions
import requests


def get_entered_url() -> str | None:
    """Retrieve the URL entered by the user."""
    return sys.argv[2] if len(sys.argv) > 2 else None

def resolve_entered_url(url: str | None = None) -> str:
    """
    Resolve the entered URL by adding 'https://' if missing and appending '/clone'
    if missing."""

    if url is None:
        url = get_entered_url()

    if url == "":
        print("No URL entered.")
        raise exceptions.InvalidArgumentError("No URL entered.")

    if not url.startswith("http://") and not url.startswith("https://"):
        raise exceptions.InvalidArgumentError(
            "Invalid remote URL provided. Please provide a valid URL starting with "
            "'http://' or 'https://'."
        )

    if not url.endswith("/clone"):
        url += "/clone"

    return url


def request_repo(url: str | None = None) -> requests.Response:
    """Request the repository from the given URL."""

    if url is None:
        url = resolve_entered_url()

    try:
        response = requests.get(url)
    except Exception as e:
        raise exceptions.HTTPGetRequestError(
            f"Failed to request repository from {url}"
        ) from e
    if response.ok:
        return response
    else:
        raise exceptions.HTTPGetRequestError(f"Failed to request repository from {url}")


def unzip_repo_file(buffer: io.BytesIO, destination: str) -> None:
    """
    Unzip the repo file. using the buffer where the repository is held and the folder
    where it should be extracted."""

    try:
        zipfile.ZipFile(buffer, "r").extractall(destination)
    except Exception as e:
        raise exceptions.ZippingFileError(f"Failed to unzip repository file") from e


def main() -> None:
    """Run functions for the <sccs clone> command."""
    response = request_repo()

    repo_name = resolve_entered_url().split("/")[-2]

    print(f"Cloning repository from {resolve_entered_url()}...")

    buffer = io.BytesIO(response.content)

    unzip_repo_file(buffer, repo_name)

    print(f"Status Code: {response.status_code}")
    if 200 <= response.status_code < 300:
        print(f"Repository cloned successfully to ./{repo_name}")
    else:
        raise exceptions.HTTPGetRequestError(
            f"Failed to clone repository: {response.text}"
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
