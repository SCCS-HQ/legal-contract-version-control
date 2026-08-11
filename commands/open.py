#!/usr/bin/env python3

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryStatus,
    TargetBranch,
)


def validate_commit_hash(c: SCCSConstants, commit_hash: str | None) -> None:

    if not commit_hash:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.COMMIT_FILE_FIELD_NAME)
        )

    valid_len = len(commit_hash) == (c.FULL_COMMIT_HASH_LENGTH)

    if not valid_len or not all(i in c.HEX_DIGITS for i in commit_hash):
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.COMMIT_FILE_FIELD_NAME)
        )


def copy_file_commit(commit_path: Path, output_file_name: Path) -> None:

    try:
        shutil.copy2(commit_path, output_file_name)
    except Exception as e:
        raise exceptions.FileCopyError() from e


def print_rewrite_confirmation_message(
    c: SCCSConstants, commit_hash: str, output_file_name: Path
) -> None:

    print(
        c.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_hash=commit_hash[: c.COMMIT_HASH_DISPLAY_LENGTH],
            output_file=output_file_name,
        )
    )


def main(
    c: SCCSConstants, commit_hash: str, rd: RepositoryData, rs: RepositoryStatus
) -> None:
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    rs.raise_for_uncommitted_changes()


    commit_path = rd.hash_to_full_path(commit_hash, c.DOCX_DIR)

    full_commit_hash = rd.resolve_full_hash(commit_hash)

    output_file_name = Path(
        c.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(
            commit_hash=full_commit_hash[: c.COMMIT_HASH_DISPLAY_LENGTH]
        )
    ).with_suffix(c.DOCX_EXTENSION)

    copy_file_commit(commit_path, output_file_name)

    print_rewrite_confirmation_message(c, full_commit_hash, output_file_name)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
    )
