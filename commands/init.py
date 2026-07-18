#!/usr/bin/env python3
"""Initialize a document with SCCS."""

import hashlib
import json
import shutil
from pathlib import Path
import mammoth

import exceptions
import utils
from constants_classes import SCCSConstants


def get_document_repo_path(c: SCCSConstants, docx_path: Path) -> Path:
    """
    Return the repo directory path derived from the entered document path, which is the
    document path without a suffix.
    """
   
    if not docx_path:
        raise exceptions.InvalidArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.DOCUMENT_PATH_FIELD_NAME))
    
    return Path(docx_path).with_suffix(c.EMPTY_STRING)


def config_inputs(c: SCCSConstants, repo_path: Path, *data: str) -> dict:
    """
    Prompt the user for a config value and return it if provided, otherwise raise an
    exception.
    """

    values = []

    for i in data:
        data_value = input(c.INPUT_CONFIG_VALUE_TEMPLATE.format(config_key=i)).strip()
        if not data_value:
            raise exceptions.InvalidInputError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=i))
        values.append(data_value)

    with open(repo_path / c.SCCS_DIR / c.CONFIG_DIR / c.CONFIG_JSON_FILE, "w", encoding=c.UTF_8) as f:
        config = {}

        for i, value in enumerate(values):
            config_key = data[i]
            config_value = value
            config[config_key] = config_value

        f.seek(0)
        json.dump(config, f, indent=4)
    return config


def check_for_prev_init(c: SCCSConstants, repo_path: Path) -> None:
    """
    Exit if the document has already been initialized with SCCS by checking if the a
    '.sccs' folder exists for the repository.
    """

    if (repo_path / c.SCCS_DIR).is_dir():
        raise exceptions.AlreadyInitializedError(c.ALREADY_INITIALIZED_ERROR_MESSAGE)


def check_file_requirements(c: SCCSConstants, file: Path) -> None:
    """
    Validate that the entered path points to an existing .docx file by checking the file
    extension and if the file exists.
    """

    if Path(file).suffix.lower() != c.DOCX_EXTENSION:
        raise exceptions.InvalidFileTypeError(c.INVALID_FILE_TYPE_ERROR_MESSAGE)
    
    if not Path(file).is_file():
        raise exceptions.FileDoesNotExistError(c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=file))


def create_commit_sha_hash(c: SCCSConstants, name: str, email: str) -> str:
    """
    Create a SHA-256 hash for the initial commit using the timestamp, user name, and
    user email.

    Return the created SHA-256 hash as a hexadecimal string.
    """

    hash_parts = [c.PROGRAM_START_TIME, c.INITIAL_VERSION_COMMIT_MESSAGE, name, email]

    return hashlib.sha256(
            c.PATH_SEPARATOR.join(hash_parts).encode(c.UTF_8)
        ).hexdigest()


