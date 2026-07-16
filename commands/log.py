#!/usr/bin/env python3
"""Print a list of past commits for the current branch."""

import json
import sys
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def print_log(constants: SCCSConstants, history_data: dict) -> None:
    """
    Read the commit log data by calling 'get_log_data'.

    Print the first 10 characters of the commit SHA hash, along with the commit author,
    timestamp, and commit message.
    """

    for i in history_data[constants.LOG_DICT_KEY]:
        print(
            f"{constants.LOG_SEPARATOR}\n"
            f"{constants.LOG_COMMIT_FILE_LABEL}{i[:constants.COMMIT_HASH_DISPLAY_LENGTH]}\n"
            f"{constants.LOG_AUTHOR_LABEL}{history_data[constants.LOG_DICT_KEY][i][constants.AUTHOR_DICT_KEY]}\n"
            f"{constants.LOG_DATE_LABEL}{history_data[constants.LOG_DICT_KEY][i][constants.TIMESTAMP_DICT_KEY]}\n"
            f"{constants.LOG_MESSAGE_LABEL}{history_data[constants.LOG_DICT_KEY][i][constants.MESSAGE_DICT_KEY]}\n"
            f"{constants.LOG_SEPARATOR}"
        )


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs log> command."""
    repo.check_repository_layout()

    print_log(constants, repo.current_branch().history_data())


if __name__ == "__main__":
    try:
        constants = SCCSConstants
        repository = RepositoryLayout(Path.cwd, constants)
        error_wrappers = ErrorWrappers()
        main(constants, repository)

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
