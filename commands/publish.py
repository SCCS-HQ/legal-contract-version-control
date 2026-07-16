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
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def reset_current_branch(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """
    Modify the document metadata to set the current branch to 'main' in preparation
    for publishing.
    """

    repo.set_current_branch(constants.MAIN_BRANCH_NAME)


def zip_cwd(constants: SCCSConstants) -> io.BytesIO:
    """
    Zip the current working directory into the memory buffer to compress before
    publication.
    """
    try:
        buffer = io.BytesIO()
    except Exception as e:
        raise exceptions.BufferError(constants.BUFFER_CREATION_FAILED_ERROR_MESSAGE) from e

    try:
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk("."):
                for i in files:
                    zf.write(Path(root) / i)
    except Exception as e:
        raise exceptions.ZippingFileError(
            constants.ZIPPING_FILE_ERROR_MESSAGE
        ) from e

    try:
        buffer.seek(0)
    except Exception as e:
        raise exceptions.BufferError(constants.BUFFER_SEEK_ERROR_MESSAGE) from e

    return buffer


def post_repo(constants: SCCSConstants, repo_zip: io.BytesIO, url: str) -> requests.Response:
    """
    Make a POST request to 'remote', sending the zipped current working directory as a file
    and 'remote' as JSON.

    Return the server response of the POST request to 'remote'.
    """

    if not urlsplit(url).path.endswith(
        constants.REQUIRED_PATH_ENDING_TEMPLATE.format(repo_name=Path.cwd().name)
    ):
        raise exceptions.InvalidAPIURLError(
            constants.INVALID_PATH_ENDING_ERROR_MESSAGE
        )

    try:
        response = requests.post(
            url,
            files=[
                (constants.POST_FILE_FIElD_NAME, (Path.cwd().name + constants.ZIP_EXTENSION, repo_zip, constants.CONTENT_TYPE_ZIP)),
                (constants.POST_DATA_FIELD_NAME, (None, json.dumps({constants.REMOTE_KEY: url}), constants.CONTENT_TYPE_JSON)),
            ],
            timeout=constants.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.HTTPPostRequestError(
            constants.HTTP_POST_REQUEST_ERROR_MESSAGE_TEMPLATE.format(url=url)
        ) from e
    return response


def print_publish_success_message(constants: SCCSConstants, response: requests.Response, url: str) -> None:
    print(constants.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(constants.PUBLISH_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs publish> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    reset_current_branch(constants, repo)

    url = constants.PUBLISH_ENDPOINT_TEMPLATE.format(base_url=repo.config_data(constants.REMOTE_KEY).rstrip(constants.URL_PARTS_SEPARATOR))

    repo_zip = zip_cwd(constants)
    response = post_repo(constants, repo_zip, url)

    response.raise_for_status()

    print_publish_success_message(constants, response, url)


if __name__ == "__main__":
    utils.run_command(main)
