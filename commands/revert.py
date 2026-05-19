from pathlib import Path
import sys
import shutil

import exceptions
import utils

def get_entered_commit() -> Path | None:
    """Retrieve the commit file path entered by the user."""

    return Path(sys.argv[2]) if len(sys.argv) > 2 else None


def validate_commit(cwd: Path | None = None, commit: Path | None = None) -> Path | None:
    """Validate the commit file path entered by the user."""

    if cwd is None:
        cwd = utils.working_directory_path

    if commit is None:
        raise exceptions.InvalidArgumentError(
            "No commit file path provided. Please specify a commit file path."
        )
    
    commit = commit.with_suffix(".docx")

    commit = Path(cwd / ".sccs" / "objects" / "docx" / commit)

    if not commit.is_file():
        raise exceptions.InvalidArgumentError(
            f"Commit file '{commit}' does not exist. Please provide a valid commit file"
            f" path."
        )

    return commit


def revert(src: Path, dst: Path | None = None) -> None:
    """Revert the current document to the specified commit."""
    
    if not src.is_file():
        raise exceptions.InvalidArgumentError(f"Source file '{src}' does not exist.")
    
    if dst is None:
        dst = utils.current_file_docx_path

    if not dst.is_file():
        raise exceptions.InvalidArgumentError(
            f"Destination file '{dst}' does not exist."
        )

    shutil.copy(src, dst)
    print_revert_confirmation_message(src)


def print_revert_confirmation_message(commit: Path) -> None:
    """Print a confirmation message for the revert."""

    print(f"Document successfully reverted to commit '{commit.name}'.")


def main() -> None:
    """Main function to handle the revert command."""
    utils.check_sccs_layout()
    
    cwd = utils.working_directory_path
    commit = get_entered_commit()
    validated_commit = validate_commit(cwd, commit)
    revert(validated_commit)

    name = utils.get_key_from_config("name")

    email = utils.get_key_from_config("email")

    docx_html = utils.convert_docx_to_html()

    commit_message = f"Revert to commit '{validated_commit.name}'"

    timestamp = utils.get_timestamp()

    history = utils.get_commit_history()

    parent_hash = utils.get_parent_hash()

    sha_hash = utils.generate_commit_hash(
        timestamp, commit_message, name, email, parent_hash
    )

    utils.copy_docx_to_objects(sha_hash)

    utils.write_diff_html(sha_hash, docx_html)

    utils.write_view_html(sha_hash, docx_html)

    updated_commit_log_history = utils.update_commit_log_history(
        history, sha_hash, timestamp, name, email, commit_message
    )

    current_branch_binary_hash = utils.hash_current_docx_binary()

    updated_commit_binary_hash_history = utils.update_commit_binary_hash_history(
        sha_hash, current_branch_binary_hash
    )

    updated_commit_messages = utils.update_commit_messages(sha_hash, commit_message)

    combined_history_update_dicts = utils.combine_update_dicts(
        updated_commit_log_history,
        updated_commit_binary_hash_history,
        updated_commit_messages,
    )

    utils.atomically_update_history(combined_history_update_dicts)

if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
else:
    raise exceptions.FileImportedAsModuleError(
        "This file cannot be run as a module. Please run it as a script."
    )
    
    

    

    