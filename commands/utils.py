#!/usr/bin/env python3
"""Module for utility functions used in SCCS."""

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
import sys

import exceptions
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


default_html_styles = (
    "<style>\n* {\nfont-family: Arial, Helvetica, sans-serif;\n}\n\n"
    ".inserted {\nbackground-color: #d4fcbc;\ndisplay: block;\nwidth: fit-content;\n}\n"
    "\n"
    ".deleted {\nbackground-color: #fbb6c2;\ndisplay: block;\nwidth: fit-content;\n}\n"
    "\n"
    ".center {\ndisplay: flex;\njustify-content: center;\n}\n</style>"
)


def clean_directory_name(name: str) -> str:
    """
    Return a filesystem-safe directory version of 'name' by replacing invalid
    characters.
    """
    return re.sub(r'[\\/:*?"<>|]', "-", name).strip(". ")


def wrap_html(html: str, styles: str = default_html_styles) -> str:
    """
    Return a wrapped HTML content in a complete document template using 'styles'. This
    requires 'html' to already include proper 'class' attributes.
    """
    return (
        f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head>"
        f"<body><div class='center'><div id='target'>{html}</div></div></body></html>"
    )


def generate_commit_hash(
    timestamp: str, commit_message: str, name: str, email: str, parent_hash: str | None
) -> str:
    """Generate a SHA-256 hash for the commit."""

    return hashlib.sha256(
        f"{timestamp}/{commit_message}/{name}/{email}/{parent_hash}".encode()
    ).hexdigest()


def copy_docx_to_objects(sha_hash: str) -> None:
    """Copy the current document to the objects directory renamed to 'sha_hash'."""
    
    shutil.copy2(
        Repository.document_path(), 
        Repository.docx_objects_path() / f"{sha_hash}.docx",
    )


def write_docx_html(
    sha_hash: str, docx_html: str, cwd: Path | None = None, styles: str | None = None
) -> None:
    """
    Write the document as HTML to the objects directory, naming the file 'sha_hash'.
    """

    if cwd is None:
        cwd = Path.cwd()
    if styles is None:
        styles = default_html_styles
    with open(
        cwd / ".sccs" / "objects" / "html" / f"{sha_hash}.html",
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(styles + docx_html)


def write_view_html(sha_hash: str, docx_html: str, cwd: Path | None = None) -> None:
    """
    Write the document HTML used for viewing, which is centered unlike the normal
    document HTML. Name the HTML file 'sha_hash'.
    """

    if cwd is None:
        cwd = Path.cwd()
    with open(
        cwd / ".sccs" / "objects" / "view_html" / f"{sha_hash}.html",
        "w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        f.write(wrap_html(docx_html))


def update_commit_binary_hash_history(
    sha_hash: str,
    hash_docx_binary: str,
    cwd: Path | None = None,
    current_branch: str | None = None,
) -> dict[str, dict]:
    """Update the commit bytes hash history."""

    if not Repository.current_branch().byte_hashes_path().is_file():
        raise FileNotFoundError(
            "Commit file hash not found. Please run 'sccs init <file_path>' to "
            f"initialize SCCS for this file."
        )

    try:
        with open(Repository.current_branch().byte_hashes_path(), "r", encoding="utf-8", newline="\n") as f:
            commit_file_hash = json.load(f)

    except Exception as e:
        raise exceptions.FileOpenError from e

    commit_file_hash[f"{sha_hash}"] = hash_docx_binary

    return {Repository.current_branch().byte_hashes_path(): commit_file_hash}


def update_commit_messages(
    sha_hash: str, commit_message: str, cwd: Path | None = None
) -> dict[str, dict]:
    """Update commit messages history."""

    # Check if commit messages file exists
    if cwd is None:
        cwd = Path.cwd()

    if not Repository.commit_messages_path().is_file():
        raise FileNotFoundError(
            "Commit messages file not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    with open(
        Repository.commit_messages_path(), "r", encoding="utf-8", newline="\n"
    ) as f:
        try:
            messages = json.load(f)
        except Exception as e:
            raise exceptions.FileOpenError from e

    messages[f"{sha_hash}"] = f"{commit_message}"

    return {Repository.commit_messages_path(): messages}


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
    if not Repository.current_branch().history_path().is_file():
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
    return {Repository.current_branch().history_path(): history}


def update_changed_branches(
    cwd: Path | None = None,
    updated_branch: list[str] | None = None,
) -> dict[Path, dict] | None:
    """Update the list of branches with unpushed changes."""

    if cwd is None:
        cwd = Path.cwd()

    if updated_branch is None:
        updated_branch = [Repository.current_branch_name()]

    branch_data = Repository.current_branch_data()

    if "updated_branches" in branch_data and isinstance(
        branch_data["updated_branches"], list
    ):
        branch_data["updated_branches"] = list(
            set(branch_data["updated_branches"] + updated_branch)
        )
    else:
        branch_data["updated_branches"] = updated_branch

    current_branch_path = Repository.current_branch_path()

    return {current_branch_path: branch_data}


def combine_update_dicts(*dicts: dict[Path, dict]) -> dict[Path, dict]:
    """
    Combine multiple update dictionaries into a single dictionary for atomically
    updating document history metadata.
    """

    update_dict = {}
    for i in dicts:
        update_dict.update(i)
    return update_dict


def atomically_update_history(update_dict: dict[Path, dict]) -> None:
    """
    For each pair in the dictionary, the key is a Path object and the value is a JSON
    dictionary. Write the JSON to temporary files, then rename the temporary files to
    atomically write.

    Open the key and write the value for each pair in the dictionary.
    """

    for i in update_dict.items():
        key, value = i
        try:
            with open(
                key.with_suffix(".tmp"), "w", encoding="utf-8", newline="\n"
            ) as f:
                json.dump(value, f)
        except Exception as e:
            raise exceptions.TemporaryFileError from e

    for i in update_dict.items():
        key, value = i
        try:
            key.with_suffix(".tmp").replace(key)
        except Exception as e:
            raise exceptions.TemporaryFileError from e


def commit_changes(commit_msg: str) -> str:
    """
    Commit uncommitted changes to the current branch using 'commit_msg' as the
    commit_message.
    """

    name = Repository.config_data("name")

    email = Repository.config_data("email")

    docx_html = Repository.convert_docx_to_html()

    commit_message = commit_msg

    timestamp = datetime.now().isoformat()

    history = Repository.current_branch().commit_history()

    parent_hash = Repository.current_branch().latest_commit()

    sha_hash = generate_commit_hash(timestamp, commit_message, name, email, parent_hash)

    copy_docx_to_objects(sha_hash)

    write_docx_html(sha_hash, docx_html)

    write_view_html(sha_hash, docx_html)

    updated_commit_log_history = update_commit_log_history(
        history, sha_hash, timestamp, name, email, commit_message
    )

    current_branch_binary_hash = Repository.current_branch().hash_current_docx_binary()

    updated_commit_binary_hash_history = update_commit_binary_hash_history(
        sha_hash, current_branch_binary_hash
    )

    updated_commit_messages = update_commit_messages(sha_hash, commit_message)

    updated_branches = update_changed_branches(updated_branch=[Repository.current_branch_name()])

    combined_history_update_dicts = combine_update_dicts(
        updated_commit_log_history,
        updated_commit_binary_hash_history,
        updated_commit_messages,
        updated_branches,
    )

    atomically_update_history(combined_history_update_dicts)

    return sha_hash


def entered_arguement(argument: int) -> str | None:
    """Return the entered command-line argument at the specified index if provided, else None."""
    
    arg_value = sys.argv[argument] if len(sys.argv) > argument else None
    return arg_value.strip() if isinstance(arg_value, str) else None