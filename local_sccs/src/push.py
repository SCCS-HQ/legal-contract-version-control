#!/usr/bin/env python3

import io
import os
import shutil
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import local_sccs.src.exceptions as exceptions
import requests
import local_sccs.src.utils as utils
from local_sccs.src.constants_classes import SCCSConstants
from local_sccs.src.repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    TargetBranch,
)


def _snapshot_file(src: Path, dst: Path) -> None:
    """Mirror `src` to `dst` cheaply.

    Tries a hardlink first (O(1), same filesystem, no extra disk usage);
    falls back to shutil.copy2 on any failure (cross-filesystem, EPERM, etc.).
    """
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def clear_updated_branches(ri: RepositoryIO) -> None:
    """
    Clear the list of updated branches in the current branch metadata.
    """

    def clear(updated: list[str]) -> bool:
        updated.clear()
        return True

    ri.mutate_updated_branches(clear)


def compare_commit_identifier_lists(
    remote_objects: list[str], rd: RepositoryData
) -> list[str]:
    """
    Compare the remote commit identifiers to the local commit identifiers and return the
    local identifiers that are missing from the remote repository. Raise an
    SCCSException if the remote repository contains commit identifiers that are missing
    locally.
    """

    local_objects = rd.repository_objects()

    object_to_upload = list(set(local_objects) - set(remote_objects))
    if list(set(remote_objects) - set(local_objects)):
        raise exceptions.SCCSException(c.MISSING_REMOTE_OBJECTS_ERROR_MESSAGE)

    return object_to_upload


def fetch_remote_objects(c: SCCSConstants, rd: RepositoryData) -> requests.Response:
    """
    Request the commit identifiers stored on the remote repository and return the
    response. Raise an SCCSException if the request fails.
    """

    try:
        return requests.get(
            c.PUSH_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url()),
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.SCCSException(c.PUSH_HTTP_REQUEST_ERROR_MESSAGE) from e


def upload_objects(
    c: SCCSConstants, buffer: io.BytesIO, rd: RepositoryData, rp: RepositoryPaths
) -> requests.Response:
    """
    Upload the zipped objects to the push endpoint of the remote repository and return
    the response. Raise an SCCSException if the remote path ending is invalid or the
    request fails.
    """

    remote = rd.base_repository_url()

    remote_path = urlsplit(remote).path.rstrip(c.PATH_SEPARATOR)
    if not remote_path.endswith(
        c.REQUIRED_PATH_ENDING_TEMPLATE.format(repo_name=rp.repository_name)
    ):
        raise exceptions.SCCSException(c.INVALID_PATH_ENDING_ERROR_MESSAGE)

    try:
        response = requests.post(
            c.PUSH_ENDPOINT_TEMPLATE.format(base_url=remote),
            files=[
                (
                    c.POST_FILE_FIELD_NAME,
                    (
                        str(Path(rp.repository_name).with_suffix(c.ZIP_EXTENSION)),
                        buffer,
                        c.CONTENT_TYPE_ZIP,
                    ),
                )
            ],
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.SCCSException(
            c.PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE.format(url=remote)
        ) from e

    return response


def zip_files_to_upload(
    c: SCCSConstants,
    remote_objects: list[str],
    rd: RepositoryData,
    rp: RepositoryPaths,
) -> io.BytesIO:
    """
    Zip the local objects that are missing from the remote repository, along with the
    document and metadata files, into a buffer and return it. Raise an SCCSException if
    the files cannot be zipped or the buffer position cannot be reset.
    """

    files_to_upload = (
        [
            i.resolve()
            for i in (rp.objects_path()).rglob(c.RGLOB_ALL_FILES_PATTERN)
            if i.is_file()
            and i.stem in set(compare_commit_identifier_lists(remote_objects, rd))
        ]
        + [rp.document_path()]
        + [rp.metadata_path()]
    )

    staging_root = utils.create_staging_directory(c, rp.root)
    try:
        for i in files_to_upload:
            dst = staging_root / i.relative_to(rp.root)
            dst.parent.mkdir(parents=True, exist_ok=True)
            _snapshot_file(i, dst)

        with utils.zip_buffer(c, zipfile.ZIP_DEFLATED) as (buffer, zf):
            for i in files_to_upload:
                snapshot_path = staging_root / i.relative_to(rp.root)
                zf.write(snapshot_path, arcname=i.relative_to(rp.root))
    finally:
        utils.cleanup_staging(staging_root)

    return buffer


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:
    """
    Run the push command by setting the current branch as the target, validating the
    repository layout, comparing the local and remote objects, and uploading the missing
    objects to the remote repository.

    Clear the updated branches in the current branch metadata of a copy of the
    repository in a staging directory, promote the staging directory to the repository
    root, print a success message, and reset the target branch when the operation
    completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    remote = rd.base_repository_url()

    remote_objects_response = fetch_remote_objects(c, rd)

    remote_objects_response.raise_for_status()

    remote_objects = remote_objects_response.json()[c.HTTP_OBJECTS_DICT_KEY]

    buffer = zip_files_to_upload(c, remote_objects, rd, rp)

    upload_response = upload_objects(c, buffer, rd, rp)

    upload_response.raise_for_status()

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:

        staging_ri = RepositoryIO(staging_root, ri.repository_name, c, ri.target)
        clear_updated_branches(staging_ri)

    utils.print_remote_success_message(
        c, upload_response.status_code, remote, c.PUSH_SUCCESS_MESSAGE_TEMPLATE
    )

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryIO(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
    )
