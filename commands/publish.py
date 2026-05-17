#!/usr/bin/env python3
"""Publish a SCCS repository to a hosted API"""

from pathlib import Path
import requests
import zipfile
import io
import os
import exceptions
import sys
import utils


def reset_current_branch(cwd: Path = None):
    if cwd is None:
        cwd = utils.working_directory_path

    with open(Path(cwd) / ".sccs" / "current_branch" / "current_branch.json", "w", encoding="utf-8", newline="\n") as f:
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
        raise exceptions.ZippingFileError("Failed to zip current working directory") from e

    try:
        buffer.seek(0)
    except Exception as e:
        raise exceptions.BufferError("Failed to reset buffer position") from e

    return buffer


def post_repo(buffer: io.BytesIO, api_url: str) -> requests.Response:
    """Post the repository to the hosted API."""

    if not api_url.split("/")[-2] == "repos":
        raise exceptions.InvalidAPIURLError("API URL must end with '/repos/<repo_name>'")

    try:
        response = requests.post(
        f"{api_url}/publish",
        files={
            "file": (Path.cwd().name + ".zip",
            buffer, "application/zip")
            }
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(f"Failed to post repository to {api_url}/publish") from e
    return response


def main() -> None:
    """Run functions for the <sccs publish> command."""
    reset_current_branch()
    
    api_url = utils.get_key_from_config("api_url")
    print(f"Publishing repository to {api_url}...")
    response = post_repo(zip_cwd(), api_url)

    print(response.status_code)
    print(response.json())


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