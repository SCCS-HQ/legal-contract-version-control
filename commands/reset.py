#!/usr/bin/env python3
"""Delete all uncommitted changes."""

import json
import shutil
import sys
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def reset(constants: SCCSConstants, Repo: RepositoryLayout) -> None:
    """Delete all uncommitted changes."""

    try:
        shutil.copy2(
            Repo.current_branch().latest_commit_path(constants.DOCX_DIR),
            Repo.document_path(),
        )
    except Exception as e:
        raise exceptions.FileCopyError(constants.RESET_ERROR_MESSAGE) from e
        

def print_success_message(constants: SCCSConstants) -> None:
    """Print a success message after resetting the document."""
    print(
        constants.RESET_SUCCESS_MESSAGE
    )


def main(constants: SCCSConstants, Repo: RepositoryLayout) -> None:
    """Main function to handle the <reset> command."""
    Repo.check_repository_layout()

    reset(constants, Repo)
    print_success_message(constants)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(constants, repository)
    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)
    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
