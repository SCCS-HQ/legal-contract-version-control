#!/usr/bin/env python3
"""Switch between document branches."""

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryPaths,
    RepositoryData,
    RepositoryWrite,
    RepositoryStatus,
    TargetBranch,
)


def check_branch_to_switch(c: SCCSConstants, branch_to_switch: str, rs: RepositoryStatus) -> None:
    """Check if the branch to switch to is valid."""

    if not branch_to_switch:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )

    if not rs.branch_exists(branch_to_switch):
        raise exceptions.BranchNotFoundError(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch)
        )


def check_commit(branch_to_switch: str, rd: RepositoryData) -> None:
    """
    Check if the commit object exists in the document history.
    """

    rd.target.set(branch_to_switch)

    commit = rd.hash_to_full_path(rd.latest_commit(), c.DOCX_DIR)

    if not (commit).is_file():
        raise exceptions.CommitNotFoundError

    rd.target.reset()


def copy_commit_to_main(c: SCCSConstants, branch_to_switch: str, rd: RepositoryData, rp: RepositoryPaths) -> None:
    """Copy the commit file to the main document."""
    
    rd.target.set(branch_to_switch)

    try:
        shutil.copy2(
            rd.hash_to_full_path(rd.latest_commit(), c.DOCX_DIR),
            (rp.document_path()),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e

    rd.target.reset()

def print_confirmation(c: SCCSConstants, branch_to_switch: str) -> None:
    """Print a confirmation message for successful branch switch."""

    print(c.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch))


def main(c: SCCSConstants, branch_to_switch: str, rd: RepositoryData, rs: RepositoryStatus, rp: RepositoryPaths, rw: RepositoryWrite) -> None:
    """Run functions for the <sccs switch> command."""
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    rs.raise_for_uncommitted_changes()

    check_branch_to_switch(c, branch_to_switch, rs)

    check_commit(branch_to_switch, rd)

    copy_commit_to_main(c, branch_to_switch, rd, rp)

    rw.set_current_branch(branch_to_switch)

    print_confirmation(c, branch_to_switch)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )

