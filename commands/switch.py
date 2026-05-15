"""Switch between document branches."""

import json
import shutil
import sys
from pathlib import Path

import exceptions
import utils


def get_branch_to_switch() -> str | None:
    """Retrieve the branch name to switch to from command-line arguments."""
    return sys.argv[2] if len(sys.argv) > 2 else None


def update_current_branch(
    branch: str, current_branch_path: Path = None, cwd: Path = None
) -> None:
    """Update the current branch in the SCCS metadata."""
    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch_path is None:
        current_branch_path = utils.current_branch_path
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


def check_branch_to_switch(branch_to_switch: str | None, branches: list) -> None:
    """Check if the branch to switch to is valid."""
    if not branch_to_switch:
        raise exceptions.InvalidArgumentError(
            "No branch specified. Please provide a branch name to switch to."
        )

    if branch_to_switch not in branches:
        raise exceptions.BranchNotFoundError(
            f"Branch '{branch_to_switch}' does not exist."
        )


def get_latest_commit_binary_hash(
    branch: str, latest_commit: str, cwd: Path = None
) -> str:
    """Retrieve the latest commit binary hash for a given branch."""
    if cwd is None:
        cwd = utils.working_directory_path
    try:
        with open(
            (
                cwd
                / ".sccs"
                / "branches"
                / branch
                / "commit_file_hash"
                / "commit_file_hash.json"
            ),
            "r",
            encoding="utf-8",
            newline="\n",
        ) as f:
            return json.load(f).get(latest_commit)
    except Exception as e:
        raise exceptions.FileOpenError from e


def check_for_changes(
    branch: str, latest_commit_binary_hash: str, current_document_hash: str
) -> None:
    """Check if there are uncommitted changes on the current branch."""
    if not current_document_hash == latest_commit_binary_hash:
        raise exceptions.UncommittedChangesError(
            f"The current file has uncommitted changes on the current branch '{branch}'"
            f". Please commit your changes before switching branches."
        )


def sanitize_branch(branch_name: str) -> str:
    """Sanitize the branch name."""
    return utils.clean_directory_name(branch_name)


def get_latest_commit(branch: str, cwd: Path = None) -> str:
    """Retrieve the latest commit hash for a given branch."""
    if cwd is None:
        cwd = utils.working_directory_path
    try:
        with open(
            (cwd / ".sccs" / "branches" / branch / "history" / "commit_history.json"),
            "r",
            encoding="utf-8",
            newline="\n",
        ) as f:
            history = json.load(f)
            return history["history"]["latest_commit"]
    except Exception as e:
        raise exceptions.FileOpenError from e


def check_commit(commit: str, cwd: Path = None) -> None:
    """Check if the commit object exists."""
    if cwd is None:
        cwd = utils.working_directory_path
    if not (cwd / ".sccs" / "objects" / "docx" / f"{commit}.docx").is_file():
        raise exceptions.CommitNotFoundError(f"Commit object '{commit}' not found.")


def copy_commit_to_main(commit: str, cwd: Path = None) -> None:
    """Copy the commit file to the main document."""
    if cwd is None:
        cwd = utils.working_directory_path
    try:
        shutil.copy2(
            (cwd / ".sccs" / "objects" / "docx" / f"{commit}.docx"),
            (cwd / f"{cwd.name}.docx"),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_confirmation(branch_to_switch: str) -> None:
    """Print a confirmation message for successful branch switch."""

    print(f"Successfully switched to branch '{branch_to_switch}'.")


def main() -> None:
    """Run functions for the <sccs switch> command."""

    utils.check_sccs_layout()

    branches = utils.get_branch_data(key="branches")

    current_branch = utils.get_current_branch()

    latest_commit = get_latest_commit(current_branch)

    latest_commit_binary_hash = get_latest_commit_binary_hash(
        current_branch, latest_commit
    )

    current_document_hash = utils.hash_current_docx_binary()

    check_for_changes(current_branch, latest_commit_binary_hash, current_document_hash)

    branch_to_switch = get_branch_to_switch()

    check_branch_to_switch(branch_to_switch, branches)

    branch_to_switch = sanitize_branch(branch_to_switch)

    latest_commit_on_branch_to_switch = get_latest_commit(branch_to_switch)

    check_commit(latest_commit_on_branch_to_switch)

    copy_commit_to_main(latest_commit_on_branch_to_switch)

    update_current_branch(branch_to_switch)

    print_confirmation(branch_to_switch)


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
