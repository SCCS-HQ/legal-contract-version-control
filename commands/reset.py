#!/usr/bin/env python3
"""Delete all uncommitted changes."""

import shutil

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def reset(c: SCCSConstants, repo: RepositoryLayout) -> None:
    """Delete all uncommitted changes."""

    try:
        shutil.copy2(
            repo.current_branch().latest_commit_path(c.DOCX_DIR),
            repo.document_path(),
        )
    except Exception as e:
        raise exceptions.FileCopyError(c.RESET_ERROR_MESSAGE) from e
        

def print_success_message(c: SCCSConstants) -> None:
    """Print a success message after resetting the document."""
    print(
        c.RESET_SUCCESS_MESSAGE
    )


def main(c: SCCSConstants, repo: RepositoryLayout) -> None:
    """Main function to handle the <reset> command."""
    repo.check_repository_layout()

    reset(c, repo)
    print_success_message(c)


if __name__ == "__main__":
    utils.run_command(main)
