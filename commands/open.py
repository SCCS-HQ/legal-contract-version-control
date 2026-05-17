#!/usr/bin/env python3
"""Open a commit file and update the current document."""

import shutil
import sys
from pathlib import Path

import exceptions
import utils


def get_commit_path_input() -> Path | None:
    """Get the absolute path of the commit file from the command-line arguments."""
    return Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None


def check_commit_path_input(commit_path: Path) -> None:
    """Check the validity of the commit file path."""
    if not commit_path:
        raise exceptions.InvalidArgumentError("Commit file path cannot be empty.")

    if not commit_path.is_file():
        raise FileNotFoundError("Commit file does not exist.")

    if commit_path.suffix.lower() != ".docx":
        raise exceptions.InvalidFileTypeError("Commit file is not a .docx file.")


def confirm_before_proceeding(
    commit_path: Path, docx_path: Path | None = None, cwd: Path | None = None
) -> None:
    """Confirm with the user before proceeding with overwriting the current document."""
    if docx_path is None:
        docx_path = utils.current_file_docx_path
    if cwd is None:
        cwd = utils.working_directory_path
    confirm = (
        input(
            f"Are you sure you want to overwrite '{cwd}/{docx_path.name}' "
            f"with the contents of '{cwd}/{commit_path.name}'?\nThis "
            f"action will replace the current content of the .docx file. (Y/N): "
        )
        .strip()
        .lower()
    )
    if confirm != "y":
        print("Update canceled.")
        sys.exit(0)


def check_changes(commit_path: Path, docx_path: Path | None = None) -> None:
    """Check if the commit_path and docx_path refer to the same file."""
    if docx_path is None:
        docx_path = utils.current_file_docx_path
    if docx_path.exists() and commit_path.exists() and docx_path.samefile(commit_path):
        print(
            "The commit file is the same as the current file. No changes will be made."
        )
        sys.exit(0)


def copy_file_commit(commit_path: Path, docx_path: Path | None = None) -> None:
    """Copy the commit file to the current document."""
    if docx_path is None:
        docx_path = utils.current_file_docx_path

    try:
        shutil.copy2(commit_path, docx_path)
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_rewrite_confirmation_message(
    commit_path: Path, docx_path: Path | None = None
) -> None:
    """Print the confirmation message after rewriting the file."""
    if docx_path is None:
        docx_path = utils.current_file_docx_path
    print(
        f"File '{docx_path.name}' has been updated with the contents of "
        f"'{commit_path.name}'."
    )


def main() -> None:
    """Run functions for the <sccs open> command."""

    utils.check_sccs_layout()

    commit_path = get_commit_path_input()

    check_commit_path_input(commit_path)

    check_changes(commit_path)

    confirm_before_proceeding(commit_path)

    copy_file_commit(commit_path)

    print_rewrite_confirmation_message(commit_path)


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
