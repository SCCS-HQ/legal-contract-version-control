#!/usr/bin/env python3
"""Print a list of all available commands."""

import sys
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def print_help(constants: SCCSConstants) -> None:
    """Print help each item in 'messages'."""

    for i in constants.HELP_MESSAGES:
        print(i)


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs help> command."""
    repo.check_repository_layout()

    print_help(constants)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        repository = RepositoryLayout(Path.cwd, constants)
        error_wrappers = ErrorWrappers()
        main()

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
