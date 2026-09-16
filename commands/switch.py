#!/usr/bin/env python3

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


def print_switch_success_message(c: SCCSConstants, branch_to_switch: str) -> None:
    """
    Print a success message indicating that the entered branch has been switched to.
    """

    print(c.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch))


def validate_branch_to_switch(
    c: SCCSConstants, branch_to_switch: str | None, rs: RepositoryStatus
) -> None:
    """
    Validate the entered branch by checking that it is not empty and exists in the
    repository. Raise an SCCSException if any validation fails.
    """

    utils.raise_if_empty(c, branch_to_switch, c.BRANCH_NAME_FIELD_NAME)

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
    """
    Validate the latest commit document of the entered branch by checking that it
    exists. Raise an SCCSException if the commit document is missing.
    """

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
    branch_to_switch: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the switch command by setting the current branch as the target, validating the
    repository layout and entered branch, and copying the latest commit document of the
    branch to the repository on a copy of the repository in a staging directory.

    Set the entered branch as the current branch, promote the staging directory to the
    repository root, print a success message, and reset the target branch when the
    operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_branch_to_switch(c, branch_to_switch, rs)

    validate_commit_identifier(c, branch_to_switch, rd, rs)

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:

        utils.copy_latest_commit_document(
            rd,
            branch_to_switch,
            staging_root / rd.paths.document_path().name,
            c.SWITCH_COPY_ERROR_MESSAGE,
        )

        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
        staging_rw.set_current_branch(branch_to_switch)

    print_switch_success_message(c, branch_to_switch)

    rs.target.reset()
