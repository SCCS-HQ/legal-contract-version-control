#!/usr/bin/env python3

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def revert(c: SCCSConstants, commit_path: Path, rp: RepositoryPaths) -> None:

    if not commit_path.is_file():
        raise exceptions.SCCSException(
            c.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
                file_name=commit_path.stem
            )
        )

    try:
        shutil.copy2(commit_path, rp.document_path())
    except Exception as e:
        raise exceptions.SCCSException() from e


def print_revert_success_message(
    c: SCCSConstants, commit_identifier: str, new_commit_identifier: str
) -> None:

    print(
        c.REVERT_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
            new_commit_identifier=new_commit_identifier[
                : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
            ],
        )
    )


def main(
    c: SCCSConstants,
    commit_identifier: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    commit_path = rd.commit_identifier_to_full_path(
        commit_identifier, c.DOCUMENT_DIRECTORY
    )

    revert(c, commit_path, rp)

    new_commit_identifier = rw.commit_changes(
        c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
        )
    )

    full_commit_identifier = rd.short_commit_identifier_to_full(commit_identifier)

    print_revert_success_message(c, full_commit_identifier, new_commit_identifier)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
