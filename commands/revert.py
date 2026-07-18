#!/usr/bin/env python3
"""Revert the current document to the specified commit."""

import shutil

from anyio import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def revert(c: SCCSConstants, repo: RepositoryLayout, commit_hash: str) -> None:
    """Revert the current document to the specified commit by copying 'src' to 'dst'."""

    src = repo.commit_file(commit_hash, c.DOCX_DIR, path=True)

    if not src.is_file():
        raise exceptions.InvalidArgumentError(
            c.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_name=src.stem)
        )

    try:
        shutil.copy2(src, repo.document_path())
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_revert_confirmation_message(c: SCCSConstants, commit_hash: str, new_commit_hash: str) -> None:
    """Print a confirmation message for the revert."""

    print(
        c.REVERT_SUCCESS_MESSAGE_TEMPLATE.format(commit_hash=commit_hash, new_commit_hash=new_commit_hash)
    )


def main(c: SCCSConstants, repo: RepositoryLayout, commit_hash: str) -> None:
    """Main function to handle the revert command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    revert(c, repo, commit_hash)

    commit_hash = repo.commit_file(commit_hash, c.DOCX_DIR, hash_10_char=True)

    new_commit_hash = repo.commit_changes(
        c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(commit_hash=commit_hash)
    )

    print_revert_confirmation_message(c, commit_hash, new_commit_hash)


if __name__ == "__main__":
    utils.run_command(main, 2)
