#!/usr/bin/env python3
"""Commit latest changes to the current branch."""

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import exceptions
import utils


def get_commit_message() -> str:
    """Retrieve the commit message from the user."""

    if len(sys.argv) <= 2 or not sys.argv[2].strip():
        raise exceptions.EmptyCommitMessageError("Commit message cannot be empty.")

    return " ".join(sys.argv[2:]).strip()


def print_commit_confirmation_message(sha_hash: str) -> None:
    """Print a confirmation message for the commit."""

    print(f"Commit {sha_hash} created successfully.")


def main() -> None:
    """Run functions for the <sccs commit> command."""
    utils.check_sccs_layout()

    sha_hash = utils.commit_changes(get_commit_message())

    print_commit_confirmation_message(sha_hash)


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
