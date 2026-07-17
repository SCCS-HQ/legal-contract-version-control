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


def get_document_repo_path(constants: SCCSConstants, docx_path: Path) -> Path:
    """
    Return the repo directory path derived from the entered document path, which is the
    document path without a suffix.
    """
   
    if not docx_path:
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.DOCUMENT_PATH_FIELD_NAME))
    
    return Path(docx_path).with_suffix(constants.EMPTY_STRING)


def config_inputs(constants: SCCSConstants, repo_path: Path, *data: str) -> dict:
    """
    Prompt the user for a config value and return it if provided, otherwise raise an
    exception.
    """

    values = []

    for i in data:
        data_value = input(constants.INPUT_CONFIG_VALUE_TEMPLATE.format(config_key=i)).strip()
        if not data_value:
            raise exceptions.InvalidInputError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=i))
        values.append(data_value)

    with open(repo_path / constants.SCCS_DIR / constants.CONFIG_DIR / constants.CONFIG_JSON_FILE, "w", encoding="utf-8") as f:
        config = {}

        for i, value in enumerate(values):
            config_key = data[i]
            config_value = value
            config[config_key] = config_value

        f.seek(0)
        json.dump(config, f, indent=4)
    return config


def check_for_prev_init(constants: SCCSConstants, repo_path: Path) -> None:
    """
    Exit if the document has already been initialized with SCCS by checking if the a
    '.sccs' folder exists for the repository.
    """

    if (repo_path / constants.SCCS_DIR).is_dir():
        raise exceptions.AlreadyInitializedError(constants.ALREADY_INITIALIZED_ERROR_MESSAGE)


def check_file_requirements(constants: SCCSConstants, file: Path) -> None:
    """
    Validate that the entered path points to an existing .docx file by checking the file
    extension and if the file exists.
    """

    if Path(file).suffix.lower() != constants.DOCX_EXTENSION:
        raise exceptions.InvalidFileTypeError(constants.INVALID_FILE_TYPE_ERROR_MESSAGE)
    
    if not Path(file).is_file():
        raise exceptions.FileDoesNotExistError(constants.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=file))


def create_commit_sha_hash(constants: SCCSConstants, name: str, email: str) -> str:
    """
    Create a SHA-256 hash for the initial commit using the timestamp, user name, and
    user email.

    Return the created SHA-256 hash as a hexadecimal string.
    """

    hash_parts = [constants.PROGRAM_START_TIME, constants.INITIAL_VERSION_COMMIT_MESSAGE, name, email]

    return hashlib.sha256(
            constants.PATH_SEPARATOR.join(hash_parts)
        ).hexdigest()


