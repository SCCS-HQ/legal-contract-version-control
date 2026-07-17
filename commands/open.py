#!/usr/bin/env python3
"""Open a commit file and update the current document."""

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def validate_commit_hash(c: SCCSConstants, commit_hash: str) -> None:
    """
    Validate the commit hash format.
    """

    valid_len = len(commit_hash) in (c.COMMIT_HASH_DISPLAY_LENGTH, c.FULL_COMMIT_HASH_LENGTH)

    if not commit_hash or not valid_len or not all(c in c.HEX_DIGITS for c in commit_hash):
        raise exceptions.InvalidArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.COMMIT_FILE_FIELD_NAME))


def copy_file_commit(commit_path: Path, output_file_name) -> None:
    """
    Copy the commit file to the current document, effectively opening the older commit.
    """

    try:
        shutil.copy2(
            commit_path,
            output_file_name
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_rewrite_confirmation_message(c: SCCSConstants, commit_hash: str, output_file_name: str) -> None:
    """
    Print the confirmation message after rewriting the file using the document name.
    """

    print(
        c.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_hash=commit_hash,
            output_file=output_file_name
        )
    )


def main(c: SCCSConstants, repo: RepositoryLayout, commit_hash: str | None = None) -> None:
    """Run functions for the <sccs open> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    output_file_name = c.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(commit_hash=commit_hash) + c.DOCX_EXTENSION

    validate_commit_hash(c, commit_hash, output_file_name)

    commit_path = repo.commit_file(commit_hash, c.DOCX_DIR, path=True)

    commit_hash = commit_path.stem[:c.COMMIT_HASH_DISPLAY_LENGTH]

    copy_file_commit(commit_path, output_file_name)

    print_rewrite_confirmation_message(c, commit_hash, output_file_name)


if __name__ == "__main__":
    utils.run_command(main, 2)