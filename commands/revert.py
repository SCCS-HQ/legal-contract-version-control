import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def revert() -> None:
    """Revert the current document to the specified commit by copying 'src' to 'dst'."""

    src = utils.validate_commit("docx", commit=utils.entered_arguement(2))

    if not src.is_file():
        raise exceptions.InvalidArgumentError(
            f"Source file '{src.stem}' does not exist."
        )


    shutil.copy2(src, utils.current_file_docx_path)


def print_revert_confirmation_message() -> None:
    """Print a confirmation message for the revert."""

    validated_commit = utils.validate_commit("docx", commit=utils.entered_arguement(2))

    print(
        f"Document successfully reverted to commit '{validated_commit.stem[:10]}' on commit "
        f"'{utils.commit_changes(
        f"Revert to commit '{validated_commit.stem}'")[:10]}'.\n"
    )


def main() -> None:
    """Main function to handle the revert command."""
    utils.check_sccs_layout()

    utils.check_for_uncommitted_changes("revert")

    revert()

    print_revert_confirmation_message()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
