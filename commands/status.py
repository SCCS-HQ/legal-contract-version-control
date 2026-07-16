#!/usr/bin/env python3
"""Check the status of the current document for uncommitted changes."""

import sys
from pathlib import Path

from commands import constants_classes
import exceptions
import utils
from repository_layout import RepositoryLayout
from constants_classes import SCCSConstants, ErrorWrappers


def print_status_message(constants: SCCSConstants, uncommitted_changes: bool) -> None:
    """Print the status message to the user."""
    if uncommitted_changes:
        print(constants.UNCOMMITTED_CHANGES_FOUND)
    else:
        print(constants.NO_UNCOMMITTED_CHANGES)


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs status> command."""
    repo.check_repository_layout()

    uncommitted_changes = repo.check_for_uncommitted_changes(raise_on_changes=False)

    print_status_message(constants, uncommitted_changes)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(repository)

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)