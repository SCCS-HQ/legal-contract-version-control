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


def print_revert_success_message(
    c: SCCSConstants, commit_identifier: str, new_commit_identifier: str
) -> None:
    """
    Print a success message indicating that the document has been reverted to the
    entered commit.
    """

    print(
        c.REVERT_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
            new_commit_identifier=new_commit_identifier[
                : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
            ],
        )
    )


def revert(
    c: SCCSConstants, commit_path: Path, staging_root: Path, repo_name: str
) -> None:
    """
    Copy the entered commit document to the staging directory. Raise an SCCSException if
    the commit file does not exist or cannot be copied.
    """

    if not commit_path.is_file():
        raise exceptions.SCCSException(
            c.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
                file_name=commit_path.stem
            )
        )

    try:
        shutil.copy2(
            commit_path, (staging_root / repo_name).with_suffix(c.DOCUMENT_EXTENSION)
        )
    except Exception as e:
        raise exceptions.SCCSException(c.REVERT_COPY_ERROR_MESSAGE) from e


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )


def main(
    c: SCCSConstants,
    commit_identifier: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the revert command by setting the current branch as the target, validating the
    repository layout, and copying the entered commit document to the repository on a
    copy of the repository in a staging directory.

    Commit the reverted document, promote the staging directory to the repository root,
    print a success message, and reset the target branch when the operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    commit_path = rd.commit_identifier_to_full_path(
        commit_identifier, c.DOCUMENT_DIRECTORY
    )

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:

        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
        revert(c, commit_path, staging_root, staging_rw.repository_name)
        new_commit_identifier = staging_rw.commit_changes(
            c.REVERT_COMMIT_MESSAGE_TEMPLATE.format(
                commit_identifier=commit_identifier[
                    : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
                ]
            ),
            allow_empty_commit=True,
        )

    print_revert_success_message(
        c, rd.short_commit_identifier_to_full(commit_identifier), new_commit_identifier
    )

    rs.target.reset()
