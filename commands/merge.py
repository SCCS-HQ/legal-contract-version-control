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
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )
    if branch == rd.current_branch():
        raise exceptions.SCCSException(c.CURRENT_BRANCH_MERGE_ERROR_MESSAGE)
    if branch not in rd.branches():
        raise exceptions.SCCSException(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch)
        )


def copy_branch_data(

    c: SCCSConstants, branch: str, rd: RepositoryData, rp: RepositoryPaths
) -> None:

    source = rp.branch_path(branch)
    destination = rp.branch_path(rd.current_branch())

    def ignore_metadata(_directory: str, names: list[str]) -> set[Any]:

        ignored = set()
        for i in names:
            if i in (c.HISTORY_DIRECTORY, c.COMMIT_BYTE_HASH_DIRECTORY):
                ignored.add(i)
        return ignored

    try:
        if source.exists():
            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
                ignore=ignore_metadata,
            )
    except Exception as e:
        raise exceptions.SCCSException(c.MERGE_COPY_ERROR_MESSAGE) from e


def copy_repository_document(

    branch: str, rd: RepositoryData, rp: RepositoryPaths
) -> None:

    original_target = rd.target.get()
    rd.target.set(branch)

    try:
        shutil.copy2(
            rd.commit_identifier_to_full_path(
                rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
            ),
            rp.document_path(),
        )
    except Exception as e:
        raise exceptions.SCCSException(c.MERGE_DOCUMENT_COPY_ERROR_MESSAGE) from e
    finally:
        rd.target.set(original_target)


def print_merge_success_message(

    c: SCCSConstants, branch: str, rd: RepositoryData
) -> None:
    print(
        c.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(
            branch_name=branch, current_branch=rd.current_branch()
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

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_branch(c, branch, rd)

    copy_repository_document(branch, rd, rp)

    copy_branch_data(c, branch, rd, rp)

    rw.commit_changes(
        c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(
            branch_name=branch, current_branch=rd.current_branch()
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
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