def create_sccs_directory_layout(constants: SCCSConstants, repo_path: Path) -> None:
    """Create the full SCCS directory structure inside the repo path."""

    paths = [
        Path(constants.SCCS_DIR),
        (Path(constants.SCCS_DIR) / constants.OBJECTS_DIR),
        (Path(constants.SCCS_DIR) / constants.OBJECTS_DIR / constants.DOCX_DIR),
        (Path(constants.SCCS_DIR) / constants.OBJECTS_DIR / constants.HTML_DIR),
        (Path(constants.SCCS_DIR) / constants.OBJECTS_DIR / constants.VIEW_HTML_DIR),
        (Path(constants.SCCS_DIR) / constants.BRANCHES_DIR),
        (Path(constants.SCCS_DIR) / constants.BRANCHES_DIR / constants.MAIN_BRANCH_NAME),
        (Path(constants.SCCS_DIR) / constants.BRANCHES_DIR / constants.MAIN_BRANCH_NAME / constants.HISTORY_DIR),
        (Path(constants.SCCS_DIR) / constants.BRANCHES_DIR / constants.MAIN_BRANCH_NAME / constants.COMMIT_FILE_HASH_DIR),
        (Path(constants.SCCS_DIR) / constants.COMMIT_MESSAGES_DIR),
        (Path(constants.SCCS_DIR) / constants.CONFIG_DIR),
        (Path(constants.SCCS_DIR) / constants.CURRENT_BRANCH_DIR)
    ]
    
    try:
        repo_path.mkdir(parents=True, exist_ok=True)

        for path in paths:
            (repo_path / path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise exceptions.FileCreateError() from e


def move_document_to_repo_directory(repo_path: Path, docx_path: Path) -> None:
    """Move the source document into the repo directory."""
    
    shutil.move(docx_path, repo_path)


def copy_document_to_objects_as_docx_and_html(constants: SCCSConstants, repo_path: Path, docx_path: Path, sha_hash: str) -> None:
    """
    Copy the document into objects as both .docx and .html. to their corresponding
    folders.
    """

    objects_path = repo_path / constants.SCCS_DIR / constants.OBJECTS_DIR

    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f).value
    except Exception as e:
        raise exceptions.ConvertingDocumentToHTMLError from e

    try:
        shutil.copy2(
            docx_path,
            (objects_path / constants.DOCX_DIR / (sha_hash + constants.DOCX_EXTENSION)),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e

    try:
        with open(
            (objects_path / constants.HTML_DIR / (sha_hash + constants.HTML_EXTENSION)),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(constants.DEFAULT_HTML_STYLES + result)
    except Exception as e:
        raise exceptions.FileWriteError from e

    try:
        with open(
            (objects_path / constants.VIEW_HTML_DIR / sha_hash + constants.HTML_EXTENSION),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(utils.wrap_html(constants, result, constants.DEFAULT_HTML_STYLES))
    except Exception as e:
        raise exceptions.FileWriteError from e


def write_history_data(constants: SCCSConstants, repo_path: Path, name: str, email: str, sha_hash: str) -> None:
    """Write the initial commit history JSON file to the main branch history folder."""


    history_data = {
        constants.HISTORY_DICT_KEY: {
            constants.INITIAL_COMMIT_DICT_KEY: sha_hash,
            constants.LATEST_COMMIT_DICT_KEY: sha_hash,
            constants.LATEST_COMMIT_NUMBER_DICT_KEY: 1,
            constants.COMMIT_ORDER_DICT_KEY: {constants.INITIAL_COMMIT_NUMBER_DICT_KEY: sha_hash},
        },
        constants.LOG_DICT_KEY: {
            sha_hash: {
                constants.TIMESTAMP_DICT_KEY: constants.PROGRAM_START_TIME,
                constants.AUTHOR_DICT_KEY: constants.COMMIT_AUTHOR_TEMPLATE.format(name=name, email=email),
                constants.MESSAGE_DICT_KEY: constants.INITIAL_COMMIT_MESSAGE,
            }
        },
    }
    try:
        with open(
            repo_path / constants.SCCS_DIR / constants.BRANCHES_DIR / constants.MAIN_BRANCH_NAME / constants.HISTORY_DIR / constants.HISTORY_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_commit_message_data(constants: SCCSConstants, repo_path: Path, sha_hash: str) -> None:
    """
    Write the initial commit message JSON file to the main branch commit messages
    folder.
    """

    commit_message_data = {
        sha_hash: constants.INITIAL_COMMIT_MESSAGE
    }
    try:
        with open(
            repo_path / constants.SCCS_DIR / constants.COMMIT_MESSAGES_DIR/ constants.COMMIT_MESSAGES_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_message_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_hashed_file_commit_data(
        constants: SCCSConstants,
        repo_path: Path,
        docx_path: Path,
        sha_hash
    ) -> None:
    """
    Write the initial commit file binary hash JSON file to the main branch commit file
    hash folder.
    """

    try:
        with open(docx_path, "rb") as f:
            hasher = hashlib.sha256()
            for i in iter(lambda: f.read(constants.MAX_FILE_READ_SIZE), b""):
                hasher.update(i)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        raise exceptions.DocumentHashingError from e

    commit_file_hash_data = {sha_hash: hashed_file}
    try:
        with open(
            repo_path / constants.SCCS_DIR / constants.BRANCHES_DIR / constants.MAIN_BRANCH_NAME / constants.COMMIT_FILE_HASH_DIR / constants.COMMIT_FILE_HASH_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_file_hash_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def write_branch_data(constants: SCCSConstants, repo_path: Path) -> None:
    """Write the initial branch tracking JSON file."""

    try:
        with open(
            repo_path / constants.SCCS_DIR / constants.CURRENT_BRANCH_DIR / constants.CURRENT_BRANCH_JSON_FILE,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(constants.DEFAULT_BRANCH_DATA, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def delete_repository_after_error(repo_path: Path) -> None:
    shutil.rmtree(repo_path, ignore_errors=True)


def print_init_success_message(constants: SCCSConstants) -> None:
    """Print a confirmation message for successful SCCS initialization."""

    print(constants.INIT_SUCCESS_MESSAGE)


def main(constants: SCCSConstants, docx_path: str) -> None:
    """Run functions for the <sccs init> command."""
   
    repo_path = get_document_repo_path(constants, docx_path)

    try:
        check_for_prev_init(constants, repo_path)

        check_file_requirements(constants, docx_path)

        create_sccs_directory_layout(constants, repo_path)
        
        config = config_inputs(constants, repo_path, constants.NAME_KEY, constants.EMAIL_KEY)

        name = config[constants.NAME_KEY]
        email = config[constants.EMAIL_KEY]

        sha_hash = create_commit_sha_hash(constants, name, email)

        move_document_to_repo_directory(repo_path, docx_path)

        copy_document_to_objects_as_docx_and_html(constants, repo_path, docx_path, sha_hash)

        write_history_data(constants, repo_path, name, email, sha_hash)

        write_commit_message_data(constants, repo_path, sha_hash)

        write_hashed_file_commit_data(constants, repo_path, docx_path, sha_hash)

        write_branch_data(constants, repo_path)

        print_init_success_message(constants)

    except Exception:
        delete_repository_after_error(repo_path)
        raise


if __name__ == "__main__":
    utils.run_command(main, 2, use_RepositoryLayout=False)