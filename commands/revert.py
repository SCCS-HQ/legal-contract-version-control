#!/usr/bin/env python3
"""Revert the current document to the specified commit."""

import shutil
import sys
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def revert(constants: SCCSConstants, repo: RepositoryLayout, commit_hash: str) -> None:
    """Revert the current document to the specified commit by copying 'src' to 'dst'."""

    src = repo.commit_file(commit_hash, constants.DOCX_DIR)

    if not src.is_file():
        raise exceptions.InvalidArgumentError(
            constants.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_name=src.stem)
        )

    try:
        shutil.copy2(src, repo.document_path())
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_revert_confirmation_message(constants: SCCSConstants, commit_hash: str, new_commit_hash: str) -> None:
    """Print a confirmation message for the revert."""

    print(
        constants.REVERT_SUCCESS_MESSAGE_TEMPLATE.format(commit_hash=commit_hash, new_commit_hash=new_commit_hash)
    )


def main(constants: SCCSConstants, repo: RepositoryLayout, commit_hash: str) -> None:
    """Main function to handle the revert command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    revert(constants, repo, commit_hash)

    commit_hash = repo.commit_file(commit_hash, constants.DOCX_DIR, hash_10_char=True)

    new_commit_hash = repo.commit_changes(
        constants.REVERT_COMMIT_MESSAGE_TEMPLATE.format(commit_hash=commit_hash)
    )

    print_revert_confirmation_message(constants, commit_hash, new_commit_hash)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(constants, repository, utils.entered_argument(2))

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
