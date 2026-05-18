#!/usr/bin/env python3
"""Initialize a document with SCCS."""

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import exceptions
import utils


def get_entered_document_path() -> Path | None:
    """Retrieve the document path entered by the user."""

    return Path(sys.argv[2]) if len(sys.argv) > 2 else None


def get_document_repo_path() -> Path | None:
    """Return the repo directory path derived from the entered document path."""

    path = get_entered_document_path()
    if not path:
        return None
    return Path(path).with_suffix("")


def check_if_arg_entered(arg: Path) -> None:
    """Check that a file path argument was provided."""

    if not arg:
        raise exceptions.InvalidArgumentError("No file path provided.")


def ask_config_input(data: str) -> str:
    """Prompt the user for a config value and return it."""

    data_value = input(f"Enter your {data}: ").strip()
    if data_value == "":
        raise exceptions.InvalidInputError(f"{data} cannot be empty.")
    else:
        return data_value


def check_for_prev_init() -> None:
    """Exit if the document has already been initialized with SCCS."""

    if (get_document_repo_path() / ".sccs").is_dir():
        raise exceptions.AlreadyInitializedError(
            "This file has already been initialized with SCCS."
        )


def check_file_requirements() -> None:
    """Validate that the entered path points to an existing .docx file."""

    entered_path = get_entered_document_path()
    if not entered_path:
        raise exceptions.InvalidArgumentError("No file path provided.")

    if Path(entered_path).suffix.lower() != ".docx":
        raise exceptions.InvalidFileTypeError(
            "File is not a .docx file. Please provide a valid .docx file."
        )
    if not Path(entered_path).is_file():
        raise FileNotFoundError("File does not exist.")


def create_commit_sha_hash(timestamp: str, user_name: str, user_email: str) -> str:
    """Create a SHA-256 hash for the initial commit."""

    return hashlib.sha256(
        f"{timestamp}/initial_version/{user_name}/{user_email}".encode()
    ).hexdigest()


def create_sccs_directory_layout() -> None:
    """Create the full SCCS directory structure inside the repo path."""

    repo_path = get_document_repo_path()
    if not repo_path:
        raise exceptions.InvalidArgumentError("No file path provided.")

    repo_path.mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "objects").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "objects" / "docx").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "objects" / "html").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "objects" / "view_html").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "branches").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "branches" / "main").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "branches" / "main" / "history").mkdir(
        parents=True, exist_ok=True
    )
    (repo_path / ".sccs" / "commit_messages").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "config").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "current_branch").mkdir(parents=True, exist_ok=True)
    (repo_path / ".sccs" / "branches" / "main" / "commit_file_hash").mkdir(
        parents=True, exist_ok=True
    )


def move_document_to_repo_directory() -> None:
    """Move the source document into the repo directory."""

    shutil.move(get_entered_document_path(), get_document_repo_path())


def copy_document_to_objects_as_docx_and_html(
    sha_hash: str, html: str, styles: str | None = None
) -> None:
    """Copy the document into objects as both .docx and .html."""

    if styles is None:
        styles = utils.default_html_styles

    repo_path = get_document_repo_path()
    doc_name = Path(get_entered_document_path()).name

    try:
        shutil.copy2(
            (repo_path / doc_name),
            (repo_path / ".sccs" / "objects" / "docx" / f"{sha_hash}.docx"),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e

    try:
        with open(
            (repo_path / ".sccs" / "objects" / "html" / f"{sha_hash}.html"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(styles + html)
    except Exception as e:
        raise exceptions.FileWriteError from e

    try:
        with open(
            (repo_path / ".sccs" / "objects" / "view_html" / f"{sha_hash}.html"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(utils.wrap_html(html))
    except Exception as e:
        raise exceptions.FileWriteError from e


def get_current_iso_time() -> str:
    """Return the current time as an ISO 8601 string."""

    return datetime.now().isoformat()


def write_history_data(
    sha_hash: str, config_user_name: str, config_user_email: str
) -> None:
    """Write the initial commit history JSON file."""

    history_data = {
        "history": {
            "initial_commit": f"{sha_hash}",
            "latest_commit": f"{sha_hash}",
            "latest_commit_number": 1,
            "commit_order": {"1": f"{sha_hash}"},
        },
        "log": {
            f"{sha_hash}": {
                "timestamp": get_current_iso_time(),
                "author": f"{config_user_name} <{config_user_email}>",
                "message": "initial commit (This is a default commit message for "
                "initial version)",
            }
        },
    }
    try:
        with open(
            (
                get_document_repo_path()
                / ".sccs"
                / "branches"
                / "main"
                / "history"
                / "commit_history.json"
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_commit_message_data(sha_hash: str) -> None:
    """Write the initial commit message JSON file."""

    commit_message_data = {
        f"{sha_hash}": "initial commit (This is a default commit message for initial "
        "version)"
    }
    try:
        with open(
            (
                get_document_repo_path()
                / ".sccs"
                / "commit_messages"
                / "commit_messages.json"
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_message_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_config_data(config_user_name: str, config_user_email: str) -> None:
    """Write the user config JSON file."""

    config_data = {"name": f"{config_user_name}", "email": f"{config_user_email}"}
    try:
        with open(
            (get_document_repo_path() / ".sccs" / "config" / "config.json"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def write_hashed_file_commit_data(sha_hash: str, hashed_file: str) -> None:
    """Write the initial commit file binary hash JSON file."""

    commit_file_hash_data = {f"{sha_hash}": hashed_file}
    try:
        with open(
            (
                get_document_repo_path()
                / ".sccs"
                / "branches"
                / "main"
                / "commit_file_hash"
                / "commit_file_hash.json"
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_file_hash_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def write_branch_data() -> None:
    """Write the initial branch tracking JSON file."""

    branches_data = {"current_branch": "main", "branches": ["main"]}
    try:
        with open(
            (
                get_document_repo_path()
                / ".sccs"
                / "current_branch"
                / "current_branch.json"
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(branches_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def confirmation_message() -> None:
    """Print a confirmation message for successful SCCS initialization."""

    print("SCCS initialization complete.")


def main() -> None:
    """Run functions for the <sccs init> command."""

    check_if_arg_entered(get_entered_document_path())

    check_for_prev_init()

    check_file_requirements()

    config_user_name = ask_config_input("name")

    config_user_email = ask_config_input("email")

    current_iso_time = get_current_iso_time()

    sha_hash = create_commit_sha_hash(
        current_iso_time, config_user_name, config_user_email
    )

    create_sccs_directory_layout()

    document_as_html = utils.convert_docx_to_html(get_entered_document_path())

    move_document_to_repo_directory()

    copy_document_to_objects_as_docx_and_html(sha_hash, document_as_html)

    write_history_data(sha_hash, config_user_name, config_user_email)

    write_commit_message_data(sha_hash)

    write_config_data(config_user_name, config_user_email)

    current_branch_binary_hash = utils.hash_current_docx_binary(
        docx_path=get_document_repo_path() / Path(get_entered_document_path()).name
    )

    write_hashed_file_commit_data(sha_hash, current_branch_binary_hash)

    write_branch_data()

    confirmation_message()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
