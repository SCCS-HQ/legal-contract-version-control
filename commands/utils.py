#!/usr/bin/env python3
"""Module for utility functions used in SCCS."""

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import exceptions
import mammoth

working_directory_path = Path.cwd()


current_file_docx_path = working_directory_path / f"{working_directory_path.name}.docx"

sccs_versions_directory_path = working_directory_path / ".sccs"

default_html_styles = (
    "<style>\n* {\nfont-family: Arial, Helvetica, sans-serif;\n}\n\n"
    ".inserted {\nbackground-color: #d4fcbc;\ndisplay: block;\nwidth: fit-content;\n}\n"
    "\n"
    ".deleted {\nbackground-color: #fbb6c2;\ndisplay: block;\nwidth: fit-content;\n}\n"
    "\n"
    ".center {\ndisplay: flex;\njustify-content: center;\n}\n</style>"
)

current_branch_path = (
    working_directory_path / ".sccs" / "current_branch" / "current_branch.json"
)


def clean_directory_name(name: str) -> str:
    """Return a filesystem-safe directory name by replacing invalid characters."""
    return re.sub(r'[\\/:*?"<>|]', "-", name).strip(". ")


def check_sccs_layout(
    sccs_dir: Path = sccs_versions_directory_path,
    docx_path: Path = current_file_docx_path,
) -> None:
    """Validate that required SCCS folders, files, and metadata exist."""

    if not sccs_dir.is_dir():
        raise exceptions.SCCSNotInitializedError(
            "This file has not been initialized with SCCS.\nPlease run 'sccs init "
            "<file_path>' to initialize SCCS for this file."
        )

    if not (sccs_dir / "current_branch").is_dir():
        raise exceptions.BranchNotFoundError(
            "Current branch directory not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "current_branch" / "current_branch.json").is_file():
        raise exceptions.BranchNotFoundError(
            "Current branch file not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    try:
        with open(
            (sccs_dir / "current_branch" / "current_branch.json"),
            "r",
            encoding="utf-8",
            newline="\n",
        ) as current_branch_file:
            current_branch = json.load(current_branch_file).get("current_branch")
            if not current_branch:
                raise exceptions.InvalidMetadataError(
                    "Current branch not found. Please run 'sccs init <file_path>' to "
                    "initialize SCCS for this file."
                )

    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        raise exceptions.InvalidMetadataError(
            "Current branch file is missing or corrupted. Please run 'sccs init "
            "<file_path>' to initialize SCCS for this file."
        ) from e

    if not (sccs_dir / "branches" / current_branch).is_dir():
        raise exceptions.BranchNotFoundError(
            "Branch directory not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "branches" / current_branch / "commit_file_hash").is_dir():
        raise FileNotFoundError(
            "Commit file hash directory not found. Please run 'sccs init <file_path>' "
            "to initialize SCCS for this file."
        )
    if not (
        sccs_dir
        / "branches"
        / current_branch
        / "commit_file_hash"
        / "commit_file_hash.json"
    ).is_file():
        raise FileNotFoundError(
            "Commit file hash JSON not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "commit_messages").is_dir():
        raise FileNotFoundError(
            "Commit messages directory not found. Please run 'sccs init <file_path>' to"
            " initialize SCCS for this file."
        )

    if not (sccs_dir / "commit_messages" / "commit_messages.json").is_file():
        raise FileNotFoundError(
            "Commit messages JSON not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "objects").is_dir():

        raise FileNotFoundError(
            "Objects directory not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "objects" / "docx").is_dir():
        raise FileNotFoundError(
            "Docx objects directory not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "objects" / "html").is_dir():
        raise FileNotFoundError(
            "HTML objects directory not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "objects" / "view_html").is_dir():
        raise FileNotFoundError(
            "View HTML objects directory not found. Please run 'sccs init <file_path>' "
            "to initialize SCCS for this file."
        )

    if not (sccs_dir / "config").is_dir():
        raise FileNotFoundError(
            "Config directory not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "config" / "config.json").is_file():
        raise FileNotFoundError(
            "Config file not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (sccs_dir / "branches" / current_branch / "history").is_dir():
        raise FileNotFoundError(
            "History directory not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not (
        sccs_dir / "branches" / current_branch / "history" / "commit_history.json"
    ).is_file():
        raise FileNotFoundError(
            "Commit history JSON not found. Please run 'sccs init <file_path>' to "
            "initialize SCCS for this file."
        )

    if not docx_path.is_file():
        raise FileNotFoundError(
            "Docx file not found. Re-initialize SCCS for this file with 'sccs init "
            "<file_path>'"
        )


def wrap_html(html: str, styles: str = default_html_styles) -> str:
    """Wrap HTML content in a complete document template with default styles."""
    return (
        f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head>"
        f"<body><div class='center'><div id='target'>{html}</div></div></body></html>"
    )


def hash_current_docx_binary(docx_path: Path = current_file_docx_path) -> str:
    """Compute and return the SHA-256 hash of the current DOCX file bytes."""
    try:
        with open(docx_path, "rb") as f:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        raise exceptions.DocumentHashingError from e
    return hashed_file


def get_current_branch(file_path: Path = current_branch_path) -> str:
    """Return the active branch name from the current branch metadata file."""
    try:
        with open(
            file_path, "r", encoding="utf-8", newline="\n"
        ) as current_branch_file:
            current_branch = json.load(current_branch_file).get("current_branch")
            if not current_branch:
                raise exceptions.InvalidMetadataError(
                    "Current branch is missing from JSON. Please run 'sccs init "
                    "<file_path>' to initialize SCCS for this file."
                )
    except Exception as e:
        raise exceptions.FileOpenError from e

    return current_branch


def get_branch_data(
    file_path: Path = current_branch_path, key: str | None = None
) -> dict | str | None:
    """Return full branch metadata or a specific value by key."""
    try:
        with open(file_path, "r", encoding="utf-8", newline="\n") as f:
            data = json.load(f)
            if key:
                return data.get(key)
            return data

    except Exception as e:
        raise exceptions.FileOpenError from e


def convert_docx_to_html(docx_path: Path | None = None) -> str:
    """Convert a DOCX document to HTML and return the generated markup."""
    if docx_path is None:
        docx_path = current_file_docx_path
    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f)
            return result.value
    except Exception as e:
        raise exceptions.ConvertingDocumentToHTMLError from e


def get_key_from_config(key: str, cwd: Path | None = None) -> str:
    """Retrieve a specific key from the SCCS config file."""
    if cwd is None:
        cwd = working_directory_path
    with open(
        Path(cwd) / ".sccs" / "config" / "config.json",
        "r",
        encoding="utf-8",
        newline="\n",
    ) as f:

        value = json.load(f).get(key)
        if value is None:
            raise exceptions.InvalidMetadataError(
                f"Key '{key}' not found in config file. Please configure the "
                f"information in the config file. with 'sccs config {key} <value>'."
            )
        return value


def write_key_to_config(key: str, value: str, cwd: Path | None = None) -> None:
    """Write a specific key to the config file."""
    if cwd is None:
        cwd = working_directory_path

    with open(
        Path(cwd) / ".sccs" / "config" / "config.json",
        "r+",
        encoding="utf-8",
        newline="\n",
    ) as f:

        config = json.load(f)
        config[key] = value
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()


def get_timestamp() -> str:
    """Retrieve the current timestamp."""

    return datetime.now().isoformat()


def get_history_path(
    cwd: Path | None = None, current_branch: str | None = None
) -> Path:
    """Retrieve the path to the commit history file."""

    if cwd is None:
        cwd = working_directory_path
    if current_branch is None:
        current_branch = get_current_branch()
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


def get_parent_hash(history: dict | None = None) -> str | None:
    """Retrieve the parent hash from the commit history."""
    if history is None:
        history = get_commit_history()
    parent_hash = history["history"].get("latest_commit")
    return parent_hash


def generate_commit_hash(
    timestamp: str, commit_message: str, name: str, email: str, parent_hash: str | None
) -> str:
    """Generate a SHA-256 hash for the commit."""

    return hashlib.sha256(
        f"{timestamp}/{commit_message}/{name}/{email}/{parent_hash}".encode()
    ).hexdigest()


def copy_docx_to_objects(
    sha_hash: str, docx_path: Path | None = None, cwd: Path | None = None
) -> None:
    """Copy the current document to the objects directory."""

    if docx_path is None:
        docx_path = current_file_docx_path
    if cwd is None:
        cwd = working_directory_path
    shutil.copy2(
        cwd / docx_path.name,
        cwd / ".sccs" / "objects" / "docx" / f"{sha_hash}.docx",
    )


def write_diff_html(
    sha_hash: str, docx_html: str, cwd: Path | None = None, styles: str | None = None
) -> None:
    """Write the diff HTML file."""

    if cwd is None:
        cwd = working_directory_path
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
    """Write the view HTML file."""

    if cwd is None:
        cwd = working_directory_path
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
    """Update commit binary hash history."""

    # Update commit file hash
    if cwd is None:
        cwd = working_directory_path
    if current_branch is None:
        current_branch = get_current_branch()

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


def update_commit_messages(
    sha_hash: str, commit_message: str, cwd: Path | None = None
) -> dict[str, dict]:
    """Update commit messages."""

    # Check if commit messages file exists
    if cwd is None:
        cwd = working_directory_path
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


def commit_changes(commit_msg: str) -> str:
    """Commit changes to the current branch with the given commit information."""

    name = get_key_from_config("name")

    email = get_key_from_config("email")

    docx_html = convert_docx_to_html()

    commit_message = commit_msg

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

    current_branch_binary_hash = hash_current_docx_binary()

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

    return sha_hash


def validate_commit(
    folder: str,
    cwd: Path | None = None,
    commit: Path | None = None,
) -> Path:
    """Validate the commit file path entered by the user."""

    commit = Path(commit.strip()) if commit else None

    if cwd is None:
        cwd = working_directory_path

    if commit is None:
        raise exceptions.InvalidArgumentError(
            "No commit file path provided. Please specify a commit file path."
        )

    if len(commit.stem.strip()) != 64 and len(commit.stem.strip()) != 10:
        raise exceptions.InvalidArgumentError(
            "Invalid commit file name. Please provide a shortened, 10 character commit hash or the full 64 character commit hash as the commit identifier."
        )

    objects_dir = cwd / ".sccs" / "objects" / folder

    matching_files = []

    for file in objects_dir.iterdir():

        if str(file.stem).startswith(str(commit.stem.strip())):
            matching_files.append(file)

    if not matching_files:
        raise exceptions.InvalidArgumentError(
            f"Commit file '{commit}' does not exist. Please provide a valid commit file"
            f" path."
        )

    if len(matching_files) > 1:
        raise exceptions.InvalidArgumentError(
            f"Multiple commit files found matching '{commit}'. Please provide a full, 64 character commit hash."
        )

    return matching_files[0]
