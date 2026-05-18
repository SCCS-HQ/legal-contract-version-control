#!/usr/bin/env python3
"""Check the status of the current document for uncommitted changes."""

import json
import sys
from pathlib import Path

import exceptions
import utils


def get_latest_commit_hash_file(
    current_branch: str | None = None, cwd: Path | None = None
) -> str:
    """Retrieve the hash of the latest commit from SCCS metadata."""
    if cwd is None:
        cwd = utils.working_directory_path
    # get the latest commit filename hash from commit history
    history_path = (
        cwd / ".sccs" / "branches" / current_branch / "history" / "commit_history.json"
    )
    if not Path(history_path).is_file():
        print(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )
        raise FileNotFoundError(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )

    try:
        with open(history_path, "r", encoding="utf-8", newline="\n") as history_file:
            history = json.load(history_file)
            latest_commit_hash = history["history"]["latest_commit"]

    except Exception as e:
        raise exceptions.FileOpenError from e

    if not latest_commit_hash:
        raise exceptions.InvalidMetadataError(
            "History file is missing the latest commit information. Please reinitialize"
            " SCCS for this file."
        )

    return latest_commit_hash


def get_latest_commit_file_binary_hash(
    current_branch: str | None = None, cwd: Path | None = None
) -> str:
    """Retrieve the hash of the latest committed file from SCCS metadata."""

    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch is None:
        current_branch = utils.get_current_branch()
    # get the hash of the latest committed file
    latest_commit_hash = get_latest_commit_hash_file(current_branch, cwd=cwd)
    latest_commit_file_hash_path = (
        cwd
        / ".sccs"
        / "branches"
        / current_branch
        / "commit_file_hash"
        / "commit_file_hash.json"
    )
    if not Path(latest_commit_file_hash_path).is_file():
        raise FileNotFoundError(
            "Latest commit file hash not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    try:
        with open(
            latest_commit_file_hash_path, "r", encoding="utf-8", newline="\n"
        ) as f:
            commit_file_hash_data = json.load(f)
            latest_commit_file_hash = commit_file_hash_data.get(latest_commit_hash)

        if not latest_commit_file_hash:
            raise exceptions.InvalidMetadataError(
                "Latest commit file hash is missing from JSON. Please reinitialize SCCS"
                " for this file."
            )

    except Exception as e:
        raise exceptions.FileOpenError from e

    return latest_commit_file_hash


def compare_hashes(old_hash: str, new_hash: str) -> bool:
    """Compare two hashes and return True if they are the same, False otherwise."""
    return old_hash == new_hash


def compare_changes_and_exit(old_hash: str, new_hash: str) -> None:
    """Compare the old and new hashes and exit with 0 if no changes are detected and
    raise exceptions.UncommittedChangesError if changes are detected."""
    if compare_hashes(old_hash, new_hash):
        print("No changes detected since the latest commit. Nothing to commit.")
        sys.exit(0)
    else:
        raise exceptions.UncommittedChangesError(
            "Changes detected since the latest commit. You can proceed with committing "
            "these changes."
        )


def main() -> None:
    """Run functions for the <sccs status> command."""

    utils.check_sccs_layout()
    compare_changes_and_exit(
        get_latest_commit_file_binary_hash(), utils.hash_current_docx_binary()
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
