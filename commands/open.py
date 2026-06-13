#!/usr/bin/env python3
"""Open a commit file and update the current document."""

import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def confirm_before_proceeding() -> None:
    """Confirm with the user before proceeding with overwriting the current document."""

    confirm = (
        input(
            f"Are you sure you want to overwrite '{Repository.document_path().name}' "
            f"with the contents of '{Repository.commit_path(
                "docx", Path.cwd(), utils.entered_arguement(2)
            ).name[:10]}'?\nThis action will replace the current content of the .docx "
            f"file. (Y/N): "
        )
        .strip()
        .lower()
    )
    if confirm != "y":
        print("Update canceled.\n")
        sys.exit(0)


def copy_file_commit() -> None:
    """
    Copy the commit file to the current document, effectively opening the older commit.
    """

    try:
        shutil.copy2(
            Repository.commit_path(
                "docx", Path.cwd(), utils.entered_arguement(2)
            ), Repository.document_path
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_rewrite_confirmation_message() -> None:
    """
    Print the confirmation message after rewriting the file using the document name.
    """

    print(
        f"File '{Repository.document_path.name}' has been updated with the contents of "
        f"'{Repository.commit_path(
            "docx", Path.cwd(), utils.entered_arguement(2)
        ).name[:10]}'.\n"
    )


def main() -> None:
    """Run functions for the <sccs open> command."""
    Repository.check_repository_layout()

    Repository.check_for_uncommitted_changes("open")

    confirm_before_proceeding()

    copy_file_commit()

    print_rewrite_confirmation_message()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
