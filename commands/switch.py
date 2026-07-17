#!/usr/bin/env python3
"""Switch between document branches."""

import shutil

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def check_branch_to_switch(c: SCCSConstants, repo: RepositoryLayout, branch_to_switch: str) -> None:
    """Check if the branch to switch to is valid."""

    if not branch_to_switch:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )

    if not repo.branch_exists(branch_to_switch):
        raise exceptions.BranchNotFoundError(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch)
        )


def check_commit(c: SCCSConstants, repo: RepositoryLayout, branch_to_switch: str) -> None:
    """
    Check if the commit object exists in the document history.
    """

    commit = repo.branch(branch_to_switch).latest_commit_path(c.DOCX_DIR)
    
    if not (commit).is_file():
        raise exceptions.CommitNotFoundError


def copy_commit_to_main(c: SCCSConstants, repo: RepositoryLayout, branch_to_switch: str) -> None:
    """Copy the commit file to the main document."""
    try:
        shutil.copy2(
            (repo.branch(branch_to_switch).latest_commit_path(c.DOCX_DIR)),
            (repo.document_path()),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_confirmation(c: SCCSConstants, branch_to_switch: str) -> None:
    """Print a confirmation message for successful branch switch."""

    print(c.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch))


def main(c: SCCSConstants, repo: RepositoryLayout, branch_to_switch: str) -> None:
    """Run functions for the <sccs switch> command."""
    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    check_branch_to_switch(c, repo, branch_to_switch)

    check_commit(c, repo, branch_to_switch)

    copy_commit_to_main(c, repo, branch_to_switch)

    repo.set_current_branch(branch_to_switch)

    print_confirmation(c, branch_to_switch)


if __name__ == "__main__":
    utils.run_command(main, 2)
