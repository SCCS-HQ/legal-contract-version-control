#!/usr/bin/env python3
"""Create, Delete, and List Branches"""

import shutil

import exceptions
import utils
from repository_layout import RepositoryLayout
from constants_classes import SCCSConstants


def validate_subcommand(c: SCCSConstants, repo: RepositoryLayout, subcommand: str, branch_name: str) -> None:
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
                c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
            )
        
    if subcommand == c.CREATE_SUBCOMMAND:
        if repo.branch_exists(branch_name):
            raise exceptions.BranchAlreadyExistsError(
                c.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)
            )
        
    if subcommand == c.DELETE_SUBCOMMAND:
        if repo.is_current_branch(branch_name):
            raise exceptions.BranchDeletionError(
                c.CURRENT_BRANCH_DELETION_ERROR_MESSAGE
            )

        if not repo.branch_exists(branch_name):
            raise exceptions.BranchMissingFromMetadataError(
                c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)
            )


def branch_create_subcommand(c: SCCSConstants, repo: RepositoryLayout, branch_name: str, current_branch_name: str) -> None:
    """
    Create a new branch from the current branch. The new branch will have the same
    commit history and metadata as the current branch.
    """

    try:
        
        
        shutil.copytree(
            repo.branch_path(current_branch_name),
            repo.branch_path(branch_name),
        )
        repo.add_to_branches_list(branch_name)
        repo.set_current_branch(branch_name)
    except Exception as e:
        rollback_changes_after_failure(c, repo, branch_name, c.CREATE_SUBCOMMAND)
        raise exceptions.FileCopyError(c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(action=c.CREATE_SUBCOMMAND)) from e

    print_branch_create_success_message(c, branch_name, current_branch_name)


def branch_delete_subcommand(c: SCCSConstants, repo: RepositoryLayout, branch_name: str) -> None:
    """
    Delete an existing branch.
    """

    branch_path = repo.branch_path(branch_name)

    try:
        repo.remove_from_branches_list(branch_name)
        shutil.rmtree(branch_path)
    except Exception as e:
        rollback_changes_after_failure(c, repo, branch_name, c.DELETE_SUBCOMMAND)       
        raise exceptions.FileDeleteError(c.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE.format(action=c.DELETE_SUBCOMMAND)) from e

    print_branch_delete_success_message(c, branch_name)


def rollback_changes_after_failure(c: SCCSConstants, repo: RepositoryLayout, branch_name: str, subcommand: str) -> None:
    """
    Rollback changes after a failed branch deletion.
    If an error occurs during branch deletion, the branch metadata will be rolled back
    to include the deleted branch again.
    """

    branch_path = repo.branch_path(branch_name)

    try:
        if subcommand == c.CREATE_SUBCOMMAND:
            repo.remove_from_branches_list(branch_name)
            repo.set_current_branch(c.MAIN_BRANCH_NAME)
            shutil.rmtree(branch_path)
        if subcommand == c.DELETE_SUBCOMMAND:
            repo.add_to_branches_list(branch_name)
    except Exception as e:
        raise exceptions.UpdatingMetadataError(
            c.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_name)
        ) from e
    

def branch_list_subcommand(c: SCCSConstants, repo: RepositoryLayout) -> None:
    """
    Print a list of all branches, indicating the current branch found in the repository
    metadata.
    """

    print(c.BRANCHES_DIR_LIST_HEADER)
    for i in repo.list_branches():
        if i == repo.current_branch_name():
            print(c.CURRENT_BRANCH_MESSAGE_TEMPLATE.format(branch_name=i))
        else:
            print(c.OTHER_BRANCH_LIST_TEMPLATE.format(branch_name=i))


def run_specified_subcommand(c: SCCSConstants, repo: RepositoryLayout, subcommand: str, branch_name: str, current_branch_name: str) -> None:
    """
    Run the specified subcommand by reading the subcommand entered:

    create: branch_create_subcommand

    delete: branch_delete_subcommand

    list: branch_list_subcommand
    """

    if subcommand == c.CREATE_SUBCOMMAND:
        branch_create_subcommand(c, repo, branch_name, current_branch_name)
    elif subcommand == c.DELETE_SUBCOMMAND:
        branch_delete_subcommand(c, repo, branch_name)
    elif subcommand == c.LIST_SUBCOMMAND:
        branch_list_subcommand(c, repo)


def print_branch_delete_success_message(c: SCCSConstants, branch_name):
    print(c.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_name))


def print_branch_create_success_message(c: SCCSConstants, branch_name: str, current_branch_name: str):
    print(
        c.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE.format(
            branch_name=branch_name, current_branch_name=current_branch_name
        )
    )


def main(
        c: SCCSConstants,
        repo: RepositoryLayout,
        subcommand: str,
        branch_name: str
    ) -> None:

    """Run functions for the <sccs branch> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()
    
    validate_subcommand(c, repo, subcommand, branch_name)

    run_specified_subcommand(c, repo, subcommand, branch_name, repo.current_branch_name())


if __name__ == "__main__":
    utils.run_command(main, 2, 3)
