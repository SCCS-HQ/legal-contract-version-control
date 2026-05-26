import shutil
import sys
from pathlib import Path

import exceptions
import utils


def get_entered_commit() -> Path | None:
    """Return the commit file path entered by the user if provided, else None."""

    return Path(sys.argv[2]) if len(sys.argv) > 2 else None


def revert(src: Path, dst: Path | None = None) -> None:
    """Revert the current document to the specified commit by copying 'src' to 'dst'."""

    if not src.is_file():
        raise exceptions.InvalidArgumentError(
            f"Source file '{src.stem}' does not exist."
        )

    if dst is None:
        dst = utils.current_file_docx_path

    shutil.copy2(src, dst)


def print_revert_confirmation_message(commit: Path, new_commit_hash: str) -> None:
    """Print a confirmation message for the revert."""

    print(
        f"Document successfully reverted to commit '{commit.stem}' on commit '{new_commit_hash}'."
    )


def main() -> None:
    """Main function to handle the revert command."""
    utils.check_sccs_layout()

    utils.check_for_uncommitted_changes("revert")

    cwd = utils.working_directory_path
    commit = get_entered_commit()
    validated_commit = utils.validate_commit("docx", cwd, commit)
    revert(validated_commit)

    new_commit_hash = utils.commit_changes(
        f"Revert to commit '{validated_commit.stem}'"
    )

    print_revert_confirmation_message(validated_commit, new_commit_hash)


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
