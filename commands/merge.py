import shutil
import sys
from pathlib import Path

import exceptions
import utils


def get_entered_branch() -> str | None:
    """Return the entered branch if provided, else None."""
    return sys.argv[2] if len(sys.argv) > 2 else None


def validate_branch(branch: str | None, current_branch: str) -> str:
    """Validate that the entered branch is not None and that it is not the current branch, and return it."""
    if branch is None:
        raise ValueError("No branch provided. Please provide a branch to merge.")
    if branch == current_branch:
        raise ValueError("Cannot merge the current branch into itself.")
    return branch


def copy_branch_data(
    current_branch: str, target_branch: str, cwd: Path | None = None
) -> None:
    """Copy the data from the source branch to the target branch."""
    if cwd is None:
        cwd = utils.working_directory_path

    current_branch_path = cwd / ".sccs" / "branches" / current_branch
    target_branch_path = cwd / ".sccs" / "branches" / target_branch

    shutil.copytree(current_branch_path, target_branch_path, dirs_exist_ok=True)


def copy_repo_document(target_branch: str, cwd: Path | None = None) -> None:
    """Copy the repo document from the source branch to the target branch."""
    if cwd is None:
        cwd = utils.working_directory_path

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
    current_branch = utils.get_current_branch()
    entered_branch = get_entered_branch()
    branch_to_merge = validate_branch(entered_branch, current_branch)
    copy_repo_document(branch_to_merge)
    copy_branch_data(branch_to_merge, current_branch)
    utils.commit_changes(f"Merged branch '{branch_to_merge}' into '{current_branch}'")
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
