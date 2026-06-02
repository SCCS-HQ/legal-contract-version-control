import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def validate_branch(branch: str | None, current_branch: str, branches: list) -> str:
    """Validate that the entered branch is valid, exists, and is not the current branch."""
    if branch is None:
        raise exceptions.InvalidArgumentError(
            "No branch provided. Please provide a branch to merge."
        )
    if branch == current_branch:
        raise exceptions.InvalidArgumentError(
            "Cannot merge the current branch into itself."
        )
    if branch not in branches:
        raise exceptions.BranchNotFoundError(f"Branch '{branch}' does not exist.")
    return branch


def copy_branch_data(
    current_branch: str, target_branch: str, cwd: Path | None = None
) -> None:
    """Copy the data from the source branch to the target branch."""
    if cwd is None:
        cwd = Path.cwd()

    current_branch_path = cwd / ".sccs" / "branches" / current_branch
    target_branch_path = cwd / ".sccs" / "branches" / target_branch

    shutil.copytree(target_branch_path, current_branch_path, dirs_exist_ok=True)


def copy_repo_document(target_branch: str, cwd: Path | None = None) -> None:
    """Copy the repo document from the source branch to the target branch."""
    if cwd is None:
        cwd = Path.cwd()

    target_repo_doc_path = (
        cwd
        / ".sccs"
        / "objects"
        / "docx"
        / f"{utils.get_latest_commit(target_branch)}.docx"
    )
    current_repo_doc_path = utils.current_file_docx_path

    shutil.copy2(target_repo_doc_path, current_repo_doc_path)


def print_merge_success_message(source_branch: str, target_branch: str) -> None:
    """Print a success message after merging the branches."""
    print(
        f"Successfully merged branch '{source_branch}' into branch '{target_branch}'."
    )


def main() -> None:
    """Merge the entered branch into the current branch."""
    utils.check_sccs_layout()

    utils.check_for_uncommitted_changes("merge")

    current_branch = utils.get_current_branch()
    entered_branch = utils.entered_arguement(2)
    branches = utils.get_branch_data(key="branches")
    branch_to_merge = validate_branch(entered_branch, current_branch, branches)
    copy_repo_document(branch_to_merge)
    copy_branch_data(current_branch, branch_to_merge)

    utils.commit_changes(f'Merged branch "{branch_to_merge}" into "{current_branch}".')

    print_merge_success_message(branch_to_merge, current_branch)


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
