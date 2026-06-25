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
from constants_classes import SCCSConstants, ErrorWrappers


def get_document_repo_path(constants: SCCSConstants, docx_path: Path | None = None) -> Path:
    """
    Return the repo directory path derived from the entered document path, which is the
    document path without a suffix.
    """

    if docx_path is None:
        docx_path = utils.entered_argument(2)
   
    if not docx_path:
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field="document path"))
    
    return Path(docx_path).with_suffix("")


def config_inputs(constants: SCCSConstants, repo_path: Path | None = None, *data: str) -> dict:
    """
    Prompt the user for a config value and return it if provided, otherwise raise an
    exception.
    """

    if repo_path is None:
        repo_path = get_document_repo_path(constants)

    values = []

    for i in data:
        data_value = input(constants.INPUT_CONFIG_DIR_VALUE_TEMPLATE.format(config_key=i)).strip()
        if not data_value:
            raise exceptions.InvalidInputError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=i))
        values.append(data_value)

    with open(repo_path / constants.SCCS / constants.CONFIG_DIR / constants.CONFIG_DIR_JSON_FILE, "w", encoding="utf-8") as f:
        config = {}

        for i, value in enumerate(values):
            config_key = data[i]
            config_value = value
            config[config_key] = config_value

        f.seek(0)
        json.dump(config, f, indent=4)
    return config


def check_for_prev_init(constants: SCCSConstants, repo_path: Path | None = None) -> None:
    """
    Exit if the document has already been initialized with SCCS by checking if the a
    '.sccs' folder exists for the repository.
    """

    if repo_path is None:
        repo_path = get_document_repo_path(constants)

    if (repo_path / constants.SCCS).is_dir():
        raise exceptions.AlreadyInitializedError(constants.ALREADY_INITIALIZED_ERROR_MESSAGE)


def check_file_requirements(constants: SCCSConstants, file: Path | None = None) -> None:
    """
    Validate that the entered path points to an existing .docx file by checking the file
    extension and if the file exists.
    """

    if file is None:
        file = utils.entered_argument(2)

    if Path(file).suffix.lower() != constants.DOCX_EXTENSION:
        raise exceptions.InvalidFileTypeError(constants.INVALID_FILE_TYPE_ERROR_MESSAGE)
    
    if not Path(file).is_file():
        raise exceptions.FileDoesNotExistError(constants.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=file))

