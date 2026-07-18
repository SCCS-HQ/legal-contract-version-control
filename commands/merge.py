#!/usr/bin/env python3
"""Merge branches in the SCCS repository."""

import shutil

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import RepositoryLayout


def validate_branch(c: SCCSConstants, repo: RepositoryLayout, branch: str) -> None:
    """Validate that the entered branch is valid, exists, and is not the current branch."""

    if not branch:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )
    if branch == repo.current_branch_name():
        raise exceptions.InvalidArgumentError(
            c.CURRENT_BRANCH_MERGE_ERROR_MESSAGE
        )
    if branch not in repo.list_branches():
        raise exceptions.BranchNotFoundError(c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch))


def copy_branch_data(repo: RepositoryLayout, branch: str) -> None:
    """Copy the data from the source branch to the target branch."""

    try:
        shutil.copytree(repo.branch_path(branch), repo.branch_path(repo.current_branch_name()), dirs_exist_ok=True)
    except Exception as e:
        raise exceptions.FileCopyError


def copy_repo_document(c: SCCSConstants, repo: RepositoryLayout, branch: str) -> None:
    """Copy the repo document from the source branch to the target branch."""

    try:
        shutil.copy2(
            repo.branch(branch).latest_commit_path(c.DOCX_DIR),
            repo.document_path()
        )
    except Exception as e:
        raise exceptions.FileCopyError from e


def print_merge_success_message(c: SCCSConstants, repo: RepositoryLayout, branch: str) -> None:
    """Print a success message after merging the branches."""
    print(
        c.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(branch=branch, current_branch=repo.current_branch_name())
    )


def main(c: SCCSConstants, repo: RepositoryLayout, branch: str) -> None:
    """Merge the entered branch into the current branch."""

    repo.check_repository_layout()

    repo.check_for_uncommitted_changes()

    validate_branch(c, repo, branch)
    copy_repo_document(c, repo, branch)
    copy_branch_data(repo, branch)

    repo.commit_changes(
        c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(branch=branch, current_branch=repo.current_branch_name())
    )

    print_merge_success_message(c, repo, branch)


if __name__ == "__main__":
    utils.run_command(main, 2)