#!/usr/bin/env python3
"""Print a list of past commits for the current branch."""

from pathlib import Path

import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryIO,
    RepositoryData,
    RepositoryStatus,
    TargetBranch,
)


def print_log(c: SCCSConstants, history_data: dict) -> None:
    """
    Read the commit log data by calling 'get_log_data'.

    Print the first 10 characters of the commit SHA hash, along with the commit author,
    timestamp, and commit message.
    """

    for i in history_data[c.LOG_DICT_KEY]:
        print(
            c.LOG_SEPARATOR,
            c.LOG_COMMIT_FILE_LABEL + i[:c.COMMIT_HASH_DISPLAY_LENGTH],
            c.LOG_AUTHOR_LABEL + history_data[c.LOG_DICT_KEY][i][c.AUTHOR_DICT_KEY],
            c.LOG_DATE_LABEL + history_data[c.LOG_DICT_KEY][i][c.TIMESTAMP_DICT_KEY],
            c.LOG_MESSAGE_LABEL + history_data[c.LOG_DICT_KEY][i][c.MESSAGE_DICT_KEY],
            c.LOG_SEPARATOR,
        )


def main(c: SCCSConstants, rd: RepositoryData, rs: RepositoryStatus, ri: RepositoryIO) -> None:
    """Run functions for the <sccs log> command."""
    rs.check_repository_layout()

    ri.target.set(rd.current_branch())

    print_log(c, ri.read_history())


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryIO(Path.cwd(), c, target),
    )
