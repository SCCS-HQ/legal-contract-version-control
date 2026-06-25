#!/usr/bin/env python3
"""Create, Delete, and List Branches"""

import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout
from constants_classes import SCCSConstants, ErrorWrappers


def validate_subcommand(constants: SCCSConstants, Repo: RepositoryLayout, subcommand: str | None = None, branch_name: str | None = None) -> None:
    """
    Validate the subcommand entered by the user.

    Raise an exception if the subcommand is invalid or if required arguments are
    missing.
    """

    if subcommand is None:
        subcommand = utils.entered_argument(2)
    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_argument(3))

    if not subcommand:
        raise exceptions.InvalidSubcommandError(
            constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field="subcommand")
        )

    if subcommand not in [constants.CREATE_SUBCOMMAND, constants.DELETE_SUBCOMMAND, constants.LIST_SUBCOMMAND]:
        raise exceptions.InvalidSubcommandError(
            constants.INVALID_SUBCOMMAND_ERROR_MESSAGE
        )

    if subcommand in [constants.CREATE_SUBCOMMAND, constants.DELETE_SUBCOMMAND]:
        if not branch_name:
            raise exceptions.InvalidArgumentError(
                constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field="branch name")
            )
        
    if subcommand == constants.CREATE_SUBCOMMAND:
        if Repo.branch_exists(branch_name):
            raise exceptions.BranchAlreadyExistsError(
                constants.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)
            )
        
    if subcommand == constants.DELETE_SUBCOMMAND:
        if Repo.is_current_branch(branch_name):
            raise exceptions.BranchDeletionError(
                constants.CURRENT_BRANCH_DIR_DELETION_ERROR_MESSAGE
            )

        if not Repo.branch_exists(branch_name):
            raise exceptions.BranchMissingFromMetadataError(
                constants.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)
            )


def branch_create_subcommand(constants: SCCSConstants, Repo: RepositoryLayout, branch_name: str | None = None, current_branch_name: str | None = None) -> None:
    """
    Create a new branch from the current branch. The new branch will have the same
    commit history and metadata as the current branch.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_argument(3))
    if current_branch_name is None:
        current_branch_name = Repo.current_branch_name()

    try:
        shutil.copytree(
            Repo.branch_path(current_branch_name),
            Repo.branch_path(branch_name),
        )
    except Exception as e:
        delete_branch_after_error(Repo, branch_name)
        raise exceptions.FileCopyError from e

    Repo.add_to_branches_list(branch_name)

    print_msg = constants.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE.format(
        branch_name=branch_name,
        current_branch_name=current_branch_name
    )

    Repo.set_current_branch(branch_name)

    print(print_msg)
    

def delete_branch_after_error(Repo: RepositoryLayout, branch_name: str | None = None) -> None:
    """
    Delete a branch after an error has occurred during branch creation by deleting the
    branch directory.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_argument(3))

    branch_path = Repo.branch_path(branch_name)
    
    if branch_path.is_dir():
        try:
            shutil.rmtree(branch_path)
        except Exception as e:
            raise exceptions.UpdatingMetadataError(constants.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)) from e


def branch_delete_subcommand(constants: SCCSConstants, Repo: RepositoryLayout, branch_name: str | None = None) -> None:
    """
    Delete an existing branch.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_argument(3))
    branch_path = Repo.branch_path(branch_name)

    Repo.remove_from_branches_list(branch_name)

    try:
        shutil.rmtree(branch_path)
    except Exception as e:
        rollback_changes_after_failure(constants, Repo, branch_name)       
        raise exceptions.UpdatingMetadataError from e

    print(constants.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_name))


def rollback_changes_after_failure(constants: SCCSConstants, Repo: RepositoryLayout, branch_name: str | None = None) -> None:
    """
    Rollback changes after a failed branch deletion.
    If an error occurs during branch deletion, the branch metadata will be rolled back
    to include the deleted branch again.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_argument(3))

    try:
        Repo.add_to_branches_list(branch_name)
    except Exception as e:
        raise exceptions.UpdatingMetadataError(
            constants.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)
        ) from e
    

def branch_list_subcommand(constants: SCCSConstants, Repo: RepositoryLayout) -> None:
    """
    Print a list of all branches, indicating the current branch found in the repository
    metadata.
    """

    print(constants.BRANCHES_DIR_LIST_HEADER)
    for i in Repo.list_branches():
        if i == Repo.current_branch_name():
            print(constants.CURRENT_BRANCH_MESSAGE_TEMPLATE.format(branch_name=i))
        else:
            print(constants.OTHER_BRANCH_LIST_TEMPLATE.format(branch_name=i))


def run_specified_subcommand(constants: SCCSConstants, Repo: RepositoryLayout, subcommand: str | None = None) -> None:
    """
    Run the specified subcommand by reading the subcommand entered:

    create: branch_create_subcommand

    delete: branch_delete_subcommand

    list: branch_list_subcommand
    """

    if subcommand is None:
        subcommand = utils.entered_argument(2)

    if subcommand == constants.CREATE_SUBCOMMAND:
        branch_create_subcommand(constants, Repo)
    elif subcommand == constants.DELETE_SUBCOMMAND:
        branch_delete_subcommand(constants, Repo)
    elif subcommand == constants.LIST_SUBCOMMAND:
        branch_list_subcommand(constants, Repo)


def main(constants: SCCSConstants, Repo: RepositoryLayout) -> None:
    """Run functions for the <sccs branch> command."""
    Repo.check_repository_layout()

    validate_subcommand(constants, Repo)

    Repo.check_for_uncommitted_changes()

    run_specified_subcommand(constants, Repo)


if __name__ == "__main__":
    try:
        
        constants = SCCSConstants()
        Repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(constants, Repository)

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
