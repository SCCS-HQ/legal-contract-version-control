#!/usr/bin/env python3
"""Open a commit file and update the current document."""

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def validate_commit_hash(constants: SCCSConstants, commit_hash: str, output_file_name: str) -> None:
    """
    Validate the commit hash format.
    """

    if not commit_hash or not len(commit_hash) == constants.COMMIT_HASH_DISPLAY_LENGTH and not len(commit_hash) == constants.FULL_COMMIT_HASH_LENGTH or not all(c in constants.HEX_DIGITS for c in commit_hash):
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.COMMIT_FILE_FIELD_NAME))


def copy_file_commit(constants: SCCSConstants, commit_hash: str, commit_path: Path) -> None:
    """
    Copy the commit file to the current document, effectively opening the older commit.
    """

    try:
        shutil.copy2(
            commit_path,
            constants.output_file_name
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_rewrite_confirmation_message(constants: SCCSConstants, commit_hash: str, output_file_name: str) -> None:
    """
    Print the confirmation message after rewriting the file using the document name.
    """

    print(
        constants.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_hash=commit_hash,
            output_file=output_file_name
        )
    )


def main(constants: SCCSConstants, repo: RepositoryLayout, commit_hash: str | None = None) -> None:
    """Run functions for the <sccs open> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    output_file_name = constants.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(commit_hash=commit_hash) + constants.DOCX_EXTENSION

    validate_commit_hash(constants, commit_hash, output_file_name)

    commit_path = repo.commit_file(commit_hash, constants.DOCX_DIR)

    commit_hash = commit_path.stem[:constants.COMMIT_HASH_DISPLAY_LENGTH]

    copy_file_commit(constants, commit_hash, commit_path)

    print_rewrite_confirmation_message(constants, commit_hash, output_file_name)


if __name__ == "__main__":
    utils.run_command(main, 2)