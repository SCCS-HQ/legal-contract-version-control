#!/usr/bin/env python3

from local_sccs.constants_classes import SCCSConstants
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryStatus,
)


def print_status_success_message(c: SCCSConstants, uncommitted_changes: bool) -> None:
    """
    Print the status of the current document based on whether uncommitted changes were
    detected.
    """

    if uncommitted_changes:
        print(c.UNCOMMITTED_CHANGES_FOUND)
    else:
        print(c.NO_UNCOMMITTED_CHANGES)


def main(c: SCCSConstants, rd: RepositoryData, rs: RepositoryStatus) -> None:
    """
    Run the status command by setting the current branch as the target, validating the
    repository layout, and printing the status of the current document.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    print_status_success_message(c, rs.validate_uncommitted_changes())

    rs.target.reset()