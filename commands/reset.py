#!/usr/bin/env python3
"""Delete all uncommitted changes."""

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryPaths,
    RepositoryData,
    RepositoryStatus,
    TargetBranch,
)


def reset(c: SCCSConstants, rd: RepositoryData, rs: RepositoryStatus, rp: RepositoryPaths) -> None:
    """Delete all uncommitted changes."""

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
    """Print a success message after resetting the document."""
    print(
        c.RESET_SUCCESS_MESSAGE
    )


def main(c: SCCSConstants, rd: RepositoryData, rs: RepositoryStatus, rp: RepositoryPaths) -> None:
    """Main function to handle the <reset> command."""
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    reset(c, rd, rs, rp)
    print_success_message(c)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
    )
