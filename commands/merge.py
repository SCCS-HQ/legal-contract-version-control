#!/usr/bin/env python3

import shutil
from pathlib import Path
from typing import Any

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def validate_branch(c: SCCSConstants, branch: str | None, rd: RepositoryData) -> None:

    if not branch:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )
    if branch == rd.current_branch():
        raise exceptions.InvalidArgumentError(c.CURRENT_BRANCH_MERGE_ERROR_MESSAGE)
    if branch not in rd.branches():
        raise exceptions.BranchNotFoundError(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch)
        )


def copy_branch_data(branch: str, rd: RepositoryData, rp: RepositoryPaths) -> None:

    source = rp.branch_path(branch)
    dest = rp.branch_path(rd.current_branch())
    c = rd.c

    def ignore_metadata(_dir, names) -> set[Any]:
        ignored = set()
        for i in names:
            if i in (c.HISTORY_DIR, c.COMMIT_FILE_HASH_DIR):
                ignored.add(i)
        return ignored

    try:
        if source.exists():
            shutil.copytree(
                source,
                dest,
                dirs_exist_ok=True,
                ignore=ignore_metadata,
            )
    except Exception as e:
        raise exceptions.FileCopyError() from e


def copy_repo_document(branch: str, rd: RepositoryData, rp: RepositoryPaths) -> None:

    original_target = rd.target.get()
    rd.target.set(branch)

    try:
        shutil.copy2(
            rd.hash_to_full_path(rd.latest_commit(), c.DOCX_DIR), rp.document_path()
        )
    except Exception as e:
        raise exceptions.FileCopyError() from e
    finally:
        rd.target.set(original_target)


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
    branch: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_branch(c, branch, rd)

    copy_repo_document(branch, rd, rp)

    copy_branch_data(branch, rd, rp)

    rw.commit_changes(
        c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(
            branch=branch, current_branch=rd.current_branch()
        ),
        allow_empty_commit=True,
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
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
