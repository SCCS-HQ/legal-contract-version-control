#!/usr/bin/env python3
"""Switch between document branches."""

import json
import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def check_branch_to_switch() -> None:
    """Check if the branch to switch to is valid."""

    branch_to_switch = utils.entered_arguement(2)

    if not branch_to_switch:
        raise exceptions.InvalidArgumentError(
            "No branch specified. Please provide a branch name to switch to."
        )

    if branch_to_switch not in Repository.list_branches():
        raise exceptions.BranchNotFoundError(
            f"Branch '{branch_to_switch}' does not exist."
        )


def sanitize_branch() -> str:
    """Sanitize the branch name."""

    return utils.clean_directory_name(utils.entered_arguement(2))


def check_commit() -> None:
    """
    Check if the commit object exists in the document history.
    """

    commit = Repository.branch(sanitize_branch(utils.entered_arguement(2))).latest_commit_path("docx")
    
    if not (commit).is_file():
        raise exceptions.CommitNotFoundError(f"Commit object '{commit}' not found.")


def copy_commit_to_main() -> None:
    """Copy the commit file to the main document."""
    try:
        shutil.copy2(
            (Repository.branch(sanitize_branch(utils.entered_arguement(2))).latest_commit_path("docx")),
            (Repository.document_path()),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_confirmation() -> None:
    """Print a confirmation message for successful branch switch."""

    print(f"Successfully switched to branch '{sanitize_branch(utils.entered_arguement(2))}'.\n")


def main() -> None:
    """Run functions for the <sccs switch> command."""
    Repository.check_repository_layout()

    Repository.check_for_uncommitted_changes("switch")

    check_branch_to_switch()

    check_commit()

    copy_commit_to_main()

    Repository.set_current_branch(sanitize_branch(utils.entered_arguement(2)))

    print_confirmation()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
