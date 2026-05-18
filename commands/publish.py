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


def reset_current_branch(cwd: Path | None = None) -> None:
    """Reset the current branch to 'main'."""

    if cwd is None:
        cwd = utils.working_directory_path

    with open(
        Path(cwd) / ".sccs" / "current_branch" / "current_branch.json",
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write('{"current_branch": "main"}')


def zip_cwd() -> io.BytesIO:
    """Zip the current working directory."""
    try:
        buffer = io.BytesIO()
    except Exception as e:
        raise exceptions.BufferError("Failed to create memory buffer") from e

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk("."):
                for file in files:
                    zip_file.write(Path(root) / file)
    except Exception as e:
        raise exceptions.ZippingFileError(
            "Failed to zip current working directory"
        ) from e

    try:
        buffer.seek(0)
    except Exception as e:
        raise exceptions.BufferError("Failed to reset buffer position") from e

    return buffer


def post_repo(buffer: io.BytesIO, remote: str) -> requests.Response:
    """Post the repository to the hosted API."""

    if not urlsplit(remote).path.endswith(
        f"/repos/{utils.working_directory_path.name}"
    ):
        raise exceptions.InvalidAPIURLError(
            "API URL must end with '/repos/<repo_name>'"
        )

    try:
        response = requests.post(
            f"{remote}/publish",
            files=[
                ("file", (Path.cwd().name + ".zip", buffer, "application/zip")),
                ("data", (None, json.dumps({"remote": remote}), "application/json")),
            ],
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            f"Failed to post repository to {remote}/publish"
        ) from e
    return response


def main() -> None:
    """Run functions for the <sccs publish> command."""
    reset_current_branch()

    remote = utils.get_key_from_config("remote")
    print(f"Publishing repository to {remote}...")
    response = post_repo(zip_cwd(), remote)

    print(f"Status Code: {response.status_code}")
    if 200 <= response.status_code < 300:
        print(f"Repository published successfully to {remote}/publish")
    else:
        raise exceptions.HTTPPostRequestError(
            f"Failed to publish repository: {response.text}"
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
