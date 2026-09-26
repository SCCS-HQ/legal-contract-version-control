#!/usr/bin/env python3

import io
import shutil
import zipfile

import local_sccs.exceptions as exceptions
import requests
import local_sccs.utils as utils
from local_sccs.constants_classes import SCCSConstants
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
)


def pull(c: SCCSConstants, rd: RepositoryData) -> requests.Response:
    """
    Post the local repository objects to the pull endpoint of the remote repository and
    return the response. Raise an SCCSException if the request fails.
    """

    try:
        response = requests.post(
            c.PULL_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url()),
            json={c.HTTP_OBJECTS_DICT_KEY: sorted(rd.repository_objects())},
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
    """
    Extract the files from the response into the repository root and copy the latest
    commit document to the repository document path.
    """

    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
        for i in zf.namelist():
            utils.safe_extract_zip(c, zf, i, rd.root)

    shutil.copy2(
        rd.commit_identifier_to_full_path(
            rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
        ),
        rp.document_path(),
    )


def main(
    c: SCCSConstants, rd: RepositoryData, rp: RepositoryPaths, rs: RepositoryStatus
) -> None:
    """
    Run the pull command by setting the current branch as the target, validating the
    repository layout, and requesting the remote repository from the pull endpoint.

    Update the files of a copy of the repository in a staging directory, promote the
    staging directory to the repository root, print a success message, and reset the
    target branch when the operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    response = pull(c, rd)
    response.raise_for_status()

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:

        staging_rd = RepositoryData(staging_root, rd.repository_name, c, rd.target)
        staging_rp = RepositoryPaths(staging_root, rp.repository_name, c, rp.target)

        update_repository_files(c, response, staging_rd, staging_rp)

    utils.print_remote_success_message(
        c,
        response.status_code,
        rd.config_data(c.REMOTE_KEY),
        c.PULL_SUCCESS_MESSAGE_TEMPLATE,
    )

    rs.target.reset()