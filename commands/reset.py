#!/usr/bin/env python3

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
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

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        reset(c, rd, staging_root, rs)
        utils.promote_staging(c, staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_reset_success_message(c)

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
