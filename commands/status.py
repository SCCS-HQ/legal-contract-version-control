#!/usr/bin/env python3
"""Check the status of the current document for uncommitted changes."""

import utils
from repository_layout import RepositoryLayout
from constants_classes import SCCSConstants


def print_status_message(c: SCCSConstants, uncommitted_changes: bool) -> None:
    """Print the status message to the user."""
    if uncommitted_changes:
        print(c.UNCOMMITTED_CHANGES_FOUND)
    else:
        print(c.NO_UNCOMMITTED_CHANGES)


def main(c: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs status> command."""
    repo.check_repository_layout()

    uncommitted_changes = repo.check_for_uncommitted_changes(raise_on_changes=False)

    print_status_message(c, uncommitted_changes)


if __name__ == "__main__":
    utils.run_command(main)