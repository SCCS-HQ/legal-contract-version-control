#!/usr/bin/env python3
"""Initialize a document with SCCS."""

import hashlib
import json
import sys
import shutil
from datetime import datetime
from pathlib import Path
import mammoth

import exceptions
import utils

PROGRAM_START_TIME = datetime.now().isoformat()
INITIAL_COMMIT_MESSAGE = "initial commit (This is a default commit message for initial version)"

def get_document_repo_path(docx_path: Path | None = None) -> Path:
    """
    Return the repo directory path derived from the entered document path, which is the
    document path without a suffix.
    """

    if docx_path is None:
        docx_path = utils.entered_arguement(2)
   
    if not docx_path:
        raise exceptions.InvalidArgumentError("No file path provided.")
    
    return Path(docx_path).with_suffix("")


def config_inputs(repo_path: Path | None = None, *data: str) -> dict:
    """
    Prompt the user for a config value and return it if provided, otherwise raise an
    exception.
    """

    if repo_path is None:
        repo_path = get_document_repo_path()

    values = []

    for i in data:
        data_value = input(f"Enter your {i}: ").strip()
        if not data_value:
            raise exceptions.InvalidInputError(f"{i} cannot be empty.")
        values.append(data_value)

    with open(repo_path / ".sccs" / "config" / f"config.json", "w", encoding="utf-8") as f:
        config = {}

        for i, value in enumerate(values):
            config_key = data[i]
            config_value = value
            config[config_key] = config_value

        f.seek(0)
        json.dump(config, f, indent=4)
    return config


def check_for_prev_init(repo_path: Path | None = None) -> None:
    """
    Exit if the document has already been initialized with SCCS by checking if the a
    '.sccs' folder exists for the repository.
    """

    if repo_path is None:
        repo_path = get_document_repo_path()

    if (repo_path / ".sccs").is_dir():
        raise exceptions.AlreadyInitializedError(
            "This file has already been initialized with SCCS."
        )


def check_file_requirements(file: Path | None = None) -> None:
    """
    Validate that the entered path points to an existing .docx file by checking the file
    extension and if the file exists.
    """

    if file is None:
        file = utils.entered_arguement(2)

    if Path(file).suffix.lower() != ".docx":
        raise exceptions.InvalidFileTypeError(
            "File is not a .docx file. Please provide a valid .docx file."
        )
    
    if not Path(file).is_file():
        raise exceptions.FileDoesNotExistError("File does not exist.")


