#!/usr/bin/env python3
"""Delete all uncommitted changes."""

import shutil

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def reset(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Delete all uncommitted changes."""

    try:
        shutil.copy2(
            repo.current_branch().latest_commit_path(constants.DOCX_DIR),
            repo.document_path(),
        )
    except Exception as e:
        raise exceptions.FileCopyError(constants.RESET_ERROR_MESSAGE) from e
        

def print_success_message(constants: SCCSConstants) -> None:
    """Print a success message after resetting the document."""
    print(
        constants.RESET_SUCCESS_MESSAGE
    )


def main(constants: SCCSConstants, repo: RepositoryLayout) -> None:
    """Main function to handle the <reset> command."""
    repo.check_repository_layout()

    reset(constants, repo)
    print_success_message(constants)


if __name__ == "__main__":
    utils.run_command(main)
