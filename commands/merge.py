#!/usr/bin/env python3

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


def validate_branch(
    c: SCCSConstants, branch: str | None, rd: RepositoryData
) -> None:

    if not branch:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )
    if branch == rd.current_branch():
        raise exceptions.InvalidArgumentError(
            c.CURRENT_BRANCH_MERGE_ERROR_MESSAGE
        )
    if branch not in rd.branches():
        raise exceptions.BranchNotFoundError(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch
            )
        )


def copy_branch_data(branch: str, rd: RepositoryData, rp: RepositoryPaths) -> None:

    try:
        shutil.copytree(
            rp.branch_path(branch),
            rp.branch_path(rd.current_branch()),
            dirs_exist_ok=True,
        )
    except Exception as e:
        raise exceptions.FileCopyError() from e


def copy_repo_document(
    branch: str, rd: RepositoryData, rs: RepositoryStatus, rp: RepositoryPaths
) -> None:

    rs.target.set(branch)

    try:
        shutil.copy2(
            rd.hash_to_full_path(rd.latest_commit(), c.DOCX_DIR),
            rp.document_path()
        )
    except Exception as e:
        raise exceptions.FileCopyError() from e

    rs.target.reset()


def print_merge_success_message(
    c: SCCSConstants, branch: str, rd: RepositoryData
) -> None:
    print(
        c.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(
            branch=branch, current_branch=rd.current_branch()
        )
    )


def main(
    c: SCCSConstants,
    branch: str | None,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    rs.raise_for_uncommitted_changes()

    assert branch is not None

    validate_branch(c, branch, rd)
    copy_repo_document(branch, rd, rs, rp)
    copy_branch_data(branch, rd, rp)

    rw.commit_changes(
        c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(
            branch=branch, current_branch=rd.current_branch()
        )
    )

    print_merge_success_message(c, branch, rd)

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
