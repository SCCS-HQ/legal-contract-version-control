#!/usr/bin/env python3
"""Create, Delete, and List Branches"""

import shutil
from pathlib import Path

import exceptions
import utils
from repository_layout import (
    RepositoryPaths,
    RepositoryData,
    RepositoryWrite,
    RepositoryStatus,
    TargetBranch,
)
from constants_classes import SCCSConstants


def validate_subcommand(
    c: SCCSConstants, subcommand: str | None, branch_name: str | None, rs: RepositoryStatus
) -> None:
    """
    Raise an exception if the subcommand is invalid or if required arguments are
    missing.
    """

    if not subcommand:
        raise exceptions.InvalidSubcommandError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.SUBCOMMAND_FIELD_NAME)
        )

    if subcommand not in c.ACCEPTED_SUBCOMMANDS:
        raise exceptions.InvalidSubcommandError(
            c.INVALID_SUBCOMMAND_ERROR_MESSAGE
        )

    if subcommand in [c.CREATE_SUBCOMMAND, c.DELETE_SUBCOMMAND]:
        if not branch_name:
            raise exceptions.InvalidArgumentError(
                c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                    field=c.BRANCH_NAME_FIELD_NAME
                )
            )

    if subcommand == c.CREATE_SUBCOMMAND:
        if rs.branch_exists(branch_name):
            raise exceptions.BranchAlreadyExistsError(
                c.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE.format(
                    branch_name=branch_name
                )
            )

    if subcommand == c.DELETE_SUBCOMMAND:
        if rs.is_current_branch(branch_name):
            raise exceptions.BranchDeletionError(
                c.CURRENT_BRANCH_DELETION_ERROR_MESSAGE
            )

        if not rs.branch_exists(branch_name):
            raise exceptions.BranchMissingFromMetadataError(
                c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                    branch_name=branch_name
                )
            )


def branch_create_subcommand(
    c: SCCSConstants,
    branch_name: str,
    current_branch_name: str,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:
    """
    Create a new branch from the current branch. The new branch will have the same
    commit history and metadata as the current branch.
    """

    try:
        shutil.copytree(
            rp.branch_path(current_branch_name),
            rp.branch_path(branch_name),
        )
        rw.add_to_branches_list(branch_name)
        rw.set_current_branch(branch_name)
    except Exception as e:
        rollback_changes_after_failure(c, branch_name, c.CREATE_SUBCOMMAND, rp, rw)
        raise exceptions.FileCopyError(
            c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(
                action=c.CREATE_SUBCOMMAND
            )
        ) from e

    print_branch_create_success_message(c, branch_name, current_branch_name)


def branch_delete_subcommand(
    c: SCCSConstants, branch_name: str, rp: RepositoryPaths, rw: RepositoryWrite
) -> None:
    """
    Delete an existing branch.
    """

    try:
        rw.remove_from_branches_list(branch_name)
        shutil.rmtree(rp.branch_path(branch_name))
    except Exception as e:
        rollback_changes_after_failure(c, branch_name, c.DELETE_SUBCOMMAND, rp, rw)
        raise exceptions.FileDeleteError(
            c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(
                action=c.DELETE_SUBCOMMAND
            )
        ) from e

    print_branch_delete_success_message(c, branch_name)


def rollback_changes_after_failure(
    c: SCCSConstants,
    branch_name: str,
    subcommand: str,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:
    """
    Rollback changes after a failed branch deletion.
    If an error occurs during branch deletion, the branch metadata will be rolled back
    to include the deleted branch again.
    """

    try:
        if subcommand == c.CREATE_SUBCOMMAND:
            rw.remove_from_branches_list(branch_name)
            rw.set_current_branch(c.MAIN_BRANCH_NAME)
            shutil.rmtree(rp.branch_path(branch_name))
        if subcommand == c.DELETE_SUBCOMMAND:
            rw.add_to_branches_list(branch_name)
    except Exception as e:
        raise exceptions.UpdatingMetadataError(
            c.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch_name
            )
        ) from e


def branch_list_subcommand(c: SCCSConstants, rd: RepositoryData) -> None:
    """
    Print a list of all branches, indicating the current branch found in the repository
    metadata.
    """

    print(c.BRANCHES_DIR_LIST_HEADER)
    for i in rd.branches():
        if i == rd.current_branch():
            print(c.CURRENT_BRANCH_MESSAGE_TEMPLATE.format(branch_name=i))
        else:
            print(c.OTHER_BRANCH_LIST_TEMPLATE.format(branch_name=i))


def run_specified_subcommand(
    c: SCCSConstants,
    subcommand: str | None,
    branch_name: str | None,
    current_branch_name: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:
    """
    Run the specified subcommand by reading the subcommand entered:

    create: branch_create_subcommand

    delete: branch_delete_subcommand

    list: branch_list_subcommand
    """

    if subcommand == c.CREATE_SUBCOMMAND:
        assert branch_name is not None
        branch_create_subcommand(c, branch_name, current_branch_name, rp, rw)
    elif subcommand == c.DELETE_SUBCOMMAND:
        assert branch_name is not None
        branch_delete_subcommand(c, branch_name, rp, rw)
    elif subcommand == c.LIST_SUBCOMMAND:
        branch_list_subcommand(c, rd)


def print_branch_delete_success_message(c: SCCSConstants, branch_name: str) -> None:
    print(c.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_name))


def print_branch_create_success_message(
    c: SCCSConstants, branch_name: str, current_branch_name: str
) -> None:
    print(
        c.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE.format(
            branch_name=branch_name, current_branch_name=current_branch_name
        )
    )


def main(
        c: SCCSConstants,
        subcommand: str | None,
        branch_name: str | None,
        rd: RepositoryData,
        rs: RepositoryStatus,
        rp: RepositoryPaths,
        rw: RepositoryWrite
    ) -> None:

    """Run functions for the <sccs branch> command."""
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

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
        utils.entered_argument(2),
        utils.entered_argument(3),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
