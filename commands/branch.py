#!/usr/bin/env python3

import shutil
from pathlib import Path

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
            raise exceptions.SCCSException(
                c.CURRENT_BRANCH_DELETION_ERROR_MESSAGE
            )

        if not rs.branch_exists(branch_name):
            raise exceptions.SCCSException(
                c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                    branch_name=branch_name
                )
            )


def rollback_changes_after_failure(
    c: SCCSConstants,
    branch_name: str,
    subcommand: str,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:

    try:
        if subcommand == c.CREATE_SUBCOMMAND:
            rw.remove_from_branches_list(branch_name)
            rw.set_current_branch(c.MAIN_BRANCH_NAME)
            shutil.rmtree(rp.branch_path(branch_name))
        if subcommand == c.DELETE_SUBCOMMAND:
            rw.add_to_branches_list(branch_name)
    except Exception as e:
        raise exceptions.SCCSException(
            c.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch_name
            )
        ) from e


def branch_create_subcommand(
    c: SCCSConstants,
    branch_name: str,
    current_branch_name: str,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:

    try:
        shutil.copytree(
            rp.branch_path(current_branch_name),
            rp.branch_path(branch_name),
        )
        rw.add_to_branches_list(branch_name)
        rw.set_current_branch(branch_name)
    except Exception as e:
        rollback_changes_after_failure(c, branch_name, c.CREATE_SUBCOMMAND, rp, rw)
        raise exceptions.SCCSException(
            c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(
                action=c.CREATE_SUBCOMMAND
            )
        ) from e

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
    c: SCCSConstants, branch_name: str, rp: RepositoryPaths, rw: RepositoryWrite
) -> None:

    try:
        rw.remove_from_branches_list(branch_name)
        shutil.rmtree(rp.branch_path(branch_name))
    except Exception as e:
        rollback_changes_after_failure(c, branch_name, c.DELETE_SUBCOMMAND, rp, rw)
        raise exceptions.SCCSException(
            c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(
                action=c.DELETE_SUBCOMMAND
            )
        ) from e

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
            raise exceptions.SCCSException(c.BRANCH_RUN_ERROR_MESSAGE)
        branch_create_subcommand(c, branch_name, current_branch_name, rp, rw)
    elif subcommand == c.DELETE_SUBCOMMAND:
        if branch_name is None:
            raise exceptions.SCCSException(c.BRANCH_RUN_ERROR_MESSAGE)
        branch_delete_subcommand(c, branch_name, rp, rw)
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

    run_specified_subcommand(
        c, subcommand, branch_name, rd.current_branch(), rd, rp, rw
    )

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
