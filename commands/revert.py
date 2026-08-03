#!/usr/bin/env python3
"""Revert the current document to the specified commit."""

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryPaths,
    RepositoryData,
    RepositoryWrite,
    RepositoryStatus,
    TargetBranch,
)


def revert(c: SCCSConstants, commit_hash: str, rd: RepositoryData, rp: RepositoryPaths) -> None:
    """Revert the current document to the specified commit by copying 'src' to 'dst'."""

    src = rd.hash_to_full_path(commit_hash)

    if not src.is_file():
        raise exceptions.InvalidArgumentError(
            c.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_name=src.stem)
        )

    try:
        shutil.copy2(src, rp.document_path())
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_revert_confirmation_message(c: SCCSConstants, commit_hash: str, new_commit_hash: str) -> None:
    """Print a confirmation message for the revert."""

    print(
        c.REVERT_SUCCESS_MESSAGE_TEMPLATE.format(commit_hash=commit_hash, new_commit_hash=new_commit_hash)
    )


def main(c: SCCSConstants, commit_hash: str, rd: RepositoryData, rs: RepositoryStatus, rp: RepositoryPaths, rw: RepositoryWrite) -> None:
    """Main function to handle the revert command."""
    rs.check_repository_layout()

    rs.check_for_uncommitted_changes()

    revert(c, commit_hash, rd, rp)

    commit_path = rd.hash_to_full_path(commit_hash)

    new_commit_hash = rw.commit_changes(
        c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(commit_hash=commit_path)
    )

    print_revert_confirmation_message(c, commit_hash, new_commit_hash)


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