def create_commit_sha_hash(constants: SCCSConstants, repo_path: Path | None = None, name: str | None = None, email: str | None = None) -> str:
    """
    Create a SHA-256 hash for the initial commit using the timestamp, user name, and
    user email.

    Return the created SHA-256 hash as a hexadecimal string.
    """
    if repo_path is None:
        repo_path = get_document_repo_path(constants)

    if name is None or email is None:
        with open(repo_path / constants.SCCS / constants.CONFIG_DIR / constants.CONFIG_DIR_JSON_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            if name is None:
                name = config.get(constants.NAME)
            if email is None:
                email = config.get(constants.EMAIL)


    return hashlib.sha256(
        f"{constants.PROGRAM_START_TIME}/{constants.INITIAL_VERSION_HASH_SEGMENT}/{name}/{email}".encode()
    ).hexdigest()


def create_sccs_directory_layout(constants: SCCSConstants, repo_path: Path | None = None) -> None:
    """Create the full SCCS directory structure inside the repo path."""

    if repo_path is None:
        repo_path = get_document_repo_path(constants)

    paths = [
        Path(constants.SCCS),
        (Path(constants.SCCS) / constants.OBJECTS_DIR),
        (Path(constants.SCCS) / constants.OBJECTS_DIR / constants.DOCX_DIR),
        (Path(constants.SCCS) / constants.OBJECTS_DIR / constants.HTML_DIR),
        (Path(constants.SCCS) / constants.OBJECTS_DIR / constants.VIEW_HTML_DIR),
        (Path(constants.SCCS) / constants.BRANCHES_DIR),
        (Path(constants.SCCS) / constants.BRANCHES_DIR / constants.MAIN_BRANCH),
        (Path(constants.SCCS) / constants.BRANCHES_DIR / constants.MAIN_BRANCH / constants.HISTORY_DIR),
        (Path(constants.SCCS) / constants.BRANCHES_DIR / constants.MAIN_BRANCH / constants.COMMIT_FILE_HASH_DIR),
        (Path(constants.SCCS) / constants.COMMIT_MESSAGES_DIR),
        (Path(constants.SCCS) / constants.CONFIG_DIR),
        (Path(constants.SCCS) / constants.CURRENT_BRANCH_DIR)
    ]
    
    try:
        repo_path.mkdir(parents=True, exist_ok=True)

        for path in paths:
            (repo_path / path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise exceptions.FileCreateError()from e


def move_document_to_repo_directory(constants: SCCSConstants, repo_path: Path | None = None, docx_path: Path | None = None) -> None:
    """Move the source document into the repo directory."""

    if repo_path is None:
        repo_path = get_document_repo_path(constants)

    if docx_path is None:
        docx_path = utils.entered_argument(2)

    shutil.move(docx_path, repo_path)


def copy_document_to_objects_as_docx_and_html(constants: SCCSConstants, repo_path: Path | None = None, docx_path: Path | None = None) -> None:
    """
    Copy the document into objects as both .docx and .html. to their corresponding
    folders.
    """
    if repo_path is None:
        repo_path = get_document_repo_path(constants)
        
    if docx_path is None:
        docx_path = Path(repo_path / Path(utils.entered_argument(2)).name)
        
    objects_path = repo_path / constants.SCCS / constants.OBJECTS_DIR

    sha_hash = create_commit_sha_hash(constants, repo_path)
    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f).value
    except Exception as e:
        raise exceptions.ConvertingDocumentToHTMLError from e

    try:
        shutil.copy2(
            docx_path,
            (objects_path / constants.DOCX_DIR / f"{sha_hash}.docx"),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e

    try:
        with open(
            (objects_path / constants.HTML_DIR / f"{sha_hash}.html"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(utils.default_html_styles + result)
    except Exception as e:
        raise exceptions.FileWriteError from e

    try:
        with open(
            (objects_path / constants.VIEW_HTML_DIR / f"{sha_hash}.html"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(utils.wrap_html(result))
    except Exception as e:
        raise exceptions.FileWriteError from e


def write_history_data(constants: SCCSConstants, repo_path: Path | None = None, name: str | None = None, email: str | None = None) -> None:
    """Write the initial commit history JSON file to the main branch history folder."""

    if repo_path is None:
        repo_path = get_document_repo_path(constants)

    if name is None:
        with open(repo_path / constants.SCCS / constants.CONFIG_DIR / constants.CONFIG_DIR_JSON_FILE, "r", encoding="utf-8") as f:
            name = json.load(f).get(constants.NAME)
    if email is None:
        with open(repo_path / constants.SCCS / constants.CONFIG_DIR / constants.CONFIG_DIR_JSON_FILE, "r", encoding="utf-8") as f:
            email = json.load(f).get(constants.EMAIL)

    sha_hash = create_commit_sha_hash(constants, repo_path, name=name, email=email)

    history_data = {
        "history": {
            "initial_commit": f"{sha_hash}",
            "latest_commit": f"{sha_hash}",
            "latest_commit_number": 1,
            "commit_order": {"1": f"{sha_hash}"},
        },
        "log": {
            f"{sha_hash}": {
                "timestamp": constants.PROGRAM_START_TIME,
                "author": f"{name} <{email}>",
                "message": constants.INITIAL_COMMIT_MESSAGE,
            }
        },
    }
    try:
        with open(
            repo_path / constants.SCCS / constants.BRANCHES_DIR / constants.MAIN_BRANCH / constants.HISTORY_DIR / constants.HISTORY_DIR_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_commit_message_data(constants: SCCSConstants, repo_path: Path | None = None, sha_hash: str | None = None) -> None:
    """
    Write the initial commit message JSON file to the main branch commit messages
    folder.
    """

    if repo_path is None:
        repo_path = get_document_repo_path(constants)
    if sha_hash is None:
        sha_hash = create_commit_sha_hash(constants, repo_path)

    commit_message_data = {
        f"{sha_hash}": constants.INITIAL_COMMIT_MESSAGE
    }
    try:
        with open(
            repo_path / constants.SCCS / constants.COMMIT_MESSAGES_DIR/ constants.COMMIT_MESSAGES_DIR_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_message_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_hashed_file_commit_data(constants: SCCSConstants, repo_path: Path | None = None, docx_path: Path | None = None, sha_hash: str | None = None) -> None:
    """
    Write the initial commit file binary hash JSON file to the main branch commit file
    hash folder.
    """
    if repo_path is None:
        repo_path = get_document_repo_path(constants)
    if sha_hash is None:
        sha_hash = create_commit_sha_hash(constants, repo_path)
    if docx_path is None:
        docx_path = (repo_path / Path(utils.entered_argument(2)).name)

    try:
        with open(docx_path, "rb") as f:
            hasher = hashlib.sha256()
            for i in iter(lambda: f.read(constants.MAX_FILE_READ_SIZE), b""):
                hasher.update(i)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        raise exceptions.DocumentHashingError from e

    commit_file_hash_data = {f"{sha_hash}": hashed_file}
    try:
        with open(
            repo_path / constants.SCCS / constants.BRANCHES_DIR / constants.MAIN_BRANCH / constants.COMMIT_FILE_HASH_DIR / constants.COMMIT_FILE_HASH_DIR_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_file_hash_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def write_branch_data(constants: SCCSConstants, repo_path: Path | None = None) -> None:
    """Write the initial branch tracking JSON file."""

    if repo_path is None:
        repo_path = get_document_repo_path(constants)

    try:
        with open(
            repo_path / constants.SCCS / constants.CURRENT_BRANCH_DIR / constants.CURRENT_BRANCH_DIR_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(constants.DEFAULT_BRANCH_DATA, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def confirmation_message(constants: SCCSConstants) -> None:
    """Print a confirmation message for successful SCCS initialization."""

    print(constants.INIT_SUCCESS_MESSAGE)


def main(constants: SCCSConstants) -> None:
    """Run functions for the <sccs init> command."""

    check_for_prev_init(constants)

    check_file_requirements(constants)

    create_sccs_directory_layout(constants)

    config_inputs(constants, None, constants.NAME, constants.EMAIL)

    create_commit_sha_hash(constants)

    move_document_to_repo_directory(constants)

    copy_document_to_objects_as_docx_and_html(constants)

    write_history_data(constants)

    write_commit_message_data(constants)

    write_hashed_file_commit_data(constants)

    write_branch_data(constants)

    confirmation_message(constants)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        error_wrappers = ErrorWrappers()
        main(constants)

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)