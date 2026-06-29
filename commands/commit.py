#!/usr/bin/env python3
"""Commit latest changes to the current branch."""

from pathlib import Path
import sys

import exceptions
import utils
from repository_layout import RepositoryLayout
from constants_classes import SCCSConstants, ErrorWrappers


def print_commit_confirmation_message(constants: SCCSConstants, Repo: RepositoryLayout, sha_hash) -> None:
    """Print a confirmation message for the commit using 'sha_hash'."""

    try:
        print(constants.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(sha_hash=sha_hash[:10]))
    except Exception as e:
        raise exceptions.SCCSException(constants.COMMIT_FAILURE_ERROR_MESSAGE) from e


def validate_commit_message(constants: SCCSConstants, commit_message: str) -> None:

    if commit_message is None or not commit_message.strip():
        raise exceptions.EmptyArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field="commit message"))


def main(constants: SCCSConstants, Repo: RepositoryLayout, commit_message: str) -> None:
    """Run functions for the <sccs commit> command."""
    Repo.check_repository_layout()

    validate_commit_message(constants, commit_message)

    sha_hash = Repo.commit_changes(commit_message)

    print_commit_confirmation_message(constants, Repo, sha_hash)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        Repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(constants, Repository, utils.entered_argument(2))

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
