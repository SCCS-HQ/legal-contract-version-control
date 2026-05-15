"""Module for utility functions used in SCCS."""

import hashlib
import json
import re
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
    file_path: Path = current_branch_path, key: str = None
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


def convert_docx_to_html(docx_path: Path = None) -> str:
    """Convert a DOCX document to HTML and return the generated markup."""
    if docx_path is None:
        docx_path = current_file_docx_path
    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f)
            return result.value
    except Exception as e:
        raise exceptions.ConvertingDocumentToHTMLError from e
