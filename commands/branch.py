#!/usr/bin/env python3
"""Create, Delete, and List Branches"""

import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

CREATE_SUBCOMMAND = "create"
DELETE_SUBCOMMAND = "delete"
LIST_SUBCOMMAND = "list"

def validate_subcommand(Repo: RepositoryLayout, subcommand: str | None = None, branch_name: str | None = None) -> None:
    """
    Validate the subcommand entered by the user.

    Raise an exception if the subcommand is invalid or if required arguments are
    missing.
    """

    if subcommand is None:
        subcommand = utils.entered_arguement(2)
    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_arguement(3))

    if not subcommand:
        raise exceptions.InvalidSubcommandError(
            "No subcommand provided. Please use 'create', 'delete', or 'list' along "
            "with required arguments."
        )

    if subcommand not in [CREATE_SUBCOMMAND, DELETE_SUBCOMMAND, LIST_SUBCOMMAND]:
        raise exceptions.InvalidSubcommandError(
            f"Invalid subcommand: {subcommand}. Please use 'create', 'delete', or "
            f"'list' along with required arguments."
        )

    if subcommand in [CREATE_SUBCOMMAND, DELETE_SUBCOMMAND]:
        if not branch_name:
            raise exceptions.InvalidArgumentError(
                "No branch name provided. Please specify a branch name."
            )
        
    if subcommand == CREATE_SUBCOMMAND:
        if Repo.branch_exists(branch_name):
            raise exceptions.BranchAlreadyExistsError(
                f"Branch '{branch_name}' already exists."
            )
        
    if subcommand == DELETE_SUBCOMMAND:
        if Repo.is_current_branch(branch_name):
            raise exceptions.BranchDeletionError(
                "Cannot delete the current branch. Please switch to another branch first."
            )

        if not Repo.branch_exists(branch_name):
            raise exceptions.BranchMissingFromMetadataError(
                f"Branch '{branch_name}' does not exist in branch data."
            )


def branch_create_subcommand(Repo: RepositoryLayout, branch_name: str | None = None, current_branch_name: str | None = None) -> None:
    """
    Create a new branch from the current branch. The new branch will have the same
    commit history and metadata as the current branch.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_arguement(3))
    if current_branch_name is None:
        current_branch_name = Repo.current_branch_name()

    new_branch_path = Repo.branch_path(branch_name)

    try:
        shutil.copytree(
            Repo.branch_path(current_branch_name),
            new_branch_path,
        )
    except Exception as e:
        delete_branch_after_error(Repo, branch_name)
        raise exceptions.FileCopyError from e

    Repo.add_to_branches_list(branch_name)

    print_msg = (
        f"Branch '{branch_name}' was created from branch '{current_branch_name}', "
        f"and is now the current branch.\n"
    )

    Repo.set_current_branch(branch_name)

    print(print_msg)
    

def delete_branch_after_error(Repo: RepositoryLayout, branch_name: str | None = None) -> None:
    """
    Delete a branch after an error has occurred during branch creation by deleting the
    branch directory.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_arguement(3))

    branch_path = Repo.branch_path(branch_name)
    
    if branch_path.is_dir():
        try:
            shutil.rmtree(branch_path)
        except Exception as e:
            raise exceptions.FileCopyError from e


def branch_delete_subcommand(Repo: RepositoryLayout, branch_name: str | None = None) -> None:
    """
    Delete an existing branch.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_arguement(3))
    branch_path = Repo.branch_path(branch_name)

    Repo.remove_from_branches_list(branch_name)

    try:
        shutil.rmtree(branch_path)
    except Exception as e:
        rollback_changes_after_failure(Repo, branch_name)       
        raise exceptions.FileCopyError from e

    print(f"Branch '{branch_name}' was deleted.\n")


def rollback_changes_after_failure(Repo: RepositoryLayout, branch_name: str | None = None) -> None:
    """
    Rollback changes after a failed branch deletion.
    If an error occurs during branch deletion, the branch metadata will be rolled back
    to include the deleted branch again.
    """

    if branch_name is None:
        branch_name = utils.clean_directory_name(utils.entered_arguement(3))

    try:
        Repo.add_to_branches_list(branch_name)
    except Exception as e:
        raise exceptions.UpdatingMetadataError(
            f"Failed to rollback branch metadata after deletion failure"
        ) from e
    

def branch_list_subcommand(Repo: RepositoryLayout) -> None:
    """
    Print a list of all branches, indicating the current branch found in the repository
    metadata.
    """

    print("Branches:\n")
    for i in Repo.list_branches():
        if i == Repo.current_branch_name():
            print(f"* {i} (current)")
        else:
            print(f"  {i}")


def run_specified_subcommand(Repo: RepositoryLayout, subcommand: str | None = None) -> None:
    """
    Run the specified subcommand by reading the subcommand entered:

    create: branch_create_subcommand

    delete: branch_delete_subcommand

    list: branch_list_subcommand
    """

    if subcommand is None:
        subcommand = utils.entered_arguement(2)

    if subcommand == CREATE_SUBCOMMAND:
        branch_create_subcommand(Repo)
    elif subcommand == DELETE_SUBCOMMAND:
        branch_delete_subcommand(Repo)
    elif subcommand == LIST_SUBCOMMAND:
        branch_list_subcommand(Repo)


def main(Repo: RepositoryLayout) -> None:
    """Run functions for the <sccs branch> command."""
    Repo.check_repository_layout()

    validate_subcommand(Repo)

    Repo.check_for_uncommitted_changes("branch")

    run_specified_subcommand(Repo)


if __name__ == "__main__":
    try:
        Repository = RepositoryLayout(Path.cwd())
        main(Repository)

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
