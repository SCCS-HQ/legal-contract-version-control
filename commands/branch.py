#!/usr/bin/env python3

from pathlib import Path
import shutil

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
)


def validate_subcommand(
    c: SCCSConstants,
    subcommand: str | None,
    branch_name: str | None,
    rs: RepositoryStatus,
) -> None:

    if not subcommand:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.SUBCOMMAND_FIELD_NAME)
        )

    if subcommand not in c.ACCEPTED_SUBCOMMANDS:
        raise exceptions.SCCSException(c.INVALID_SUBCOMMAND_ERROR_MESSAGE)

    if subcommand in [c.CREATE_SUBCOMMAND, c.DELETE_SUBCOMMAND]:
        if not branch_name:
            raise exceptions.SCCSException(
                c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                    field=c.BRANCH_NAME_FIELD_NAME
                )
            )

    if subcommand == c.CREATE_SUBCOMMAND:
        if rs.branch_exists(branch_name):
            raise exceptions.SCCSException(
                c.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE.format(
                    branch_name=branch_name
                )
            )

    if subcommand == c.DELETE_SUBCOMMAND:
        if rs.is_current_branch(branch_name):
            raise exceptions.SCCSException(c.CURRENT_BRANCH_DELETION_ERROR_MESSAGE)

        if not rs.branch_exists(branch_name):
            raise exceptions.SCCSException(
                c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                    branch_name=branch_name
                )
            )


def branch_create_subcommand(
    c: SCCSConstants,
    branch_name: str,
    current_branch_name: str,
    rw: RepositoryWrite,
) -> None:

    rw.target.set(branch_name)
    rw.add_branch_metadata(branch_name, current_branch_name)

    print_branch_create_success_message(c, branch_name, current_branch_name)


def print_branch_create_success_message(
    c: SCCSConstants, branch_name: str, current_branch_name: str
) -> None:

    print(
        c.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE.format(
            branch_name=branch_name, current_branch_name=current_branch_name
        )
    )


def branch_delete_subcommand(
    c: SCCSConstants, branch_name: str, rd: RepositoryData, rw: RepositoryWrite
) -> None:

    if branch_name == c.MAIN_BRANCH_NAME:
        raise exceptions.SCCSException(c.DELETING_MAIN_ERROR_MESSAGE)

    rw.remove_branch_metadata(branch_name, rd.current_branch())
    print_branch_delete_success_message(c, branch_name)


def print_branch_delete_success_message(c: SCCSConstants, branch_name: str) -> None:

    print(c.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_name))


def branch_list_subcommand(c: SCCSConstants, rd: RepositoryData) -> None:

    print(c.BRANCHES_DIRECTORY_LIST_HEADER)
    for i in rd.branches():
        (
            print(c.CURRENT_BRANCH_MESSAGE_TEMPLATE.format(branch_name=i))
            if i == rd.current_branch()
            else print(c.OTHER_BRANCH_LIST_TEMPLATE.format(branch_name=i))
        )


def run_specified_subcommand(
    c: SCCSConstants,
    subcommand: str | None,
    branch_name: str | None,
    current_branch_name: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:

    if subcommand == c.CREATE_SUBCOMMAND:
        if branch_name is None:
            raise exceptions.SCCSException(c.INVALID_BRANCH_NAME_ERROR_MESSAGE)
        branch_create_subcommand(c, branch_name, current_branch_name, rw)
    elif subcommand == c.DELETE_SUBCOMMAND:
        if branch_name is None:
            raise exceptions.SCCSException(c.INVALID_BRANCH_NAME_ERROR_MESSAGE)
        branch_delete_subcommand(c, branch_name, rd, rw)
    elif subcommand == c.LIST_SUBCOMMAND:
        branch_list_subcommand(c, rd)


def main(
    c: SCCSConstants,
    subcommand: str | None,
    branch_name: str | None,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_subcommand(c, subcommand, branch_name, rs)

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        shutil.copytree(rd.root, staging_root, dirs_exist_ok=True)

        staging_rd = RepositoryData(staging_root, c, rd.target)
        staging_rp = RepositoryPaths(staging_root, c, rp.target)
        staging_rw = RepositoryWrite(staging_root, c, rw.target)

        run_specified_subcommand(
            c, subcommand, branch_name, staging_rd.current_branch(), staging_rd, staging_rp, staging_rw
        )
        utils.promote_staging(c, staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        utils.entered_argument(c, 3, raise_on_not_provided=False),
        RepositoryData(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
