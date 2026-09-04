#!/usr/bin/env python3

from pathlib import Path
import shutil
import tempfile

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryStatus,
    RepositoryWrite,
)


def validate_commit_message(c: SCCSConstants, commit_message: str | None) -> None:

    if commit_message is None or not commit_message:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=c.COMMIT_MESSAGE_FIELD_NAME
            )
        )


def print_commit_success_message(c: SCCSConstants, commit_identifier: str) -> None:

    print(
        c.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
        )
    )


def finalize_commit(rw, staging_rw):

    shutil.move(staging_rw.root, rw.root)

def main(
    c: SCCSConstants,
    commit_message: str,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    validate_commit_message(c, commit_message)

    staging_root = Path(tempfile.mkdtemp(prefix=c.TEMPORARY_DIRECTORY_PREFIX, dir=rd.root.parent))

    try:
        shutil.copytree(rd.root, staging_root, dirs_exist_ok=True)

        staging_rw = RepositoryWrite(staging_root, c, rw.target)
        commit_identifier = staging_rw.commit_changes(commit_message)

        finalize_commit(rw, staging_rw)

    except Exception as e:
        if staging_root.exists():
            shutil.rmtree(staging_root, ignore_errors=True)

        raise e


    print_commit_success_message(c, commit_identifier)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
