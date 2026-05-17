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


def resolve_entered_url(url: str = get_entered_url()) -> str:
    """
    Resolve the entered URL by adding 'https://' if missing and appending '/clone'
    if missing."""

    if url is None:
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


def request_repo(url: str = resolve_entered_url()) -> requests.Response:
    """Request the repository from the given URL."""
    try:
        response = requests.get(url)
    except Exception as e:
        raise exceptions.HTTPGetRequestError(
            f"Failed to request repository from {url}/clone"
        ) from e
    return response


def unzip_repo_file(buffer: io.BytesIO, destination: str) -> None:
    """
    Unzip the repo file. using the buffer where the repository is held and the folder
    where it should be extracted."""

    try:
        zipfile.ZipFile(buffer, "r").extractall(destination)
    except Exception as e:
        raise exceptions.ZippingFileError(f"Failed to unzip repository file") from e


def main() -> None:
    """Run functions for the <sccs publish> command."""

    response = request_repo()

    buffer = io.BytesIO(response.content)

    unzip_repo_file(buffer, resolve_entered_url().split("/")[-2])

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
else:
    raise exceptions.FileImportedAsModuleError(
        "This file cannot be run as a module. Please run it as a script."
    )
