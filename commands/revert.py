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


def revert(
    c: SCCSConstants, commit_path: Path, staging_root: Path, repo_name: str
) -> None:

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

    staging_root = utils.create_staging_directory(c, utils.current_symlink_path(c, rp.repository_name))

    new_commit_identifier = None

    try:
        shutil.copytree(utils.current_symlink_path(c, rp.repository_name), staging_root, dirs_exist_ok=True)

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
        utils.promote_versioned(c, staging_root, rp.repository_name)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_revert_success_message(
        c, rd.short_commit_identifier_to_full(commit_identifier), new_commit_identifier
    )

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().parent.parent.name
    repository_root = utils.current_symlink_path(c, repository_name)
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(repository_root, repository_name, c, target),
        RepositoryPaths(repository_root, repository_name, c, target),
        RepositoryStatus(repository_root, repository_name, c, target),
        RepositoryWrite(repository_root, repository_name, c, target),
    )
