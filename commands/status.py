#!/usr/bin/env python3
"""Check the status of the current document for uncommitted changes."""

import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def print_status_message() -> None:
    """Print the status message to the user."""
    uncommitted_changes = Repository.check_for_uncommitted_changes("status", exit=False)
    if uncommitted_changes:
        print("Uncommitted changes detected.\n")
    else:
        print("No uncommitted changes detected.\n")


def main() -> None:
    """Run functions for the <sccs status> command."""
    Repository.check_repository_layout()

    print_status_message()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
