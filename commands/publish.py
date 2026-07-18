#!/usr/bin/env python3
"""Publish a SCCS repository to a hosted API"""

import io
import json
import os
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import exceptions
import requests
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def reset_current_branch(c: SCCSConstants, repo: RepositoryLayout) -> None:
    """
    Modify the document metadata to set the current branch to 'main' in preparation
    for publishing.
    """

    repo.set_current_branch(c.MAIN_BRANCH_NAME)


def zip_cwd(c: SCCSConstants) -> io.BytesIO:
    """
    Zip the current working directory into the memory buffer to compress before
    publication.
    """
    try:
        buffer = io.BytesIO()
    except Exception as e:
        raise exceptions.BufferError(c.BUFFER_CREATION_FAILED_ERROR_MESSAGE) from e

    try:
        with zipfile.ZipFile(buffer, "w", ) as zf:
            for root, dirs, files in os.walk(c.WALK_ROOT):
                for i in files:
                    zf.write(Path(root) / i)
    except Exception as e:
        raise exceptions.ZippingFileError(
            c.ZIPPING_FILE_ERROR_MESSAGE
        ) from e

    try:
        buffer.seek(0)
    except Exception as e:
        raise exceptions.BufferError(c.BUFFER_SEEK_ERROR_MESSAGE) from e

    return buffer


def post_repo(c: SCCSConstants, repo: RepositoryLayout, repo_zip: io.BytesIO, url: str) -> requests.Response:
    """
    Make a POST request to 'remote', sending the zipped current working directory as a file
    and 'remote' as JSON.

    Return the server response of the POST request to 'remote'.
    """

    if not urlsplit(url).path.endswith(
        c.REQUIRED_PATH_ENDING_TEMPLATE.format(repo_name=Path.cwd().name)
    ):
        raise exceptions.InvalidAPIURLError(
            c.INVALID_PATH_ENDING_ERROR_MESSAGE
        )

    try:
        response = requests.post(
            url,
            files=[
                (
                    c.POST_FILE_FIELD_NAME,
                    (
                        str(Path(repo.repo_name).with_suffix(c.ZIP_EXTENSION)),
                        repo_zip,
                        c.CONTENT_TYPE_ZIP,
                    ),
                ),
            ],
            timeout=c.HTTP_TIMEOUT_SECONDS,
            )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            c.HTTP_POST_REQUEST_ERROR_MESSAGE_TEMPLATE.format(url=url)
        ) from e
    return response


def print_publish_success_message(c: SCCSConstants, repo: RepositoryLayout, response: requests.Response, url: str) -> None:
    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PUBLISH_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(c: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs publish> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    reset_current_branch(c, repo)

    url = c.PUBLISH_ENDPOINT_TEMPLATE.format(base_url=repo.base_repo_url())

    repo_zip = zip_cwd(c)
    response = post_repo(c, repo, repo_zip, url)

    response.raise_for_status()

    print_publish_success_message(c, repo, response, url)


if __name__ == "__main__":
    utils.run_command(main)
