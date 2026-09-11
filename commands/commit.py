#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def validate_commit_message(c: SCCSConstants, commit_message: str | None) -> None:

    if commit_message is None or not commit_message:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=c.COMMIT_MESSAGE_FIELD_NAME
            )
        )


def print_commit_success_message(c: SCCSConstants, commit_identifier: str) -> None:

    print(
        c.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
        )
    )


def finalize_commit(
    c: SCCSConstants, rw: RepositoryWrite, staging_rw: RepositoryWrite
) -> None:

    history = rw.io.read_history()
    next_version_number = history[c.LATEST_COMMIT_NUMBER_DICT_KEY] + 1

    new_version_path = (
        Path.home()
        / c.SCCS_DIRECTORY
        / c.REPOSITORIES_PATH_SEGMENT
        / staging_rw.repository_name
        / c.VERSIONS_PATH_SEGMENT
        / c.VERSION_PATH_SEGMENT_TEMPLATE.format(version_number=next_version_number)
    )

    utils.promote_staging(c, staging_rw.root, new_version_path)

    temporary_root = rw.root.with_name(c.TEMPORARY_DIRECTORY_PREFIX + rw.root.name)

    try:
        temporary_root.symlink_to(new_version_path, target_is_directory=True)
        os.replace(temporary_root, rw.root)
        
    except Exception:
        shutil.rmtree(new_version_path)
        shutil.rmtree(temporary_root)
        raise
    

def main(
    c: SCCSConstants,
    commit_message: str,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    validate_commit_message(c, commit_message)

    staging_root = utils.create_staging_directory(c, rd.root)

    try:
        shutil.copytree(rd.root, staging_root, dirs_exist_ok=True)

        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
        commit_identifier = staging_rw.commit_changes(commit_message)

        finalize_commit(c, rw, staging_rw)

    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_commit_success_message(c, commit_identifier)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().parent.parent.name
    repository_root = (
        Path.home() /
        c.SCCS_DIRECTORY /
        c.REPOSITORIES_PATH_SEGMENT /
        repository_name /
        c.VERSIONS_PATH_SEGMENT /
        c.CURRENT_PATH_SEGMENT
    )
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(repository_root, repository_name, c, target),
        RepositoryStatus(repository_root, repository_name, c, target),
        RepositoryWrite(repository_root, repository_name, c, target),
    )
