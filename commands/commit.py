#!/usr/bin/env python3
"""Commit latest changes to the current branch."""

from pathlib import Path
import sys

import exceptions
import utils
from repository_layout import RepositoryLayout


def print_commit_confirmation_message(Repo: RepositoryLayout, confirmation_msg: str) -> None:
    """Print a confirmation message for the commit using 'sha_hash'."""

    print(f"Commit {Repo.commit_changes(confirmation_msg)[:10]} created successfully.\n")


def main(Repo: RepositoryLayout) -> None:
    """Run functions for the <sccs commit> command."""
    Repo.check_repository_layout()

    commit_message = utils.entered_arguement(2)

    print_commit_confirmation_message(Repo, commit_message)


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
