#!/usr/bin/env python3
"""Merge branches in the SCCS repository."""

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


def validate_branch(c: SCCSConstants, branch: str, rd: RepositoryData) -> None:
    """Validate that the entered branch is valid, exists, and is not the current branch."""

    if not branch:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )
    if branch == rd.current_branch():
        raise exceptions.InvalidArgumentError(
            c.CURRENT_BRANCH_MERGE_ERROR_MESSAGE
        )
    if branch not in rd.branches():
        raise exceptions.BranchNotFoundError(c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch))


def copy_branch_data(branch: str, rd: RepositoryData, rp: RepositoryPaths) -> None:
    """Copy the data from the source branch to the target branch."""

    try:
        shutil.copytree(rp.branch_path(branch), rp.branch_path(rd.current_branch()), dirs_exist_ok=True)
    except Exception as e:
        raise exceptions.FileCopyError


def copy_repo_document(branch: str, rd: RepositoryData, rp: RepositoryPaths) -> None:
    """Copy the repo document from the source branch to the target branch."""

    try:
        shutil.copy2(
            rd.hash_to_full_path(rd.latest_commit(branch)),
            rp.document_path()
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_merge_success_message(c: SCCSConstants, branch: str, rd: RepositoryData) -> None:
    """Print a success message after merging the branches."""
    print(
        c.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(branch=branch, current_branch=rd.current_branch())
    )


def main(c: SCCSConstants, branch: str, rd: RepositoryData, rs: RepositoryStatus, rp: RepositoryPaths, rw: RepositoryWrite) -> None:
    """Merge the entered branch into the current branch."""

    rs.check_repository_layout()

    rs.check_for_uncommitted_changes()

    validate_branch(c, branch, rd)
    copy_repo_document(branch, rd, rp)
    copy_branch_data(branch, rd, rp)

    rw.commit_changes(
        c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(branch=branch, current_branch=rd.current_branch())
    )

    print_merge_success_message(c, branch, rd)


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
