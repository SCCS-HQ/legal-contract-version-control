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


def update_current_branch(
    current_branch_path: Path | None = None, cwd: Path | None = None
) -> None:
    """
    Update the current branch in the SCCS metadata before switching branches.
    """
    if cwd is None:
        cwd = Path.cwd()
    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    branch = utils.entered_arguement(2)

    try:
        with open(current_branch_path, "r", encoding="utf-8", newline="\n") as f:
            current_branch = json.load(f)
            current_branch["current_branch"] = branch

        tmp_path = cwd / ".sccs" / "current_branch" / "tmp"

        with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(current_branch, f, indent=4)

        (tmp_path).replace((cwd / ".sccs" / "current_branch" / "current_branch.json"))

    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def check_branch_to_switch() -> None:
    """Check if the branch to switch to is valid."""

    branch_to_switch = utils.entered_arguement(2)
    branches = Repository.current_branch_data(key="branches")

    if not branch_to_switch:
        raise exceptions.InvalidArgumentError(
            "No branch specified. Please provide a branch name to switch to."
        )

    if branch_to_switch not in branches:
        raise exceptions.BranchNotFoundError(
            f"Branch '{branch_to_switch}' does not exist."
        )


def sanitize_branch() -> str:
    """Sanitize the branch name."""

    return utils.clean_directory_name(utils.entered_arguement(2))


def check_commit(cwd: Path | None = None) -> None:
    """
    Check if the commit object exists in the document history.
    """

    commit = Repository.branch(sanitize_branch(utils.entered_arguement(2))).latest_commit()

    if cwd is None:
        cwd = Path.cwd()
    if not (cwd / ".sccs" / "objects" / "docx" / f"{commit}.docx").is_file():
        raise exceptions.CommitNotFoundError(f"Commit object '{commit}' not found.")


def copy_commit_to_main(cwd: Path | None = None) -> None:
    """Copy the commit file to the main document."""
    if cwd is None:
        cwd = Path.cwd()
    try:
        shutil.copy2(
            (cwd / ".sccs" / "objects" / "docx" / f"{Repository.branch(sanitize_branch(utils.entered_arguement(2))).latest_commit()}.docx"),
            (cwd / f"{cwd.name}.docx"),
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

    update_current_branch()

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
