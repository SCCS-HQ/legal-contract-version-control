"""Create, Delete, and List Branches"""

import json
import shutil
import sys
from pathlib import Path

import exceptions
import utils


def get_entered_subcommand() -> str | None:
    """Retrieve the subcommand entered by the user."""

    return sys.argv[2] if len(sys.argv) > 2 else None


def get_entered_branch_name() -> str | None:
    """Retrieve the branch name entered by the user."""

    return sys.argv[3] if len(sys.argv) > 3 else None


def validate_subcommand(subcommand: str | None, branch_name: str | None) -> None:
    """Validate the subcommand entered by the user."""

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
    current_branch: str,
    branch_data: dict,
    cwd: Path | None = None,
    current_branch_path: Path | None = None,
) -> None:
    """Create a new branch from the current branch."""

    if cwd is None:
        cwd = utils.working_directory_path

    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    sanitized_branch_name = utils.clean_directory_name(get_entered_branch_name())

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
        delete_branch_after_error(sanitized_branch_name, cwd=cwd)
        raise exceptions.FileCopyError from e

    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as current_branch_file:
            branch_data["branches"].append(sanitized_branch_name)
            branch_data["current_branch"] = sanitized_branch_name
            json.dump(branch_data, current_branch_file, indent=4)

    # Clean up the created directory before raising
    except Exception as e:
        delete_branch_after_error(sanitized_branch_name, cwd=cwd)
        raise exceptions.BranchCreationError from e

    print(
        f"Branch '{sanitized_branch_name}' was created from branch '{current_branch}', "
        f"and is now the current branch."
    )


def delete_branch_after_error(branch_name: str, cwd: Path = None) -> None:
    """Delete a branch after an error has occurred during creation."""

    if cwd is None:
        cwd = utils.working_directory_path

    branch_path = cwd / ".sccs" / "branches" / branch_name
    if branch_path.is_dir():
        shutil.rmtree(branch_path)


def branch_delete_subcommand(
    current_branch: str,
    branch_data: dict,
    cwd: Path = None,
    current_branch_path: Path = None,
) -> None:
    """Delete an existing branch."""

    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    sanitized_branch_name = utils.clean_directory_name(get_entered_branch_name())

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
        ) as current_branch_file:
            branch_data["branches"].remove(sanitized_branch_name)
            json.dump(branch_data, current_branch_file, indent=4)

    except Exception as e:
        raise exceptions.UpdatingMetadataError from e

    try:
        shutil.rmtree(branch_path)

    except Exception as e:
        rollback_changes_after_failure(current_branch_path, branch_data=branch_data)
        raise exceptions.BranchDeletionError from e

    print(f"Branch '{sanitized_branch_name}' was deleted.")


def rollback_changes_after_failure(
    current_branch_path: Path = None, branch_data: dict = None
) -> None:
    """Rollback changes after a failed branch deletion."""

    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    if branch_data is None:
        branch_data = utils.get_branch_data()

    sanitized_branch_name = utils.clean_directory_name(get_entered_branch_name())
    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as current_branch_file:
            branch_data["branches"].append(sanitized_branch_name)
            json.dump(branch_data, current_branch_file, indent=4)

    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def branch_list_subcommand(current_branch: str, branch_data: dict) -> None:
    """List all branches."""

    print("Branches:")
    for branch in branch_data.get("branches", []):
        if branch == current_branch:
            print(f"* {branch} (current)")
        else:
            print(f"  {branch}")


def run_specified_subcommand(
    subcommand: str, current_branch: str, branch_data: dict
) -> None:
    """Run the specified subcommand."""

    if subcommand == "create":
        branch_create_subcommand(current_branch, branch_data)
    elif subcommand == "delete":
        branch_delete_subcommand(current_branch, branch_data)
    elif subcommand == "list":
        branch_list_subcommand(current_branch, branch_data)


def main() -> None:
    """Run functions for the <sccs branch> command."""
    utils.check_sccs_layout()

    validate_subcommand(get_entered_subcommand(), get_entered_branch_name())

    run_specified_subcommand(
        get_entered_subcommand(),
        utils.get_current_branch(),
        utils.get_branch_data(),
    )


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
else:
    raise exceptions.FileImportedAsModuleError(
        "This file cannot be run as a module. Please run it as a script."
    )
