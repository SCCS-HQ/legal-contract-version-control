import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import utils


def get_key_from_config(key, cwd=None):
    """Retrieve the value for a given key from the SCCS configuration file."""

    if cwd is None:
        cwd = utils.working_directory_path
    # Get name and email entered on init
    config_path = os.path.join(cwd, ".sccs", "config", "config.json")

    if not Path(config_path).is_file():
        print(
            "Configuration file not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8", newline="\n") as config_file:
        config = json.load(config_file)
        value = config.get(key)
    return value


def get_commit_message():
    """Retrieve the commit message from the user."""

    commit_message = input("Enter commit message: ").strip()

    if commit_message == "":
        print("Commit message cannot be empty.")
        sys.exit(1)
    return commit_message


def get_timestamp():
    """Retrieve the current timestamp."""

    return datetime.now().isoformat()


def get_history_path(cwd=None, current_branch=None):
    """Retrieve the path to the commit history file."""

    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch is None:
        current_branch = utils.get_current_branch()
    return os.path.join(
        cwd, ".sccs", "branches", current_branch, "history", "commit_history.json"
    )


def get_commit_history():
    """Retrieve the commit history from the commit history file."""

    history_path = get_history_path()
    if not Path(history_path).is_file():
        print(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )
        sys.exit(1)

    try:
        with open(history_path, "r", encoding="utf-8", newline="\n") as history_file:
            history = json.load(history_file)

    except Exception as e:
        print(f"Error retrieving JSON from history file: {e}")
        sys.exit(1)

    return history


def get_parent_hash(history):
    """Retrieve the parent hash from the commit history."""

    parent_hash = history["history"].get("latest_commit")
    return parent_hash


def generate_commit_hash(timestamp, commit_message, name, email, parent_hash):
    """Generate a SHA-256 hash for the commit."""

    return hashlib.sha256(
        f"{timestamp}/{commit_message}/{name}/{email}/{parent_hash}".encode()
    ).hexdigest()


def copy_docx_to_objects(sha_hash, docx_path=None, cwd=None):
    """Copy the current document to the objects directory."""

    if docx_path is None:
        docx_path = utils.current_file_docx_path
    if cwd is None:
        cwd = utils.working_directory_path
    shutil.copy2(
        os.path.join(cwd, Path(docx_path).name),
        os.path.join(cwd, ".sccs", "objects", "docx", f"{sha_hash}.docx"),
    )


def write_diff_html(sha_hash, docx_html, cwd=None, styles=None):
    """Write the diff HTML file."""

    if cwd is None:
        cwd = utils.working_directory_path
    if styles is None:
        styles = utils.default_html_styles
    with open(
        os.path.join(cwd, ".sccs", "objects", "html", f"{sha_hash}.html"),
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(styles + docx_html)


def write_view_html(sha_hash, docx_html, cwd=None):
    """Write the view HTML file."""

    if cwd is None:
        cwd = utils.working_directory_path
    with open(
        os.path.join(cwd, ".sccs", "objects", "view_html", f"{sha_hash}.html"),
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(utils.wrap_html(docx_html))


def update_commit_log_history(
    history, sha_hash, timestamp, name, email, commit_message
):
    """Update the commit log history."""

    # Check if history file exists
    commit_history_path = get_history_path()
    if not os.path.isfile(commit_history_path):
        print(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )
        sys.exit(1)

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


def update_commit_messages(sha_hash, commit_message, cwd=None):
    """Update commit messages."""

    # Check if commit messages file exists
    if cwd is None:
        cwd = utils.working_directory_path
    commit_messages_path = os.path.join(
        cwd, ".sccs", "commit_messages", "commit_messages.json"
    )

    if not Path(commit_messages_path).is_file():
        print(
            "Commit messages file not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )
        sys.exit(1)

    with open(
        commit_messages_path, "r", encoding="utf-8", newline="\n"
    ) as commit_messages_file:
        try:
            messages = json.load(commit_messages_file)
        except Exception as e:
            print(f"Error reading commit messages: {e}")
            sys.exit(1)

    messages[f"{sha_hash}"] = f"{commit_message}"

    return {commit_messages_path: messages}


def update_commit_binary_hash_history(
    sha_hash, hash_docx_binary, cwd=None, current_branch=None
):
    """Update commit binary hash history."""

    # Update commit file hash
    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch is None:
        current_branch = utils.get_current_branch()

    commit_file_hash_path = os.path.join(
        cwd,
        ".sccs",
        "branches",
        current_branch,
        "commit_file_hash",
        "commit_file_hash.json",
    )
    if not Path(commit_file_hash_path).is_file():
        print(
            "Commit file hash not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )
        sys.exit(1)

    try:
        with open(commit_file_hash_path, "r", encoding="utf-8", newline="\n") as f:
            commit_file_hash = json.load(f)

    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        print(f"Error loading commit file hash: {e}")
        sys.exit(1)
    commit_file_hash[f"{sha_hash}"] = hash_docx_binary

    return {commit_file_hash_path: commit_file_hash}


def combine_update_dicts(*dicts):
    """Combine multiple update dictionaries into a single dictionary."""

    update_dict = {}
    for d in dicts:
        update_dict.update(d)
    return update_dict


def atomically_update_history(update_dict):
    """Atomically update the history files."""

    for key, value in update_dict.items():
        try:
            with open(
                f"{Path(key).with_suffix('.tmp')}", "w", encoding="utf-8", newline="\n"
            ) as f:
                json.dump(value, f)
        except Exception as e:
            print(f"Error opening temporary file: {e}")
            sys.exit(1)
    for key, value in update_dict.items():
        try:
            os.replace(f"{Path(key).with_suffix('.tmp')}", f"{Path(key)}")
        except Exception as e:
            print(f"Error replacing temporary file: {e}")
            sys.exit(1)


def print_commit_confirmation_message(sha_hash):
    """Print a confirmation message for the commit."""

    print(f"Commit {sha_hash} created successfully.")


if __name__ == "__main__":
    utils.check_sccs_layout()

    name = get_key_from_config("name")

    email = get_key_from_config("email")

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
