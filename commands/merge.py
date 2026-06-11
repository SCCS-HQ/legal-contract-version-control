import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def validate_branch() -> str:
    """Validate that the entered branch is valid, exists, and is not the current branch."""

    branch = utils.entered_arguement(2)
    current_branch = Repository.current_branch_name()

    if branch is None:
        raise exceptions.InvalidArgumentError(
            "No branch provided. Please provide a branch to merge."
        )
    if branch == current_branch:
        raise exceptions.InvalidArgumentError(
            "Cannot merge the current branch into itself."
        )
    if branch not in Repository.current_branch_data(key="branches"):
        raise exceptions.BranchNotFoundError(f"Branch '{branch}' does not exist.")
    return branch


def copy_branch_data() -> None:
    """Copy the data from the source branch to the target branch."""
    if cwd is None:
        cwd = Path.cwd()
    

    current_branch_path = cwd / ".sccs" / "branches" / Repository.current_branch_name()
    target_branch_path = cwd / ".sccs" / "branches" / validate_branch()

    shutil.copytree(target_branch_path, current_branch_path, dirs_exist_ok=True)


def copy_repo_document() -> None:
    """Copy the repo document from the source branch to the target branch."""
    if cwd is None:
        cwd = Path.cwd()

    target_repo_doc_path = (
        cwd
        / ".sccs"
        / "objects"
        / "docx"
        / f"{Repository.branch(validate_branch()).latest_commit()}.docx"
    )
    current_repo_doc_path = utils.current_file_docx_path

    shutil.copy2(target_repo_doc_path, current_repo_doc_path)


def print_merge_success_message() -> None:
    """Print a success message after merging the branches."""
    print(
        f"Successfully merged branch '{validate_branch()}' into branch '{Repository.current_branch_name()}'."
    )


def main() -> None:
    """Merge the entered branch into the current branch."""
    Repository.check_repository_layout()

    Repository.check_for_uncommitted_changes("merge")

    copy_repo_document()
    copy_branch_data()

    utils.commit_changes(
        f'Merged branch "{validate_branch()}" into "{Repository.current_branch_name()}".'
    )

    print_merge_success_message()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
