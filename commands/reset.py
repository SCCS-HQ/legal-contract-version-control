#!/usr/bin/env python3

from pathlib import Path
import shutil

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    TargetBranch,
)


def reset(
    c: SCCSConstants, rd: RepositoryData, rp: RepositoryPaths, rs: RepositoryStatus
) -> None:

    rs.target.set(rd.current_branch())

    try:
        shutil.copy2(
            rd.hash_to_full_path(rd.latest_commit(), c.DOCX_DIR),
            rp.document_path(),
        )
    except Exception as e:
        raise exceptions.FileCopyError(c.RESET_ERROR_MESSAGE) from e

    rs.target.reset()

def print_success_message(c: SCCSConstants) -> None:
    print(c.RESET_SUCCESS_MESSAGE)


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    reset(c, rd, rp, rs)
    print_success_message(c)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
    )
