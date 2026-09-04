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
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    TargetBranch,
)


def pull(c: SCCSConstants, rd: RepositoryData) -> requests.Response:

    try:
        response = requests.post(
            c.PULL_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url()),
            json={c.HTTP_OBJECTS_DICT_KEY: rd.repository_objects()},
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.SCCSException(c.HTTP_REQUEST_ERROR_MESSAGE) from e

    return response


def update_repository_files(
    c: SCCSConstants,
    response: requests.Response,
    rd: RepositoryData,
    rp: RepositoryPaths,
) -> None:

    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
        for i in zf.namelist():
            utils.safe_extract_zip(c, zf, i, rd.root)

    shutil.copy2(
        rd.commit_identifier_to_full_path(
            rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
        ),
        rp.document_path(),
    )


def print_pull_success_message(
    c: SCCSConstants, response: requests.Response, url: str
) -> None:

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PULL_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(
    c: SCCSConstants, rd: RepositoryData, rp: RepositoryPaths, rs: RepositoryStatus
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    response = pull(c, rd)
    response.raise_for_status()

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        shutil.copytree(rp.root, staging_root, dirs_exist_ok=True)

        staging_rd = RepositoryData(staging_root, rd.repository_name, c, rd.target)
        staging_rp = RepositoryPaths(staging_root, rp.repository_name, c, rp.target)

        update_repository_files(c, response, staging_rd, staging_rp)
        utils.promote_staging(staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_pull_success_message(c, response, rd.config_data(c.REMOTE_KEY))

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
    )
