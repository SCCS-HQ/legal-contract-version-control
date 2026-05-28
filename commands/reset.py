#!/usr/bin/env python3
"""Delete all uncommitted changes."""

import json
import shutil
import sys
from pathlib import Path

import modules.exceptions as exceptions
import modules.utils as utils


def reset(cwd: Path | None = None) -> None:
    """Delete all uncommitted changes."""

    if cwd is None:
        cwd = utils.working_directory_path

    if not utils.check_for_uncommitted_changes("reset", exit=False, cwd=cwd):
        raise exceptions.NoUncommittedChangesError()

    with open(
        cwd
        / ".sccs"
        / "branches"
        / utils.get_current_branch(
            cwd / ".sccs" / "current_branch" / "current_branch.json"
        )
        / "history"
        / "commit_history.json"
    ) as f:
        data = json.load(f)
        latest_commit = data["history"]["latest_commit"]

    shutil.copy2(
        utils.validate_commit("docx", cwd, latest_commit),
        cwd / cwd.with_suffix(".docx").name,
    )


def print_success_message() -> None:
    """Print a success message after resetting the document."""
    print(
        "All uncommitted changes have been deleted. The document has been reset to the "
        "latest commit."
    )


def main() -> None:
    """Main function to handle the <reset> command."""
    utils.check_sccs_layout()
    reset()
    print_success_message()


if __name__ == "__main__":
    try:
        main()
    except exceptions.SCCSException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred:\n{e}\n")
        sys.exit(1)
