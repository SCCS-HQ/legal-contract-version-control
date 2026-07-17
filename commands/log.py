#!/usr/bin/env python3
"""Print a list of past commits for the current branch."""

import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def print_log(constants: SCCSConstants, history_data: dict) -> None:
    """
    Read the commit log data by calling 'get_log_data'.

    Print the first 10 characters of the commit SHA hash, along with the commit author,
    timestamp, and commit message.
    """

    for i in history_data[constants.LOG_DICT_KEY]:
        print(
            constants.LOG_SEPARATOR,
            constants.LOG_COMMIT_FILE_LABEL + i[:constants.COMMIT_HASH_DISPLAY_LENGTH],
            constants.LOG_AUTHOR_LABEL + history_data[constants.LOG_DICT_KEY][i][constants.AUTHOR_DICT_KEY],
            constants.LOG_DATE_LABEL + history_data[constants.LOG_DICT_KEY][i][constants.TIMESTAMP_DICT_KEY],
            constants.LOG_MESSAGE_LABEL + history_data[constants.LOG_DICT_KEY][i][constants.MESSAGE_DICT_KEY],
            constants.LOG_SEPARATOR,
        )


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Run functions for the <sccs log> command."""
    repo.check_repository_layout()

    print_log(constants, repo.current_branch().history_data())


if __name__ == "__main__":
    utils.run_command(main)
