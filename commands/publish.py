#!/usr/bin/env python3

import io
import json
import os
from pathlib import Path

import exceptions
import requests
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def zip_current_directory(c: SCCSConstants) -> io.BytesIO:
    """
    Zip the contents of the current directory into a buffer and return it. Raise an
    SCCSException if the files cannot be zipped.
    """

    with utils.zip_buffer(c) as (zip_buffer, zf):
        for root, dirs, files in os.walk(c.WALK_ROOT):
            for i in files:
                zf.write(Path(root) / i)

    return zip_buffer


def post_repository(
    c: SCCSConstants,
    repository_zip: io.BytesIO,
    url: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
) -> requests.Response:
    """
    Post the zipped repository and the repository remote to the entered URL and return
    the response. Raise an SCCSException if the request fails.
    """

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
            data={c.DATA_DATA: json.dumps({c.DATA_REMOTE: rd.base_repository_url()})},
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.SCCSException(c.HTTP_REQUEST_ERROR_MESSAGE) from e
    return response


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the publish command by setting the current branch as the target, validating the
    repository layout, and posting the zipped repository to the hosting service with the
    main branch set as the current branch of a copy of the repository in a staging
    directory.

    Promote the staging directory to the repository root, print a success message, and
    reset the target branch when the operation completes.
    """
    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    url = c.PUBLISH_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url())

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:

        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
        staging_rw.set_current_branch(c.MAIN_BRANCH_NAME)
        response = post_repository(
            c,
            zip_current_directory(c),
            url,
            rd,
            rp,
        )
        response.raise_for_status()

    utils.print_remote_success_message(
        c, response.status_code, url, c.PUBLISH_SUCCESS_MESSAGE_TEMPLATE
    )

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
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )
