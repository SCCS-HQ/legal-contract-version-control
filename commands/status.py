import hashlib
import json
import os
import sys
from pathlib import Path

import utils


def get_latest_commit_hash_file(current_branch, cwd=None):
    if cwd is None:
        cwd = utils.working_directory_path
    # get the latest commit filename hash from commit history
    history_path = os.path.join(
        cwd, ".sccs", "branches", current_branch, "history", "commit_history.json"
    )
    if not Path(history_path).is_file():
        print(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )
        sys.exit(1)

    try:
        with open(history_path, "r", encoding="utf-8", newline="\n") as history_file:
            history = json.load(history_file)
            latest_commit_hash = history["history"]["latest_commit"]

    except Exception as e:
        print(f"Error loading history file: {e}")
        sys.exit(1)

    if not latest_commit_hash:
        print(
            "History file is missing the latest commit information. Please "
            "reinitialize SCCS for this file."
        )
        sys.exit(1)

    return latest_commit_hash


def get_latest_commit_file_binary_hash(current_branch=None, cwd=None):
    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch is None:
        current_branch = utils.get_current_branch()
    # get the hash of the latest committed file
    latest_commit_hash = get_latest_commit_hash_file(current_branch, cwd=cwd)
    latest_commit_file_hash_path = os.path.join(
        cwd,
        ".sccs",
        "branches",
        current_branch,
        "commit_file_hash",
        "commit_file_hash.json",
    )
    if not Path(latest_commit_file_hash_path).is_file():
        print(
            "Latest commit file hash not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )
        sys.exit(1)

    try:
        with open(
            latest_commit_file_hash_path, "r", encoding="utf-8", newline="\n"
        ) as f:
            commit_file_hash_data = json.load(f)
            latest_commit_file_hash = commit_file_hash_data.get(latest_commit_hash)

        if not latest_commit_file_hash:
            print(
                "Latest commit file hash is missing from JSON. Please run 'sccs init "
                "<file_path>' to initialize SCCS for this file."
            )
            sys.exit(1)
    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        print(f"Error reading latest commit file hash: {e}")
        sys.exit(1)

    return latest_commit_file_hash


def compare_hashes(old_hash, new_hash):
    return old_hash == new_hash


def print_changes_message_and_exit(old_hash, new_hash):
    if compare_hashes(old_hash, new_hash):
        print("No changes detected since the latest commit. Nothing to commit.")
        sys.exit(0)
    else:
        print(
            "Changes detected since the latest commit. You can proceed with committing "
            "these changes."
        )
        sys.exit(1)


if __name__ == "__main__":
    utils.check_sccs_layout()
    print_changes_message_and_exit(
        get_latest_commit_file_binary_hash(), utils.hash_current_docx_binary()
    )