def create_commit_sha_hash(repo_path: Path | None = None, time: str | None = None, name: str | None = None, email: str | None = None) -> str:
    """
    Create a SHA-256 hash for the initial commit using the timestamp, user name, and
    user email.

    Return the created SHA-256 hash as a hexadecimal string.
    """
    if repo_path is None:
        repo_path = get_document_repo_path()
    if time is None:
        time = PROGRAM_START_TIME

    if name is None or email is None:
        with open(repo_path / ".sccs" / "config" / "config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            if name is None:
                name = config.get("name")
            if email is None:
                email = config.get("email")


    return hashlib.sha256(
        f"{time}/initial_version/{name}/{email}".encode()
    ).hexdigest()


def create_sccs_directory_layout(repo_path: Path | None = None) -> None:
    """Create the full SCCS directory structure inside the repo path."""

    if repo_path is None:
        repo_path = get_document_repo_path()

    paths = [".sccs",
        Path(".sccs/objects"),
        Path(".sccs/objects/docx"),
        Path(".sccs/objects/html"),
        Path(".sccs/objects/view_html"),
        Path(".sccs/branches"),
        Path(".sccs/branches/main"),
        Path(".sccs/branches/main/history"),
        Path(".sccs/branches/main/commit_file_hash"),
        Path(".sccs/commit_messages"),
        Path(".sccs/config"),
        Path(".sccs/current_branch")
    ]
    
    try:
        repo_path.mkdir(parents=True, exist_ok=True)

        for path in paths:
            (repo_path / path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise exceptions.FileCreateError from e


def move_document_to_repo_directory(repo_path: Path | None = None, docx_path: Path | None = None) -> None:
    """Move the source document into the repo directory."""

    if repo_path is None:
        repo_path = get_document_repo_path()

    if docx_path is None:
        docx_path = utils.entered_arguement(2)

    shutil.move(docx_path, repo_path)


def copy_document_to_objects_as_docx_and_html(
    repo_path: Path | None = None, docx_path: Path | None = None
) -> None:
    """
    Copy the document into objects as both .docx and .html. to their corresponding
    folders.
    """
    if repo_path is None:
        repo_path = get_document_repo_path()
        
    if docx_path is None:
        docx_path = Path(repo_path / Path(utils.entered_arguement(2)).name)
        
    objects_path = repo_path / ".sccs" / "objects"

    sha_hash = create_commit_sha_hash(repo_path)
    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f).value
    except Exception as e:
        raise exceptions.ConvertingDocumentToHTMLError from e

    try:
        shutil.copy2(
            docx_path,
            (objects_path / "docx" / f"{sha_hash}.docx"),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e

    try:
        with open(
            (objects_path / "html" / f"{sha_hash}.html"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(utils.default_html_styles + result)
    except Exception as e:
        raise exceptions.FileWriteError from e

    try:
        with open(
            (objects_path / "view_html" / f"{sha_hash}.html"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(utils.wrap_html(result))
    except Exception as e:
        raise exceptions.FileWriteError from e


def write_history_data(repo_path: Path | None = None, name: str | None = None, email: str | None = None) -> None:
    """Write the initial commit history JSON file to the main branch history folder."""

    if repo_path is None:
        repo_path = get_document_repo_path()

    if name is None:
        with open(repo_path / ".sccs" / "config" / "config.json", "r", encoding="utf-8") as f:
            name = json.load(f).get("name")
    if email is None:
        with open(repo_path / ".sccs" / "config" / "config.json", "r", encoding="utf-8") as f:
            email = json.load(f).get("email")

    sha_hash = create_commit_sha_hash(repo_path, name=name, email=email)

    history_data = {
        "history": {
            "initial_commit": f"{sha_hash}",
            "latest_commit": f"{sha_hash}",
            "latest_commit_number": 1,
            "commit_order": {"1": f"{sha_hash}"},
        },
        "log": {
            f"{sha_hash}": {
                "timestamp": PROGRAM_START_TIME,
                "author": f"{name} <{email}>",
                "message": INITIAL_COMMIT_MESSAGE,
            }
        },
    }
    try:
        with open(
            repo_path / ".sccs" / "branches" / "main" / "history" / "history.json",
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_commit_message_data(repo_path: Path | None = None, sha_hash: str | None = None) -> None:
    """
    Write the initial commit message JSON file to the main branch commit messages
    folder.
    """

    if repo_path is None:
        repo_path = get_document_repo_path()
    if sha_hash is None:
        sha_hash = create_commit_sha_hash(repo_path)

    commit_message_data = {
        f"{sha_hash}": INITIAL_COMMIT_MESSAGE
    }
    try:
        with open(
            repo_path / ".sccs" / "commit_messages" / "commit_messages.json",
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_message_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_hashed_file_commit_data(repo_path: Path | None = None, docx_path: Path | None = None, sha_hash: str | None = None) -> None:
    """
    Write the initial commit file binary hash JSON file to the main branch commit file
    hash folder.
    """
    if repo_path is None:
        repo_path = get_document_repo_path()
    if sha_hash is None:
        sha_hash = create_commit_sha_hash(repo_path)
    if docx_path is None:
        docx_path = (repo_path / Path(utils.entered_arguement(2)).name)

    try:
        with open(docx_path, "rb") as f:
            hasher = hashlib.sha256()
            for i in iter(lambda: f.read(65536), b""):
                hasher.update(i)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        raise exceptions.DocumentHashingError from e

    commit_file_hash_data = {f"{sha_hash}": hashed_file}
    try:
        with open(
            repo_path / ".sccs" / "branches" / "main" / "commit_file_hash" / "commit_file_hash.json",
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_file_hash_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def write_branch_data(repo_path: Path | None = None) -> None:
    """Write the initial branch tracking JSON file."""

    if repo_path is None:
        repo_path = get_document_repo_path()

    branches_data = {"current_branch": "main", "branches": ["main"]}

    try:
        with open(
            repo_path / ".sccs" / "current_branch" / "current_branch.json",
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(branches_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def confirmation_message() -> None:
    """Print a confirmation message for successful SCCS initialization."""

    print("SCCS initialization complete.\n")


def main() -> None:
    """Run functions for the <sccs init> command."""

    check_for_prev_init()

    check_file_requirements()

    create_sccs_directory_layout()

    config_inputs(None, "name", "email")

    create_commit_sha_hash()

    move_document_to_repo_directory()

    copy_document_to_objects_as_docx_and_html()

    write_history_data()

    write_commit_message_data()

    write_hashed_file_commit_data()

    write_branch_data()

    confirmation_message()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)