import io
import json
import os
from pathlib import Path

import requests
from avora import utils
from avora.constants_classes import AvoraConstants
from avora.exceptions import AvoraException
from avora.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
)


def post_repository(
    c: AvoraConstants,
    repository_zip: io.BytesIO,
    url: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
) -> requests.Response:
    """
    Post the zipped repository and the repository remote to the entered URL and return
    the response. Raise an AvoraException if the request fails.
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
        raise AvoraException(c.HTTP_REQUEST_ERROR_MESSAGE) from e
    return response


def zip_current_directory(c: AvoraConstants) -> io.BytesIO:
    """
    Zip the contents of the current directory into a buffer and return it. Raise an
    AvoraException if the files cannot be zipped.
    """

    with utils.zip_buffer(c) as (buffer, zf):
        for root, dirs, files in os.walk(c.WALK_ROOT):
            for i in files:
                zf.write(Path(root) / i)

    return buffer


def main(
    c: AvoraConstants,
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

    try:
        rs.validate_repository_layout()
        rs.target.set(rd.current_branch())

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
    except AvoraException:
        raise
    except Exception as e:
        raise AvoraException(c.STAGED_REPOSITORY_ERROR_MESSAGE) from e
    finally:
        rs.target.reset()