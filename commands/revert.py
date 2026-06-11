import shutil
import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def revert() -> None:
    """Revert the current document to the specified commit by copying 'src' to 'dst'."""

    src = Repository.commit_path("docx", commit=utils.entered_arguement(2))

    if not src.is_file():
        raise exceptions.InvalidArgumentError(
            f"Source file '{src.stem}' does not exist."
        )


    shutil.copy2(src, Repository.document_path)


def print_revert_confirmation_message() -> None:
    """Print a confirmation message for the revert."""

    validated_commit = Repository.commit_path("docx", commit=utils.entered_arguement(2))

    print(
        f"Document successfully reverted to commit '{validated_commit.stem[:10]}' on commit "
        f"'{utils.commit_changes(
        f"Revert to commit '{validated_commit.stem}'")[:10]}'.\n"
    )


def main() -> None:
    """Main function to handle the revert command."""
    Repository.check_repository_layout()

    Repository.check_for_uncommitted_changes("revert")

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
