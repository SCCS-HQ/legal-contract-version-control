#!/usr/bin/env python3
"""Pull the repository from the remote server."""

import io
import zipfile
from pathlib import Path

import exceptions
import requests
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryStatus,
    TargetBranch,
)


def pull(c: SCCSConstants, rd: RepositoryData) -> requests.Response:
    """Make a POST request to 'remote'/pull, returning the response."""

    data = {c.HTTP_OBJECTS_DICT_KEY: rd.repo_objects()}
    url = c.PULL_ENDPOINT_TEMPLATE.format(base_url=rd.base_repo_url())

    try:
        response = requests.post(url, json=data, timeout=c.HTTP_TIMEOUT_SECONDS)
    except Exception as e:
        raise exceptions.HTTPPostRequestError(c.HTTP_REQUEST_ERROR_MESSAGE) from e

    return response


def update_repo_files(c: SCCSConstants, response: requests.Response) -> None:
    """
    Unzip the file in 'response' to 'destination'.
    """

    try:
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
            zf.extractall(Path.cwd())
    except Exception as e:
        raise exceptions.ZippingFileError(c.UNZIP_FAILED_ERROR_MESSAGE) from e


def print_pull_success_message(c: SCCSConstants, response: requests.Response, url: str) -> None:
    """Print a success message after pulling the repository."""

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PULL_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(c: SCCSConstants, rd: RepositoryData, rs: RepositoryStatus) -> None:
    """Run functions for the <sccs pull> command."""
    rs.check_repository_layout()

    rs.check_for_uncommitted_changes()

    remote = rd.config_data(c.REMOTE_KEY)

    response = pull(c, rd)
    response.raise_for_status()

    update_repo_files(c, response)

    print_pull_success_message(c, response, remote)


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
    )
