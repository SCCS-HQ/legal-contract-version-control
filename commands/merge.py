#!/usr/bin/env python3

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
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
    c: SCCSConstants, branch: str, rd: RepositoryData, ri: RepositoryIO
) -> None:

    ri.target.set(branch)
    branch_to_merge_data = ri.read_branch_data()

    ri.target.set(rd.current_branch())
    ri.write_branch_data(branch_to_merge_data)


def copy_repository_document(
    c: SCCSConstants, branch: str, rd: RepositoryData, rp: RepositoryPaths
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
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_branch(c, branch, rd)

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        staging_ri = RepositoryIO(staging_root, c, ri.target)
        staging_rp = RepositoryPaths(staging_root, c, rp.target)
        staging_rw = RepositoryWrite(staging_root, c, rw.target)

        copy_repository_document(c, branch, rd, staging_rp)

        copy_branch_data(c, branch, rd, staging_ri)

        staging_rw.commit_changes(
            c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(
                branch_name=branch, current_branch=rd.current_branch()
            ),
            allow_empty_commit=True,
        )

        utils.promote_staging(staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_merge_success_message(c, branch, rd)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryIO(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
