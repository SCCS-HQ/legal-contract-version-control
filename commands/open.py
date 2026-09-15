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


def copy_commit_file(commit_path: Path, output_file_name: Path) -> None:
    """
    Copy the commit file to the output file name. Raise an SCCSException if the commit
    file cannot be copied.
    """

    try:
        shutil.copy2(commit_path, output_file_name)
    except Exception as e:
        raise exceptions.SCCSException(c.OPEN_COPY_ERROR_MESSAGE) from e

def main(
    c: SCCSConstants, commit_identifier: str, rd: RepositoryData, rs: RepositoryStatus
) -> None:
    """
    Run the open command by setting the current branch as the target, validating the
    repository layout and entered commit identifier, and copying the commit document to
    the current directory.

    Promote the staging directory to the current directory, print a success message, and
    reset the target branch when the operation completes.
    """

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

    with utils.staged_repository(c, Path.cwd(), Path.cwd()) as staging_root:
        copy_commit_file(commit_path, staging_root / output_file_name.name)

    print_open_success_message(c, full_commit_identifier, output_file_name)

    rs.target.reset()

def print_open_success_message(
    c: SCCSConstants, commit_identifier: str, output_file_name: Path
) -> None:
    """
    Print a success message indicating that the entered commit has been opened as the
    output file.
    """

    print(
        c.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
            output_file=output_file_name,
        )
    )

def validate_commit_identifier(
    c: SCCSConstants, commit_identifier: str, rd: RepositoryData
) -> None:
    """
    Validate the entered commit identifier by checking that it has a valid commit
    identifier length and contains only hexadecimal digits. Raise an SCCSException if
    the commit identifier is invalid.
    """

    rd.raise_for_commit_identifier_length(commit_identifier)

    if not all(i in c.HEX_DIGITS for i in commit_identifier):
        raise exceptions.SCCSException(c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE)


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
    )
