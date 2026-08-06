#!/usr/bin/env python3
"""Commit latest changes to the current branch."""

from pathlib import Path

import exceptions
import utils
from repository_layout import (
    RepositoryData,
    RepositoryWrite,
    RepositoryStatus,
    TargetBranch,
)
from constants_classes import SCCSConstants


def print_commit_confirmation_message(c: SCCSConstants, sha_hash: str) -> None:
    """Print a confirmation message for the commit using 'sha_hash'."""

    try:
        print(c.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(sha_hash=sha_hash))
    except Exception as e:
        raise exceptions.SCCSException(c.COMMIT_FAILURE_ERROR_MESSAGE) from e


def validate_commit_message(c: SCCSConstants, commit_message: str) -> None:

    if commit_message is None or not commit_message:
        raise exceptions.EmptyArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.COMMIT_MESSAGE_FIELD_NAME))


def main(c: SCCSConstants, commit_message: str, rd: RepositoryData, rs: RepositoryStatus, rw: RepositoryWrite) -> None:
    """Run functions for the <sccs commit> command."""

    rw.target.set(rd.current_branch())

    rs.check_repository_layout()

    validate_commit_message(c, commit_message)

    print_commit_confirmation_message(c, rw.commit_changes(commit_message))

    rw.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
