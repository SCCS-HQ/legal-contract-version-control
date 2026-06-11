#!/usr/bin/env python3
"""Create, Delete, and List Branches"""

import json
import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())

def validate_subcommand() -> None:
    """
    Validate the subcommand entered by the user.

    Raise an exception if the subcommand is invalid or if required arguments are
    missing.
    """

    subcommand = utils.entered_arguement(2)
    branch_name = utils.entered_arguement(3)

    if not subcommand:
        raise exceptions.InvalidSubcommandError(
            "No subcommand provided. Please use 'create', 'delete', or 'list' along "
            "with required arguments."
        )

    if subcommand not in ["create", "delete", "list"]:
        raise exceptions.InvalidSubcommandError(
            f"Invalid subcommand: {subcommand}. Please use 'create', 'delete', or "
            f"'list' along with required arguments."
        )

    if subcommand in ["create", "delete"]:
        if not branch_name:
            raise exceptions.InvalidArgumentError(
                "No branch name provided. Please specify a branch name."
            )


def branch_create_subcommand(
    cwd: Path | None = None,
    current_branch_path: Path | None = None,
) -> None:
    """
    Create a new branch from the current branch. The new branch will have the same
    commit history and metadata as the current branch.
    """

    current_branch = Repository.current_branch_name()
    branch_data = Repository.current_branch_data()


    if cwd is None:
        cwd = Path.cwd()

    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    sanitized_branch_name = utils.clean_directory_name(utils.entered_arguement(3))

    if not sanitized_branch_name:
        raise exceptions.InvalidArgumentError(
            "Invalid branch name. Please provide a valid branch name."
        )

    if sanitized_branch_name in branch_data["branches"]:
        raise exceptions.BranchAlreadyExistsError(
            f"Branch '{sanitized_branch_name}' already exists."
        )

    if (cwd / ".sccs" / "branches" / sanitized_branch_name).is_dir():
        raise exceptions.BranchAlreadyExistsError(
            f"Branch '{sanitized_branch_name}' already exists."
        )

    try:
        shutil.copytree(
            cwd / ".sccs" / "branches" / current_branch,
            cwd / ".sccs" / "branches" / sanitized_branch_name,
        )
    except Exception as e:
        delete_branch_after_error()
        raise exceptions.FileCopyError from e

    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as f:
            branch_data["branches"].append(sanitized_branch_name)
            branch_data["current_branch"] = sanitized_branch_name
            json.dump(branch_data, f, indent=4)

    # Clean up the created directory before raising
    except Exception as e:
        delete_branch_after_error()
        raise exceptions.BranchCreationError from e

    print(
        f"Branch '{sanitized_branch_name}' was created from branch '{current_branch}', "
        f"and is now the current branch.\n"
    )


def delete_branch_after_error(cwd: Path | None = None) -> None:
    """
    Delete a branch after an error has occurred during branch creation by deleting the
    branch directory.
    """

    if cwd is None:
        cwd = Path.cwd()

    branch_path = cwd / ".sccs" / "branches" / utils.clean_directory_name(utils.entered_arguement(3))
    if branch_path.is_dir():
        shutil.rmtree(branch_path)


def branch_delete_subcommand(
    cwd: Path | None = None,
    current_branch_path: Path | None = None,
) -> None:
    """
    Delete an existing branch using the branch name provided by the user. The branch
    directory will be deleted, and the branch will be removed from the branch metadata.
    If the deleted branch is the current branch, an exception will be raised and the
    branch will not be deleted. If an error occurs during deletion, any changes made
    to the branch metadata will be rolled back.
    """

    current_branch = Repository.current_branch_name()
    branch_data = Repository.current_branch_data()


    if cwd is None:
        cwd = Path.cwd()
    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    sanitized_branch_name = utils.clean_directory_name(utils.entered_arguement(3))

    branch_path = cwd / ".sccs" / "branches" / sanitized_branch_name

    if sanitized_branch_name == current_branch:
        raise exceptions.BranchDeletionError(
            "Cannot delete the current branch. Please switch to another branch first."
        )

    if not branch_path.exists():
        raise exceptions.BranchNotFoundError(
            f"Branch '{sanitized_branch_name}' does not exist."
        )

    if not sanitized_branch_name in branch_data["branches"]:
        raise exceptions.BranchMissingFromMetadataError(
            f"Branch '{sanitized_branch_name}' does not exist in branch data."
        )

    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as f:
            branch_data["branches"].remove(sanitized_branch_name)
            json.dump(branch_data, f, indent=4)

    except Exception as e:
        raise exceptions.UpdatingMetadataError from e

    try:
        shutil.rmtree(branch_path)

    except Exception as e:
        rollback_changes_after_failure(current_branch_path, branch_data=branch_data)
        raise exceptions.BranchDeletionError from e

    print(f"Branch '{sanitized_branch_name}' was deleted.\n")


def rollback_changes_after_failure(
    current_branch_path: Path | None = None, branch_data: dict | None = None
) -> None:
    """
    Rollback changes after a failed branch deletion.
    If an error occurs during branch deletion, the branch metadata will be rolled back
    to include the deleted branch again."""

    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    if branch_data is None:
        branch_data = Repository.current_branch_data()

    sanitized_branch_name = utils.clean_directory_name(utils.entered_arguement(3))
    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as f:
            branch_data["branches"].append(sanitized_branch_name)
            json.dump(branch_data, f, indent=4)

    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def branch_list_subcommand() -> None:
    """
    Print a list of all branches, indicating the current branch found in the repository
    metadata.
    """
    current_branch = Repository.current_branch_name()
    branch_data = Repository.current_branch_data()

    print("Branches:\n")
    for i in branch_data.get("branches", []):
        if i == current_branch:
            print(f"* {i} (current)")
        else:
            print(f"  {i}")


def run_specified_subcommand() -> None:
    """
    Run the specified subcommand by reading the subcommand entered:

    create: branch_create_subcommand

    delete: branch_delete_subcommand

    list: branch_list_subcommand
    """

    subcommand = utils.entered_arguement(2)

    if subcommand == "create":
        branch_create_subcommand()
    elif subcommand == "delete":
        branch_delete_subcommand()
    elif subcommand == "list":
        branch_list_subcommand()


def main() -> None:
    """Run functions for the <sccs branch> command."""
    Repository.check_repository_layout()

    validate_subcommand()

    Repository.check_for_uncommitted_changes("branch")

    run_specified_subcommand()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
