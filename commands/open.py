#!/usr/bin/env python3
"""Open a commit file and update the current document."""

import shutil
import sys
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def validate_commit_hash(constants: SCCSConstants, commit_hash: str) -> None:
    """
    Validate the commit hash format.
    """

    if not commit_hash or not len(commit_hash) == 10 or not len(commit_hash) == 64 or not all(c in "0123456789abcdef" for c in commit_hash):
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.COMMIT_FILE_FIELD_NAME)) from e


def copy_file_commit(constants: SCCSConstants, commit_hash: str, commit_path: Path) -> None:
    """
    Copy the commit file to the current document, effectively opening the older commit.
    """

    try:
        shutil.copy2(
            commit_path,
            constants.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(commit_hash=commit_hash)
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_rewrite_confirmation_message(constants: SCCSConstants, commit_hash: str) -> None:
    """
    Print the confirmation message after rewriting the file using the document name.
    """

    print(
        constants.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_hash=commit_hash,
            output_file=constants.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(commit_hash=commit_hash)
        )
    )


def main(constants: SCCSConstants, repo: RepositoryLayout, commit_hash: str | None = None) -> None:
    """Run functions for the <sccs open> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    validate_commit_hash(constants, commit_hash)

    commit_path = repo.commit_file(commit_hash, constants.DOCX_DIR)

    commit_hash = commit_path.stem[constants.COMMIT_HASH_DISPLAY_LENGTH]

    copy_file_commit(constants, commit_hash, commit_path)

    print_rewrite_confirmation_message(constants, commit_hash)


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