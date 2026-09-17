#!/usr/bin/env python3

from pathlib import Path

import src.commands.exceptions as exceptions
import src.commands.utils as utils
from src.commands.constants_classes import SCCSConstants
from src.commands.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def branch_create_subcommand(
    c: SCCSConstants,
    branch_name: str,
    rd: RepositoryData,
    rw: RepositoryWrite,
) -> None:
    """
    Set the target branch to the new branch name and add the current branch metadata to
    the new branch.

    Print a success message indicating that the new branch has been created from the
    current branch.
    """

    rw.target.set(branch_name)

    current_branch_name = rd.current_branch()

    rw.add_branch_metadata(branch_name, current_branch_name)

    print_branch_create_success_message(c, branch_name, current_branch_name)


def branch_delete_subcommand(
    c: SCCSConstants, branch_name: str, rd: RepositoryData, rw: RepositoryWrite
) -> None:
    """
    Delete the specified branch by removing its metadata from the repository.

    If the branch to be deleted is the main branch, raise an SCCSException indicating
    that the main branch cannot be deleted.

    Print a success message indicating that the branch has been deleted.
    """

    if branch_name.lower() == c.MAIN_BRANCH_NAME:
        raise exceptions.SCCSException(c.DELETING_MAIN_ERROR_MESSAGE)

    rw.remove_branch_metadata(branch_name, rd.current_branch())
    print_branch_delete_success_message(c, branch_name)


def branch_list_subcommand(c: SCCSConstants, rd: RepositoryData) -> None:
    """
    List all branches in the repository, indicating the current branch with a special
    marker. Print the list of branches to the console.
    """

    print(c.BRANCHES_DIRECTORY_LIST_HEADER)
    for i in rd.branches():
        (
            print(c.CURRENT_BRANCH_MESSAGE_TEMPLATE.format(branch_name=i))
            if i == rd.current_branch()
            else print(c.OTHER_BRANCH_LIST_TEMPLATE.format(branch_name=i))
        )


def print_branch_create_success_message(
    c: SCCSConstants, branch_name: str, current_branch_name: str
) -> None:
    """
    Print a success message indicating that the new branch has been created from the
    current branch.
    """

    print(
        c.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE.format(
            branch_name=branch_name, current_branch_name=current_branch_name
        )
    )


def print_branch_delete_success_message(c: SCCSConstants, branch_name: str) -> None:
    """Print a success message indicating that the branch has been deleted."""

    print(c.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_name))


def run_specified_subcommand(
    c: SCCSConstants,
    subcommand: str | None,
    branch_name: str | None,
    rd: RepositoryData,
    rw: RepositoryWrite,
) -> None:
    """
    Delegate the execution of the specified subcommand to the appropriate function based
    on the subcommand provided. Raise an SCCSException if the subcommand is invalid.
    """

    if subcommand == c.CREATE_SUBCOMMAND:
        if branch_name is None:
            raise exceptions.SCCSException(c.INVALID_BRANCH_NAME_ERROR_MESSAGE)
        branch_create_subcommand(c, branch_name, rd, rw)
    elif subcommand == c.DELETE_SUBCOMMAND:
        if branch_name is None:
            raise exceptions.SCCSException(c.INVALID_BRANCH_NAME_ERROR_MESSAGE)
        branch_delete_subcommand(c, branch_name, rd, rw)
    elif subcommand == c.LIST_SUBCOMMAND:
        branch_list_subcommand(c, rd)


def validate_subcommand(
    c: SCCSConstants,
    subcommand: str | None,
    branch_name: str | None,
    rs: RepositoryStatus,
) -> None:
    """
    Validate the subcommand and ensure the proper arguments are provided for each
    subcommand. Raise an SCCSException if any validation fails.
    """

    utils.raise_if_empty(c, subcommand, c.SUBCOMMAND_FIELD_NAME)

    if subcommand not in c.ACCEPTED_SUBCOMMANDS:
        raise exceptions.SCCSException(c.INVALID_SUBCOMMAND_ERROR_MESSAGE)

    if subcommand in [c.CREATE_SUBCOMMAND, c.DELETE_SUBCOMMAND]:
        utils.raise_if_empty(c, branch_name, c.BRANCH_NAME_FIELD_NAME)

    if subcommand == c.CREATE_SUBCOMMAND and rs.branch_exists(branch_name):
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


def main(
    c: SCCSConstants,
    subcommand: str | None,
    branch_name: str | None,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the branch command by setting the current branch as the target, validating the
    repository layout, and delegating execution of the entered subcommand to a copy of
    the repository in a staging directory.

    Promote the staging directory to the repository root and reset the target branch
    when the operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_subcommand(c, subcommand, branch_name, rs)

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:

        staging_rd = RepositoryData(staging_root, rd.repository_name, c, rd.target)
        staging_rw = RepositoryWrite(staging_root, rd.repository_name, c, rw.target)

        run_specified_subcommand(
            c,
            subcommand,
            branch_name,
            staging_rd,
            staging_rw,
        )

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    wd = utils.working_directory(c)
    target = TargetBranch(c)
    repository_name = wd.name
    utils.run_command(
        main,
        utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
        utils.entered_argument(c, c.SECOND_ARGUMENT_INDEX, raise_on_not_provided=False),
        RepositoryData(wd, repository_name, c, target),
        RepositoryPaths(wd, repository_name, c, target),
        RepositoryStatus(wd, repository_name, c, target),
        RepositoryWrite(wd, repository_name, c, target),
    )
