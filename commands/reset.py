#!/usr/bin/env python3

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    TargetBranch,
)


def reset(
    c: SCCSConstants, rd: RepositoryData, staging_root: Path, rs: RepositoryStatus
) -> None:

    rs.target.set(rd.current_branch())

    try:
        shutil.copy2(
            rd.commit_identifier_to_full_path(
                rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
            ),
            staging_root / rd.paths.document_path().name,
        )
    except Exception as e:
        raise exceptions.SCCSException(c.RESET_ERROR_MESSAGE) from e

    rs.target.reset()


def print_reset_success_message(c: SCCSConstants) -> None:

    print(c.RESET_SUCCESS_MESSAGE)


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    staging_root = utils.create_staging_directory(c, utils.current_symlink_path(c, rp.repository_name))

    try:
        shutil.copytree(utils.current_symlink_path(c, rp.repository_name), staging_root, dirs_exist_ok=True)

        reset(c, rd, staging_root, rs)
        utils.promote_versioned(c, staging_root, rp.repository_name)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_reset_success_message(c)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().parent.parent.name
    repository_root = utils.current_symlink_path(c, repository_name)
    utils.run_command(
        main,
        RepositoryData(repository_root, repository_name, c, target),
        RepositoryPaths(repository_root, repository_name, c, target),
        RepositoryStatus(repository_root, repository_name, c, target),
    )
