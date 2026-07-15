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


def pull(constants: SCCSConstants, Repo: RepositoryLayout) -> requests.Response:
    """Make a POST request to 'remote'/pull, returning the response."""

    data = {constants.HTTP_OBJECTS_DATA_KEY: Repo.repo_objects()}
    # url = f"{Repo.config_data(constants.REMOTE_KEY).rstrip(constants.URL_PARTS_SEPARATOR)}/pull"
    url = constants.PULL_ENDPOINT_TEMPLATE.format(base_url=Repo.config_data(constants.REMOTE_KEY).rstrip(constants.URL_PARTS_SEPARATOR))

    try:
        response = requests.post(url, json=data, timeout=constants.HTTP_TIMEOUT_SECONDS)
    except Exception as e:
        raise exceptions.HTTPPostRequestError(constants.HTTP_POST_REQUEST_ERROR_MESSAGE.format(url=url)) from e

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


def main(constants: SCCSConstants, Repo: RepositoryLayout) -> None:
    """Run functions for the <sccs pull> command."""
    Repo.check_repository_layout()

    Repo.check_for_uncommitted_changes()

    remote = Repo.config_data(constants.REMOTE_KEY)
    
    response = pull(constants, Repo)
    response.raise_for_status()

    update_repo_files(response)
    
    print_pull_success_message(constants, response, remote)

    


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(constants, repository)

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
