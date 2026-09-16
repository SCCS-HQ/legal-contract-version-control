#!/usr/bin/env python3

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


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:
    """
    Run the reset command by setting the current branch as the target, validating the
    repository layout, and restoring the latest commit document on a copy of the
    repository in a staging directory.

    Promote the staging directory to the repository root, print a success message, and
    reset the target branch when the operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    with utils.staged_repository(c, rp.root, rp.root) as staging_root:
        utils.copy_latest_commit_document(
            rd,
            rd.current_branch(),
            staging_root / rd.paths.document_path().name,
            c.RESET_ERROR_MESSAGE,
        )

    print_reset_success_message(c)

    rs.target.reset()


def print_reset_success_message(c: SCCSConstants) -> None:
    """
    Print a success message after a successful reset operation.
    """

    print(c.RESET_SUCCESS_MESSAGE)


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
