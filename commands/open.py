#!/usr/bin/env python3
"""Open a commit file and update the current document."""

import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def confirm_before_proceeding(
    docx_path: Path | None = None, cwd: Path | None = None
) -> None:
    """Confirm with the user before proceeding with overwriting the current document."""
    if docx_path is None:
        docx_path = Repository.document_path
    if cwd is None:
        cwd = Path.cwd()

    commit_name = Repository.commit_path(
        "docx", Path.cwd(), utils.entered_arguement(2)
    ).name[:10]

    confirm = (
        input(
            f"Are you sure you want to overwrite '{cwd}/{docx_path.name}' "
            f"with the contents of '{cwd}/{commit_name}'?\nThis "
            f"action will replace the current content of the .docx file. (Y/N): "
        )
        .strip()
        .lower()
    )
    if confirm != "y":
        print("Update canceled.\n")
        sys.exit(0)


def copy_file_commit(docx_path: Path | None = None) -> None:
    """
    Copy the commit file to the current document, effectively opening the older commit.
    """
    if docx_path is None:
        docx_path = Repository.document_path

    try:
        shutil.copy2(
            Repository.commit_path(
                "docx", Path.cwd(), utils.entered_arguement(2)
            ), docx_path
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_rewrite_confirmation_message(docx_path: Path | None = None) -> None:
    """
    Print the confirmation message after rewriting the file using the document name.
    """
    if docx_path is None:
        docx_path = Repository.document_path

    commit_name = Repository.commit_path(
        "docx", Path.cwd(), utils.entered_arguement(2)
    ).name[:10]

    print(
        f"File '{docx_path.name}' has been updated with the contents of "
        f"'{commit_name}'.\n"
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
