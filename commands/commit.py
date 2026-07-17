#!/usr/bin/env python3
"""Commit latest changes to the current branch."""

import exceptions
import utils
from repository_layout import RepositoryLayout
from constants_classes import SCCSConstants


def print_commit_confirmation_message(constants: SCCSConstants, repo: RepositoryLayout, sha_hash) -> None:
    """Print a confirmation message for the commit using 'sha_hash'."""

    try:
        print(constants.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(sha_hash=sha_hash[:constants.COMMIT_HASH_DISPLAY_LENGTH]))
    except Exception as e:
        raise exceptions.SCCSException(constants.COMMIT_FAILURE_ERROR_MESSAGE) from e


def validate_commit_message(constants: SCCSConstants, commit_message: str) -> None:

    if commit_message is None or not commit_message.strip():
        raise exceptions.EmptyArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.COMMIT_MESSAGE_FIELD_NAME))


def main(constants: SCCSConstants, repo: RepositoryLayout, commit_message: str) -> None:
    """Run functions for the <sccs commit> command."""
    repo.check_repository_layout()

    validate_commit_message(constants, commit_message)

    sha_hash = repo.commit_changes(commit_message)

    print_commit_confirmation_message(constants, repo, sha_hash)


if __name__ == "__main__":
    utils.run_command(main, 2)
