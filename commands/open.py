import os
import shutil
import sys
from pathlib import Path

import utils


def get_commit_path_input():
    commit_path = input("Enter the path to the commit file (.docx): ").strip()
    return commit_path


def check_commit_path_input(commit_path):
    if commit_path == "":
        print("Commit file path cannot be empty.")
        sys.exit(1)

    if not Path(commit_path).is_file() or Path(commit_path).suffix.lower() != ".docx":
        print("Invalid commit file path, make sure the file exists and is a .docx file")
        sys.exit(1)


def confirm_before_proceeding(commit_path, docx_path=None, cwd=None):
    if docx_path is None:
        docx_path = utils.current_file_docx_path
    if cwd is None:
        cwd = utils.working_directory_path
    confirm = (
        input(
            f"Are you sure you want to overwrite '{cwd}/{os.path.basename(docx_path)}' "
            f"with the contents of '{cwd}/{os.path.basename(commit_path)}'?\nThis "
            f"action will replace the current content of the .docx file. (Y/N): "
        )
        .strip()
        .lower()
    )
    if confirm != "y":
        print("Update canceled.")
        sys.exit(0)


def check_changes(commit_path, docx_path=None):
    if docx_path is None:
        docx_path = utils.current_file_docx_path
    if (
        Path(docx_path).exists()
        and Path(commit_path).exists()
        and os.path.samefile(docx_path, commit_path)
    ):
        print(
            "The commit file is the same as the current file. No changes will be made."
        )
        sys.exit(0)


def copy_file_commit(commit_path, docx_path=None):
    if docx_path is None:
        docx_path = utils.current_file_docx_path

    try:
        shutil.copy2(commit_path, docx_path)
    except Exception as e:
        print(f"Error occurred while updating the file: {e}")
        sys.exit(1)


def print_rewrite_confirmation_message(commit_path, docx_path=None):
    if docx_path is None:
        docx_path = utils.current_file_docx_path
    print(
        f"File '{os.path.basename(docx_path)}' has been updated with the contents of "
        f"'{os.path.basename(commit_path)}'."
    )


if __name__ == "__main__":
    utils.check_sccs_layout()

    commit_path = get_commit_path_input()

    check_commit_path_input(commit_path)

    check_changes(commit_path)

    confirm_before_proceeding(commit_path)

    copy_file_commit(commit_path)

    print_rewrite_confirmation_message(commit_path)
