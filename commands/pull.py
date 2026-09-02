#!/usr/bin/env python3

import io
import shutil
import zipfile
from pathlib import Path

import exceptions
import requests
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
)


def pull(c: SCCSConstants, rd: RepositoryData) -> requests.Response:

    remote_data = {c.HTTP_OBJECTS_DICT_KEY: rd.repository_objects()}
    url = c.PULL_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url())

    try:
        response = requests.post(url, json=remote_data, timeout=c.HTTP_TIMEOUT_SECONDS)
    except Exception as e:
        raise exceptions.SCCSException(c.HTTP_REQUEST_ERROR_MESSAGE) from e

    return response


def update_repository_files(c: SCCSConstants, response: requests.Response, rd: RepositoryData, rp: RepositoryPaths) -> None:

    destination = Path.cwd()
    try:
        with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
            print(i for i in zf.namelist())
            for i in zf.namelist():
                utils.safe_extract_zip(c, zf, i, destination)

        shutil.copy2(
            rd.commit_identifier_to_full_path(
                rd.latest_commit_identifier(),
                c.DOCUMENT_DIRECTORY
            ),
            rp.document_path()
        )
    
    except exceptions.SCCSException as e:
        raise e


def print_pull_success_message(
    c: SCCSConstants, response: requests.Response, url: str
) -> None:

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PULL_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(c: SCCSConstants, rd: RepositoryData, rp: RepositoryPaths, rs: RepositoryStatus) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    response = pull(c, rd)
    response.raise_for_status()

    update_repository_files(c, response, rd, rp)

    print_pull_success_message(c, response, rd.config_data(c.REMOTE_KEY))

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
    )