def create_sccs_directory_layout(c: SCCSConstants, repo_path: Path) -> None:
    """Create the full SCCS directory structure inside the repo path."""

    paths = [
        Path(c.SCCS_DIR),
        (Path(c.SCCS_DIR) / c.OBJECTS_DIR),
        (Path(c.SCCS_DIR) / c.OBJECTS_DIR / c.DOCX_DIR),
        (Path(c.SCCS_DIR) / c.OBJECTS_DIR / c.HTML_DIR),
        (Path(c.SCCS_DIR) / c.OBJECTS_DIR / c.VIEW_HTML_DIR),
        (Path(c.SCCS_DIR) / c.BRANCHES_DIR),
        (Path(c.SCCS_DIR) / c.BRANCHES_DIR / c.MAIN_BRANCH_NAME),
        (Path(c.SCCS_DIR) / c.BRANCHES_DIR / c.MAIN_BRANCH_NAME / c.HISTORY_DIR),
        (Path(c.SCCS_DIR) / c.BRANCHES_DIR / c.MAIN_BRANCH_NAME / c.COMMIT_FILE_HASH_DIR),
        (Path(c.SCCS_DIR) / c.COMMIT_MESSAGES_DIR),
        (Path(c.SCCS_DIR) / c.CONFIG_DIR),
        (Path(c.SCCS_DIR) / c.CURRENT_BRANCH_DIR)
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


def copy_document_to_objects_as_docx_and_html(c: SCCSConstants, repo_path: Path, docx_path: Path, sha_hash: str) -> None:
    """
    Copy the document into objects as both .docx and .html. to their corresponding
    folders.
    """

    objects_path = repo_path / c.SCCS_DIR / c.OBJECTS_DIR

    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f).value
    except Exception as e:
        raise exceptions.ConvertingDocumentToHTMLError from e

    try:
        shutil.copy2(
            docx_path,
            (objects_path / c.DOCX_DIR / sha_hash).with_suffix(c.DOCX_EXTENSION),
        )
    except Exception as e:
        raise exceptions.FileCopyError from e

    try:
        with open(
            (objects_path / c.HTML_DIR / sha_hash).with_suffix(c.HTML_EXTENSION),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            f.write(c.DEFAULT_HTML_STYLES + result)
    except Exception as e:
        raise exceptions.FileWriteError from e

    try:
        with open(
            (objects_path / c.VIEW_HTML_DIR / sha_hash).with_suffix(c.HTML_EXTENSION),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            f.write(utils.wrap_html(c, result, c.DEFAULT_HTML_STYLES))
    except Exception as e:
        raise exceptions.FileWriteError from e


def write_history_data(c: SCCSConstants, repo_path: Path, name: str, email: str, sha_hash: str) -> None:
    """Write the initial commit history JSON file to the main branch history folder."""


    history_data = {
        c.HISTORY_DICT_KEY: {
            c.INITIAL_COMMIT_DICT_KEY: sha_hash,
            c.LATEST_COMMIT_DICT_KEY: sha_hash,
            c.LATEST_COMMIT_NUMBER_DICT_KEY: 1,
            c.COMMIT_ORDER_DICT_KEY: {c.INITIAL_COMMIT_NUMBER_DICT_KEY: sha_hash},
        },
        c.LOG_DICT_KEY: {
            sha_hash: {
                c.TIMESTAMP_DICT_KEY: c.PROGRAM_START_TIME,
                c.AUTHOR_DICT_KEY: c.COMMIT_AUTHOR_TEMPLATE.format(name=name, email=email),
                c.MESSAGE_DICT_KEY: c.INITIAL_COMMIT_MESSAGE,
            }
        },
    }
    try:
        with open(
            repo_path / c.SCCS_DIR / c.BRANCHES_DIR / c.MAIN_BRANCH_NAME / c.HISTORY_DIR / c.HISTORY_JSON_FILE,
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_commit_message_data(c: SCCSConstants, repo_path: Path, sha_hash: str) -> None:
    """
    Write the initial commit message JSON file to the main branch commit messages
    folder.
    """

    commit_message_data = {
        sha_hash: c.INITIAL_COMMIT_MESSAGE
    }
    try:
        with open(
            repo_path / c.SCCS_DIR / c.COMMIT_MESSAGES_DIR/ c.COMMIT_MESSAGES_JSON_FILE,
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            json.dump(commit_message_data, f, indent=4)
    except Exception as e:
        raise exceptions.FileOpenError from e


def write_hashed_file_commit_data(
        c: SCCSConstants,
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
            while i := f.read(c.MAX_FILE_READ_SIZE):
                hasher.update(i)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        raise exceptions.DocumentHashingError from e

    commit_file_hash_data = {sha_hash: hashed_file}
    try:
        with open(
            repo_path / c.SCCS_DIR / c.BRANCHES_DIR / c.MAIN_BRANCH_NAME / c.COMMIT_FILE_HASH_DIR / c.COMMIT_FILE_HASH_JSON_FILE,
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            json.dump(commit_file_hash_data, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def write_branch_data(c: SCCSConstants, repo_path: Path) -> None:
    """Write the initial branch tracking JSON file."""

    try:
        with open(
            repo_path / c.SCCS_DIR / c.CURRENT_BRANCH_DIR / c.CURRENT_BRANCH_JSON_FILE,
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            json.dump(c.DEFAULT_BRANCH_DATA, f, indent=4)
    except Exception as e:
        raise exceptions.UpdatingMetadataError from e


def delete_repository_after_error(repo_path: Path) -> None:
    shutil.rmtree(repo_path, ignore_errors=True)


def print_init_success_message(c: SCCSConstants) -> None:
    """Print a confirmation message for successful SCCS initialization."""

    print(c.INIT_SUCCESS_MESSAGE)


def main(c: SCCSConstants, docx_path: Path) -> None:
    """Run functions for the <sccs init> command."""
   
    repo_path = get_document_repo_path(c, docx_path)

    try:
        check_for_prev_init(c, repo_path)

        check_file_requirements(c, docx_path)

        create_sccs_directory_layout(c, repo_path)
        
        config = config_inputs(c, repo_path, c.NAME_KEY, c.EMAIL_KEY)

        name = config[c.NAME_KEY]
        email = config[c.EMAIL_KEY]

        sha_hash = create_commit_sha_hash(c, name, email)

        move_document_to_repo_directory(repo_path, docx_path)

        copy_document_to_objects_as_docx_and_html(c, repo_path, docx_path, sha_hash)

        write_history_data(c, repo_path, name, email, sha_hash)

        write_commit_message_data(c, repo_path, sha_hash)

        write_hashed_file_commit_data(c, repo_path, docx_path, sha_hash)

        write_branch_data(c, repo_path)

        print_init_success_message(c)

    except Exception:
        delete_repository_after_error(repo_path)
        raise


if __name__ == "__main__":
    utils.run_command(main, 2, use_RepositoryLayout=False)