#!/usr/bin/env python3

from pathlib import Path
import shutil

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


def check_branch_to_switch(
    c: SCCSConstants, branch_to_switch: str | None, rs: RepositoryStatus
) -> None:

    if not branch_to_switch:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )

    if not rs.branch_exists(branch_to_switch):
        raise exceptions.BranchNotFoundError(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch_to_switch
            )
        )


def check_commit(
    c: SCCSConstants, branch_to_switch: str | None, rd: RepositoryData, rs: RepositoryStatus
) -> None:

    rs.target.set(branch_to_switch)


    if not (
        rd.hash_to_full_path(rd.latest_commit(), c.DOCX_DIR)
    ).is_file():
        raise exceptions.CommitNotFoundError()

    rs.target.reset()


def copy_commit_to_main(
    c: SCCSConstants,
    branch_to_switch: str,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rp: RepositoryPaths,
) -> None:
    
    rs.target.set(branch_to_switch)

    try:
        shutil.copy2(
            rd.hash_to_full_path(rd.latest_commit(), c.DOCX_DIR),
            rp.document_path(),
        )
    except Exception as e:
        raise exceptions.FileCopyError() from e

    rs.target.reset()

def print_confirmation(c: SCCSConstants, branch_to_switch: str) -> None:

    print(c.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch))


def main(
    c: SCCSConstants,
    branch_to_switch: str | None,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    rs.raise_for_uncommitted_changes()

    check_branch_to_switch(c, branch_to_switch, rs)

    assert branch_to_switch is not None

    check_commit(c, branch_to_switch, rd, rs)

    copy_commit_to_main(c, branch_to_switch, rd, rs, rp)

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

