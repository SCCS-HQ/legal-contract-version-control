#!/usr/bin/env python3
"""Publish a SCCS repository to a hosted API"""

import io
import json
import os
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import exceptions
import requests
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def reset_current_branch(cwd: Path | None = None) -> None:
    """
    Modify the document metadata to set the current branch to 'main' in preparation
    for publishing.
    """

    Repository.set_current_branch("main", cwd)


def zip_cwd() -> io.BytesIO:
    """
    Zip the current working directory into the memory buffer to compress before
    publication.
    """
    try:
        buffer = io.BytesIO()
    except Exception as e:
        raise exceptions.BufferError("Failed to create memory buffer") from e

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk("."):
                for i in files:
                    zf.write(Path(root) / i)
    except Exception as e:
        raise exceptions.ZippingFileError(
            "Failed to zip current working directory"
        ) from e

    try:
        buffer.seek(0)
    except Exception as e:
        raise exceptions.BufferError("Failed to reset buffer position") from e

    return buffer


def post_repo() -> requests.Response:
    """
    Make a POST request to 'remote', sending the zipped current working directory as a file
    and 'remote' as JSON.

    Return the server response of the POST request to 'remote'.
    """

    url = f"{Repository.config_data('remote').rstrip('/')}/publish"

    if not urlsplit(url).path.endswith(
        f"/repos/{Path.cwd().name}"
    ):
        raise exceptions.InvalidAPIURLError(
            "API URL must end with '/repos/<repo_name>'"
        )

    try:
        response = requests.post(
            url,
            files=[
                ("file", (Path.cwd().name + ".zip", zip_cwd(), "application/zip")),
                ("data", (None, json.dumps({"remote": url}), "application/json")),
            ],
            timeout=60,
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            f"Failed to post repository to {url}"
        ) from e
    return response


def main() -> None:
    """Run functions for the <sccs publish> command."""
    Repository.check_repository_layout()

    reset_current_branch()

    url = f"{Repository.config_data('remote').rstrip('/')}/publish"
    print(f"Publishing repository to {url}...\n")
    response = post_repo()

    print(f"Status Code: {response.status_code}\n")
    response.raise_for_status()
    print(f"Repository published successfully to {url}\n")


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
