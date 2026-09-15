#!/usr/bin/env python3

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


def validate_commit_message(c: SCCSConstants, commit_message: str) -> None:
    """
    Validates the entered commit message by checking if it is not empty.

    Raises an SCCSException if the commit message is invalid.
    """

    if not commit_message:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=c.COMMIT_MESSAGE_FIELD_NAME
            )
        )


def print_commit_success_message(c: SCCSConstants, commit_identifier: str) -> None:
    """
    Print a success message after a successful commit operation, including the commit
    identifier of the new commit.
    """

    print(
        c.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
        )
    )


def main(
    c: SCCSConstants,
    commit_message: str,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the commit command by setting the current branch as the target, validating the
    repository layout and commit message, and committing the changes to a copy of the
    repository in a staging directory.

    Promote the staging directory to the repository root, print a success message, and
    reset the target branch when the operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    validate_commit_message(c, commit_message)

    staging_root = utils.create_staging_directory(c, rd.root)

    try:
        shutil.copytree(rd.root, staging_root, dirs_exist_ok=True)

        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
        commit_identifier = staging_rw.commit_changes(commit_message)

        utils.promote_staging(c, staging_rw.root, rw.root)

    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_commit_success_message(c, commit_identifier)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )
