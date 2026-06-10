#!/usr/bin/env python3
"""Print a list of all available commands."""

import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


MESSAGES_TO_PRINT = [
    "SCCS Help",
    "Available commands:",
    "  sccs branch - Create a new branch, delete, or list branches.",
    "  sccs clone - Clone a hosted SCCS repository with a URL.",
    "  sccs commit - Commit changes to the repository.",
    "  sccs config - Configure a repository's data value (remote, name, email)",
    "  sccs diff - Show differences between the current document and a past commit.",
    "  sccs help - Print this help message.",
    "  sccs init - Initialize a new SCCS repository.",
    "  sccs log - Print a list of past commits for the current branch.",
    "  sccs open - Open a commit file and update the current document.",
    "  sccs publish - Publish a local repository to a hosting service.",
    "  sccs pull - Pull changes from a remote repository and merge them into the local "
    "repository.",
    "  sccs push - Push changes from the local repository to a remote repository.",
    "  sccs revert - Revert the current document to the specified commit.",
    "  sccs reset - Delete all uncommitted changes.",
    "  sccs switch - Switch between document branches.",
    "  sccs status - Check the status of the current document for uncommitted changes.",
    "  sccs merge - Merge the entered branch into the current branch.",
]


def print_help() -> None:
    """Print help each item in 'messages'."""

    for i in MESSAGES_TO_PRINT:
        print(i)


def main() -> None:
    """Run functions for the <sccs help> command."""
    utils.check_sccs_layout()

    print_help()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
