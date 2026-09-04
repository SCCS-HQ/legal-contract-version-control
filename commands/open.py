#!/usr/bin/env python3

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryStatus,
)


def validate_commit_identifier(c: SCCSConstants, commit_identifier: str | None) -> None:

    if not commit_identifier:
        raise exceptions.SCCSException(c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE)

    if len(commit_identifier) != c.FULL_COMMIT_IDENTIFIER_LENGTH or not all(
        i in c.HEX_DIGITS for i in commit_identifier
    ):
        raise exceptions.SCCSException(c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE)


def copy_commit_file(commit_path: Path, output_file_name: Path) -> None:

    try:
        shutil.copy2(commit_path, output_file_name)
    except Exception as e:
        raise exceptions.SCCSException(c.OPEN_COPY_ERROR_MESSAGE) from e


def print_open_success_message(
    c: SCCSConstants, commit_identifier: str, output_file_name: Path
) -> None:

    print(
        c.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
            output_file=output_file_name,
        )
    )


def main(
    c: SCCSConstants, commit_identifier: str, rd: RepositoryData, rs: RepositoryStatus
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    commit_path = rd.commit_identifier_to_full_path(
        commit_identifier, c.DOCUMENT_DIRECTORY
    )

    full_commit_identifier = rd.short_commit_identifier_to_full(commit_identifier)

    output_file_name = Path(
        c.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(
            commit_identifier=full_commit_identifier[
                : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
            ]
        )
    ).with_suffix(c.DOCUMENT_EXTENSION)

    staging_root = utils.create_staging_directory(c, Path.cwd())

    try:
        copy_commit_file(commit_path, staging_root / output_file_name.name)
        utils.promote_staging(staging_root, Path.cwd())
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_open_success_message(c, full_commit_identifier, output_file_name)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
    )
