#!/usr/bin/env python3
"""Commit latest changes to the current branch."""

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import exceptions
import utils


def get_commit_message() -> str:
    """Retrieve the commit message from the user."""

    commit_message = input("Enter commit message: ").strip()

    if commit_message == "":
        raise exceptions.EmptyCommitMessageError("Commit message cannot be empty.")

    return commit_message


def get_timestamp() -> str:
    """Retrieve the current timestamp."""

    return datetime.now().isoformat()


def get_history_path(cwd: Path = None, current_branch: str = None) -> Path:
    """Retrieve the path to the commit history file."""

    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch is None:
        current_branch = utils.get_current_branch()
    return (
        cwd / ".sccs" / "branches" / current_branch / "history" / "commit_history.json"
    )


def get_commit_history() -> dict:
    """Retrieve the commit history from the commit history file."""

    history_path = get_history_path()
    if not history_path.is_file():
        raise FileNotFoundError(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )

    try:
        with open(history_path, "r", encoding="utf-8", newline="\n") as history_file:
            history = json.load(history_file)

    except Exception as e:
        raise exceptions.FileOpenError from e

    return history


def get_parent_hash(history: dict) -> str:
    """Retrieve the parent hash from the commit history."""

    parent_hash = history["history"].get("latest_commit")
    return parent_hash


def generate_commit_hash(
    timestamp: str, commit_message: str, name: str, email: str, parent_hash: str
) -> str:
    """Generate a SHA-256 hash for the commit."""

    return hashlib.sha256(
        f"{timestamp}/{commit_message}/{name}/{email}/{parent_hash}".encode()
    ).hexdigest()


def copy_docx_to_objects(
    sha_hash: str, docx_path: Path = None, cwd: Path = None
) -> None:
    """Copy the current document to the objects directory."""

    if docx_path is None:
        docx_path = utils.current_file_docx_path
    if cwd is None:
        cwd = utils.working_directory_path
    shutil.copy2(
        cwd / docx_path.name,
        cwd / ".sccs" / "objects" / "docx" / f"{sha_hash}.docx",
    )


def write_diff_html(
    sha_hash: str, docx_html: str, cwd: Path = None, styles: str = None
) -> None:
    """Write the diff HTML file."""

    if cwd is None:
        cwd = utils.working_directory_path
    if styles is None:
        styles = utils.default_html_styles
    with open(
        cwd / ".sccs" / "objects" / "html" / f"{sha_hash}.html",
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(styles + docx_html)


def write_view_html(sha_hash: str, docx_html: str, cwd: Path = None) -> None:
    """Write the view HTML file."""

    if cwd is None:
        cwd = utils.working_directory_path
    with open(
        cwd / ".sccs" / "objects" / "view_html" / f"{sha_hash}.html",
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(utils.wrap_html(docx_html))


def update_commit_log_history(
    history: dict,
    sha_hash: str,
    timestamp: str,
    name: str,
    email: str,
    commit_message: str,
) -> dict[str, dict]:
    """Update the commit log history."""

    # Check if history file exists
    commit_history_path = get_history_path()
    if not commit_history_path.is_file():
        raise FileNotFoundError(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )

    # Update history
    history["history"]["latest_commit"] = f"{sha_hash}"
    history["history"]["latest_commit_number"] = (
        history["history"].get("latest_commit_number", 0) + 1
    )

    latest_commit_number = history["history"]["latest_commit_number"]

    history["history"]["commit_order"][str(latest_commit_number)] = f"{sha_hash}"

    history["log"][f"{sha_hash}"] = {
        "timestamp": timestamp,
        "author": f"{name} <{email}>",
        "message": commit_message,
    }
    return {commit_history_path: history}


def update_commit_messages(
    sha_hash: str, commit_message: str, cwd: Path = None
) -> dict[str, dict]:
    """Update commit messages."""

    # Check if commit messages file exists
    if cwd is None:
        cwd = utils.working_directory_path
    commit_messages_path = cwd / ".sccs" / "commit_messages" / "commit_messages.json"

    if not commit_messages_path.is_file():
        raise FileNotFoundError(
            "Commit messages file not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    with open(
        commit_messages_path, "r", encoding="utf-8", newline="\n"
    ) as commit_messages_file:
        try:
            messages = json.load(commit_messages_file)
        except Exception as e:
            raise exceptions.FileOpenError from e

    messages[f"{sha_hash}"] = f"{commit_message}"

    return {commit_messages_path: messages}


def update_commit_binary_hash_history(
    sha_hash: str, hash_docx_binary: str, cwd: Path = None, current_branch: str = None
) -> dict[str, dict]:
    """Update commit binary hash history."""

    # Update commit file hash
    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch is None:
        current_branch = utils.get_current_branch()

    commit_file_hash_path = (
        cwd
        / ".sccs"
        / "branches"
        / current_branch
        / "commit_file_hash"
        / "commit_file_hash.json"
    )
    if not commit_file_hash_path.is_file():
        raise FileNotFoundError(
            "Commit file hash not found. Please run 'sccs init <file_path>' to "
            f"initialize SCCS for this file."
        )

    try:
        with open(commit_file_hash_path, "r", encoding="utf-8", newline="\n") as f:
            commit_file_hash = json.load(f)

    except Exception as e:
        raise exceptions.FileOpenError from e

    commit_file_hash[f"{sha_hash}"] = hash_docx_binary

    return {commit_file_hash_path: commit_file_hash}


def combine_update_dicts(*dicts: dict[Path, dict]) -> dict[Path, dict]:
    """Combine multiple update dictionaries into a single dictionary."""

    update_dict = {}
    for d in dicts:
        update_dict.update(d)
    return update_dict


def atomically_update_history(update_dict: dict[Path, dict]) -> None:
    """Atomically update the history files."""

    for key, value in update_dict.items():
        try:
            with open(
                key.with_suffix(".tmp"), "w", encoding="utf-8", newline="\n"
            ) as f:
                json.dump(value, f)
        except Exception as e:
            raise exceptions.TemporaryFileError from e

    for key, value in update_dict.items():
        try:
            key.with_suffix(".tmp").replace(key)
        except Exception as e:
            raise exceptions.TemporaryFileError from e


def print_commit_confirmation_message(sha_hash: str) -> None:
    """Print a confirmation message for the commit."""

    print(f"Commit {sha_hash} created successfully.")


def main() -> None:
    """Run functions for the <sccs commit> command."""
    utils.check_sccs_layout()

    name = utils.get_key_from_config("name")

    email = utils.get_key_from_config("email")

    docx_html = utils.convert_docx_to_html()

    commit_message = get_commit_message()

    timestamp = get_timestamp()

    history = get_commit_history()

    parent_hash = get_parent_hash(history)

    sha_hash = generate_commit_hash(timestamp, commit_message, name, email, parent_hash)

    copy_docx_to_objects(sha_hash)

    write_diff_html(sha_hash, docx_html)

    write_view_html(sha_hash, docx_html)

    updated_commit_log_history = update_commit_log_history(
        history, sha_hash, timestamp, name, email, commit_message
    )

    current_branch_binary_hash = utils.hash_current_docx_binary()

    updated_commit_binary_hash_history = update_commit_binary_hash_history(
        sha_hash, current_branch_binary_hash
    )

    updated_commit_messages = update_commit_messages(sha_hash, commit_message)

    combined_history_update_dicts = combine_update_dicts(
        updated_commit_log_history,
        updated_commit_binary_hash_history,
        updated_commit_messages,
    )

    atomically_update_history(combined_history_update_dicts)

    print_commit_confirmation_message(sha_hash)


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
