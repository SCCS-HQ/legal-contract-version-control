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


def validate_branch_to_switch(
    c: SCCSConstants, branch_to_switch: str | None, rs: RepositoryStatus
) -> None:

    if not branch_to_switch:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )

    if not rs.branch_exists(branch_to_switch):
        raise exceptions.SCCSException(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch_to_switch
            )
        )


def validate_commit_identifier(
    c: SCCSConstants,
    branch_to_switch: str | None,
    rd: RepositoryData,
    rs: RepositoryStatus,
) -> None:

    rs.target.set(branch_to_switch)

    if not rd.commit_identifier_to_full_path(
        rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
    ).is_file():
        raise exceptions.SCCSException(
            c.SWITCH_COMMIT_FILE_MISSING_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch_to_switch
            )
        )

    rs.target.reset()


def copy_commit_to_main(
    c: SCCSConstants,
    branch_to_switch: str,
    rd: RepositoryData,
    staging_root: Path,
    rs: RepositoryStatus,
) -> None:

    rs.target.set(branch_to_switch)

    try:
        shutil.copy2(
            rd.commit_identifier_to_full_path(
                rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
            ),
            staging_root / rd.paths.document_path().name,
        )
    except Exception as e:
        raise exceptions.SCCSException(c.SWITCH_COPY_ERROR_MESSAGE) from e

    rs.target.reset()


def print_switch_success_message(c: SCCSConstants, branch_to_switch: str) -> None:

    print(c.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch))


def main(
    c: SCCSConstants,
    branch_to_switch: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_branch_to_switch(c, branch_to_switch, rs)

    validate_commit_identifier(c, branch_to_switch, rd, rs)

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        shutil.copytree(rp.root, staging_root, dirs_exist_ok=True)

        copy_commit_to_main(c, branch_to_switch, rd, staging_root, rs)
        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
        staging_rw.set_current_branch(branch_to_switch)
        utils.promote_staging(staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_switch_success_message(c, branch_to_switch)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )
