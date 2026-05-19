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

    return sys.argv[2] if len(sys.argv) > 2 else "No commit message provided."


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
