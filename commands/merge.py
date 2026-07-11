#!/usr/bin/env python3
"""Merge branches in the SCCS repository."""

import shutil
import sys
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants, ErrorWrappers
from repository_layout import RepositoryLayout


def validate_branch(constants: SCCSConstants, Repo: RepositoryLayout, branch: str) -> None:
    """Validate that the entered branch is valid, exists, and is not the current branch."""

    if not branch:
        raise exceptions.InvalidArgumentError(
            constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.BRANCH_NAME_FIELD_NAME)
        )
    if branch == Repo.current_branch_name():
        raise exceptions.InvalidArgumentError(
            constants.CURRENT_BRANCH_MERGE_ERROR_MESSAGE
        )
    if branch not in Repo.list_branches():
        raise exceptions.BranchNotFoundError(constants.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch))


def copy_branch_data(Repo: RepositoryLayout, branch: str) -> None:
    """Copy the data from the source branch to the target branch."""

    try:
        shutil.copytree(Repo.branch_path(branch), Repo.branch_path(Repo.current_branch_name()), dirs_exist_ok=True)
    except Exception as e:
        raise exceptions.FileCopyError


def copy_repo_document(constants: SCCSConstants, Repo: RepositoryLayout, branch: str) -> None:
    """Copy the repo document from the source branch to the target branch."""

    try:
        shutil.copy2(
            Repo.branch(branch).latest_commit_path(constants.DOCX_DIR),
            Repo.document_path()
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_merge_success_message(constants: SCCSConstants, Repo: RepositoryLayout, branch: str) -> None:
    """Print a success message after merging the branches."""
    print(
        constants.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(branch=branch, current_branch=Repo.current_branch_name())
    )


def main(constants: SCCSConstants, Repo: RepositoryLayout, branch: str | None = None) -> None:
    """Merge the entered branch into the current branch."""

    Repo.check_repository_layout()

    Repo.check_for_uncommitted_changes()

    validate_branch(constants, Repo, branch)
    copy_repo_document(Repo, branch)
    copy_branch_data(Repo, branch)

    Repo.commit_changes(
        constants.MERGE_COMMIT_MESSAGE_TEMPLATE.format(branch=branch, current_branch=Repo.current_branch_name())
    )

    print_merge_success_message(constants, Repo, branch)

RepositoryLayout.latest_commit_path()

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