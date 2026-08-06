#!/usr/bin/env python3
"""Check the status of the current document for uncommitted changes."""

from pathlib import Path

import utils
from repository_layout import (
    RepositoryPaths,
    RepositoryData,
    RepositoryWrite,
    RepositoryStatus,
    TargetBranch,
)
from constants_classes import SCCSConstants


def print_status_message(c: SCCSConstants, uncommitted_changes: bool) -> None:
    """Print the status message to the user."""
    if uncommitted_changes:
        print(c.UNCOMMITTED_CHANGES_FOUND)
    else:
        print(c.NO_UNCOMMITTED_CHANGES)


def main(c: SCCSConstants, rd: RepositoryData, rs: RepositoryStatus) -> None:
    """Run functions for the <sccs status> command."""
    rs.target.set(rd.current_branch())
    
    rs.check_repository_layout()

    uncommitted_changes = rs.check_for_uncommitted_changes()

    print_status_message(c, uncommitted_changes)


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(main, RepositoryStatus(Path.cwd(), c, target))
