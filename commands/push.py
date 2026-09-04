#!/usr/bin/env python3

import io
import os
import shutil
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import exceptions
import requests
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
)


def fetch_remote_objects(c: SCCSConstants, rd: RepositoryData) -> requests.Response:

    try:
        return requests.get(
            c.PUSH_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url()),
            timeout=c.HTTP_TIMEOUT_SECONDS,
        )
    except Exception as e:
        raise exceptions.SCCSException(c.PUSH_HTTP_REQUEST_ERROR_MESSAGE) from e





def compare_commit_identifier_lists(
    remote_objects: list[str], rd: RepositoryData
) -> list[str]:

    local_objects = rd.repository_objects()

    object_to_upload = list(set(local_objects) - set(remote_objects))
    if list(set(remote_objects) - set(local_objects)):
        raise exceptions.SCCSException(c.MISSING_REMOTE_OBJECTS_ERROR_MESSAGE)

    return object_to_upload


def _snapshot_file(src: Path, dst: Path) -> None:
    """Mirror `src` to `dst` cheaply.

    Tries a hardlink first (O(1), same filesystem, no extra disk usage);
    falls back to shutil.copy2 on any failure (cross-filesystem, EPERM, etc.).
    """
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def zip_files_to_upload(
    c: SCCSConstants,
    remote_objects: list[str],
    rd: RepositoryData,
    rp: RepositoryPaths,
) -> io.BytesIO:


    files_to_upload = (
        [    
            i.resolve()
            for i in (rp.objects_path()).rglob(c.RGLOB_ALL_FILES_PATTERN)
            if i.is_file() and i.stem in set(
                compare_commit_identifier_lists(remote_objects, rd)
            )
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

        buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for i in files_to_upload:
                    snapshot_path = staging_root / i.relative_to(rp.root)
                    zf.write(snapshot_path, arcname=i.relative_to(rp.root))
        except Exception as e:
            raise exceptions.SCCSException(c.ZIPPING_FILE_ERROR_MESSAGE) from e

        try:
            buffer.seek(0)
        except Exception as e:
            raise exceptions.SCCSException(c.ZIP_BUFFER_SEEK_ERROR_MESSAGE) from e
    finally:
        utils.cleanup_staging(staging_root)

    return buffer


def upload_objects(
    c: SCCSConstants, buffer: io.BytesIO, rd: RepositoryData, rp: RepositoryPaths
) -> requests.Response:

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


def clear_updated_branches(
    c: SCCSConstants, ri: RepositoryIO, rp: RepositoryPaths
) -> None:

    data = ri.read_current_branch_data()
    data[c.UPDATED_BRANCHES_DICT_KEY] = []
    ri.write_current_branch_data(data)


def print_push_success_message(
    c: SCCSConstants, response: requests.Response, url: str
) -> None:

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.PUSH_SUCCESS_MESSAGE_TEMPLATE.format(url=url))


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    remote = rd.base_repository_url()

    remote_objects_response = fetch_remote_objects(c, rd)

    remote_objects_response.raise_for_status()

    remote_objects = remote_objects_response.json()[c.HTTP_OBJECTS_DICT_KEY]

    buffer = zip_files_to_upload(c, remote_objects, rd, rp)

    upload_response = upload_objects(c, buffer, rd, rp)

    upload_response.raise_for_status()

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        staging_ri = RepositoryIO(staging_root, ri.repository_name, c, ri.target)
        clear_updated_branches(c, staging_ri, rp)
        utils.promote_staging(staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_push_success_message(c, upload_response, remote)

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
