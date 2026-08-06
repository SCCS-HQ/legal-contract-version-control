#!/usr/bin/env python3
"""Print a list of all available commands."""

from pathlib import Path

import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryStatus,
    TargetBranch,
)


def print_help(c: SCCSConstants) -> None:
    """Print help each item in 'messages'."""

    for i in c.HELP_MESSAGES:
        print(i)


def main(c: SCCSConstants, rd: RepositoryData, rs: RepositoryStatus) -> None:
    """Run functions for the <sccs help> command."""
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    print_help(c)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(main, RepositoryData(Path.cwd(), c, target), RepositoryStatus(Path.cwd(), c, target))
