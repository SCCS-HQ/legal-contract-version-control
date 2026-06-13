#!/usr/bin/env python3
"""Delete all uncommitted changes."""

import json
import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def reset() -> None:
    """Delete all uncommitted changes."""

    shutil.copy2(
        Repository.current_branch().latest_commit_path("docx"),
        Repository.document_path(),
    )


def print_success_message() -> None:
    """Print a success message after resetting the document."""
    print(
        "All uncommitted changes have been deleted. The document has been reset to the "
        "latest commit.\n"
    )


def main() -> None:
    """Main function to handle the <reset> command."""
    Repository.check_repository_layout()

    reset()
    print_success_message()


if __name__ == "__main__":
    try:
        main()
    except exceptions.SCCSException as e:
        print(f"Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred:\n{e}\n")
        sys.exit(1)
