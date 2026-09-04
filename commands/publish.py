#!/usr/bin/env python3

import io
import json
import os
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
    RepositoryWrite,
)


def reset_current_branch(c: SCCSConstants, rw: RepositoryWrite) -> None:

    rw.set_current_branch(c.MAIN_BRANCH_NAME)


def zip_current_directory(c: SCCSConstants) -> io.BytesIO:

    try:
        zip_buffer = io.BytesIO()
    except Exception as e:
        raise exceptions.SCCSException(
            c.ZIP_BUFFER_CREATION_FAILED_ERROR_MESSAGE
        ) from e

    try:
        with zipfile.ZipFile(
            zip_buffer,
            "w",
        ) as zf:
            for root, dirs, files in os.walk(c.WALK_ROOT):
                for i in files:
                    zf.write(Path(root) / i)
    except Exception as e:
        raise exceptions.SCCSException(c.ZIPPING_FILE_ERROR_MESSAGE) from e

    try:
        zip_buffer.seek(0)
    except Exception as e:
        raise exceptions.SCCSException(c.ZIP_BUFFER_SEEK_ERROR_MESSAGE) from e

    return zip_buffer


def post_repository(
    c: SCCSConstants,
    repository_zip: io.BytesIO,
    url: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
) -> requests.Response:

    try:
        response = requests.post(
            url,
            files=[
                (
                    c.POST_FILE_FIELD_NAME,
                    (
                        str(Path(rp.repository_name).with_suffix(c.ZIP_EXTENSION)),
                        repository_zip,
                        c.CONTENT_TYPE_ZIP,
                    ),
                ),
            ],
            data={"data": json.dumps({"remote": rd.base_repository_url()})},
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.SCCSException(c.HTTP_REQUEST_ERROR_MESSAGE) from e
    return response


def print_publish_success_message(
    c: SCCSConstants, response: requests.Response, url: str
) -> None:

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PUBLISH_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,

) -> None:
    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    reset_current_branch(c, rw)

    url = c.PUBLISH_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url())

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        staging_rw = RepositoryWrite(staging_root, c, rw.target)
        staging_rw.set_current_branch(c.MAIN_BRANCH_NAME)
        response = post_repository(c, zip_current_directory(c), url, rd, rp)
        response.raise_for_status()
        utils.promote_staging(c, staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_publish_success_message(c, response, rd.base_repository_url())

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
