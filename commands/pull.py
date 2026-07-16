#!/usr/bin/env python3
"""Pull the repository from the remote server."""

import io
import sys
from urllib import response
import zipfile
from pathlib import Path

import exceptions
import requests
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def pull(constants: SCCSConstants, repo: RepositoryLayout) -> requests.Response:
    """Make a POST request to 'remote'/pull, returning the response."""

    data = {constants.HTTP_OBJECTS_DATA_KEY: repo.repo_objects()}
    url = constants.PULL_ENDPOINT_TEMPLATE.format(base_url=repo.config_data(constants.REMOTE_KEY).rstrip(constants.URL_PARTS_SEPARATOR))

    try:
        response = requests.post(url, json=data, timeout=constants.HTTP_TIMEOUT_SECONDS)
    except Exception as e:
        raise exceptions.HTTPPostRequestError(constants.HTTP_POST_REQUEST_ERROR_MESSAGE_TEMPLATE.format(url=url)) from e

    return response


def update_repo_files(response: requests.Response) -> None:
    """
    Unzip the file in 'response' to 'destination'.
    """

    try:
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
            zf.extractall(Path.cwd())
    except Exception as e:
        raise exceptions.UnzipError(constants.UNZIP_FAILED_ERROR_MESSAGE) from e

def print_pull_success_message(constants: SCCSConstants, response: requests.Response, url: str) -> None:
    """Print a success message after pulling the repository."""

    print(constants.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(constants.PULL_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs pull> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    remote = repo.config_data(constants.REMOTE_KEY)
    
    response = pull(constants, repo)
    response.raise_for_status()

    update_repo_files(response)
    
    print_pull_success_message(constants, response, remote)

    


if __name__ == "__main__":
    utils.run_command(main)
