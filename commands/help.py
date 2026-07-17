#!/usr/bin/env python3
"""Print a list of all available commands."""

import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def print_help(c: SCCSConstants) -> None:
    """Print help each item in 'messages'."""

    for i in c.HELP_MESSAGES:
        print(i)


def main(c: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs help> command."""
    repo.check_repository_layout()

    print_help(c)


if __name__ == "__main__":
    utils.run_command(main)
