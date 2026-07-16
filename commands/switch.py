#!/usr/bin/env python3
"""Switch between document branches."""

import json
import shutil
import sys
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def check_branch_to_switch(constants: SCCSConstants, Repo: RepositoryLayout, branch_to_switch: str) -> None:
    """Check if the branch to switch to is valid."""

    if not branch_to_switch:
        raise exceptions.InvalidArgumentError(
            constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.BRANCH_NAME_FIELD_NAME)
        )

    if not Repo.branch_exists(branch_to_switch):
        raise exceptions.BranchNotFoundError(
            constants.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch)
        )


def check_commit(constants: SCCSConstants, Repo: RepositoryLayout, branch_to_switch: str) -> None:
    """
    Check if the commit object exists in the document history.
    """

    commit = Repo.branch(branch_to_switch).latest_commit_path(constants.DOCX_DIR)
    
    if not (commit).is_file():
        raise exceptions.CommitNotFoundError


def copy_commit_to_main(constants: SCCSConstants, Repo: RepositoryLayout, branch_to_switch: str) -> None:
    """Copy the commit file to the main document."""
    try:
        shutil.copy2(
            (Repo.branch(branch_to_switch).latest_commit_path(constants.DOCX_DIR)),
            (Repo.document_path()),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_confirmation(constants: SCCSConstants, branch_to_switch: str) -> None:
    """Print a confirmation message for successful branch switch."""

    print(constants.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch))


def main(constants: SCCSConstants, Repo: RepositoryLayout, branch_to_switch: str) -> None:
    """Run functions for the <sccs switch> command."""
    Repo.check_repository_layout()

    Repo.check_for_uncommitted_changes()

    check_branch_to_switch(constants, Repo, branch_to_switch)

    check_commit(constants, Repo, branch_to_switch)

    copy_commit_to_main(constants, Repo, branch_to_switch)

    Repo.set_current_branch(branch_to_switch)

    print_confirmation(constants, branch_to_switch)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(constants, repository, utils.entered_argument(2))

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
