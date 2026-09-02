#!/usr/bin/env python3

from pathlib import Path
from typing import Any

import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryIO,
    RepositoryStatus,
)


def print_log(c: SCCSConstants, log_data: dict[str, Any]) -> None:

    for i in log_data:
        print(
            c.LOG_SEPARATOR + c.NEWLINE,
            c.LOG_COMMIT_FILE_LABEL
            + i[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
            + c.NEWLINE,
            (
                c.LOG_AUTHOR_LABEL
                + log_data[i][c.AUTHOR_DICT_KEY]
                + c.NEWLINE
            ),
            (
                c.LOG_DATE_LABEL
                + log_data[i][c.TIMESTAMP_DICT_KEY]
                + c.NEWLINE
            ),
            (
                c.LOG_MESSAGE_LABEL
                + log_data[i][c.MESSAGE_DICT_KEY]
                + c.NEWLINE
            ),
            c.LOG_SEPARATOR,
            sep="",
        )


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    ri: RepositoryIO,
    rs: RepositoryStatus,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    print_log(c, ri.read_log())

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryIO(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
    )
