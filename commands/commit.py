#!/usr/bin/env python3
"""Commit latest changes to the current branch."""

from pathlib import Path
import sys

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def print_commit_confirmation_message() -> None:
    """Print a confirmation message for the commit using 'sha_hash'."""

    try:
        sha_hash = utils.commit_changes(utils.entered_arguement(2))
    except Exception as e:
        raise exceptions.CommitChangesError("Failed to commit changes") from e
    print(f"Commit {sha_hash[:10]} created successfully.\n")


def main() -> None:
    """Run functions for the <sccs commit> command."""
    Repository.check_repository_layout()

    print_commit_confirmation_message()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
