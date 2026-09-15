#!/usr/bin/env python3

import hashlib
import os
import shutil
from pathlib import Path

import exceptions
import mammoth
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def ask_config_input(c: SCCSConstants, key: str) -> str:
    """
    Prompt the user for the entered configuration key and return the entered value.
    Raise an SCCSException if the value is empty.
    """

    data_value = input(c.INPUT_CONFIG_VALUE_TEMPLATE.format(config_key=key)).strip()
    utils.raise_if_empty(c, data_value, key, capitalize=True)

    return data_value


def copy_document_to_objects_as_document_and_html(
    c: SCCSConstants, document_path: Path, commit_identifier: str, rp: RepositoryPaths
) -> None:
    """
    Copy the document to the document objects directory, convert it to HTML, and write
    the HTML to the HTML and view HTML objects directories. Raise an SCCSException if
    the document cannot be converted or copied.
    """

    try:
        with open(document_path, "rb") as f:
            result = mammoth.convert_to_html(f).value
    except Exception as e:
        raise exceptions.SCCSException(c.INIT_COPY_ERROR_MESSAGE) from e

    try:
        shutil.copy2(
            document_path,
            (rp.document_objects_path() / commit_identifier).with_suffix(
                c.DOCUMENT_EXTENSION
            ),
        )
    except Exception as e:
        raise exceptions.SCCSException(c.INIT_COPY_ERROR_MESSAGE) from e

    try:
        with open(
            (rp.html_objects_path() / commit_identifier).with_suffix(c.HTML_EXTENSION),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            f.write(c.DEFAULT_HTML_STYLES + result)
    except Exception as e:
        raise exceptions.SCCSException(c.INIT_COPY_ERROR_MESSAGE) from e

    try:
        with open(
            (rp.view_html_objects_path() / commit_identifier).with_suffix(
                c.HTML_EXTENSION
            ),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            f.write(utils.wrap_html(c, result, c.DEFAULT_HTML_STYLES))
    except Exception as e:
        raise exceptions.SCCSException(c.INIT_COPY_ERROR_MESSAGE) from e


def copy_document_to_repository_directory(
    repository_path: Path, document_path: Path
) -> None:
    """
    Copy the document to the repository directory.
    """

    shutil.copy2(document_path, repository_path)


def create_commit_identifier(c: SCCSConstants, name: str, email: str) -> str:
    """
    Return the initial commit identifier created by hashing the program start time,
    initial version commit message, name, and email.
    """

    return utils.create_commit_identifier(
        c,
        [c.PROGRAM_START_TIME, c.INITIAL_VERSION_COMMIT_MESSAGE, name, email],
    )


def create_sccs_directory_layout(
    c: SCCSConstants, ri: RepositoryIO, rp: RepositoryPaths, rs: RepositoryStatus
) -> None:
    """
    Create the SCCS directory layout for the repository, including the objects,
    document, and HTML directories. Raise an SCCSException if the directories cannot be
    created.
    """

    rs.target.set(c.MAIN_BRANCH_NAME)

    paths = [
        rp.sccs_path(),
        rp.objects_path(),
        rp.document_objects_path(),
        rp.html_objects_path(),
        rp.view_html_objects_path(),
    ]

    try:
        rp.root.mkdir(parents=True, exist_ok=True)

        for i in paths:
            (i).mkdir(parents=True, exist_ok=True)

    except Exception as e:
        raise exceptions.SCCSException(c.INIT_CREATE_ERROR_MESSAGE) from e

    rs.target.reset()


def finalize_repository_creation(
    c: SCCSConstants,
    document_path: Path,
    rp: RepositoryPaths,
    staging_rp: RepositoryPaths,
) -> None:
    """
    Promote the staging directory to the repository root and remove the original
    document from the parent directory. Print a warning if the source document cannot be
    removed.
    """

    utils.promote_staging(c, staging_rp.root, rp.root)

    try:
        os.remove(document_path)
    except OSError as e:
        print(
            c.SOURCE_FILE_DELETION_ERROR_WARNING_TEMPLATE.format(
                document_path=document_path, e=e
            )
        )


def main(
    c: SCCSConstants,
    document_path: Path,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the init command by validating that the repository is not already initialized
    and that the entered document exists, and by prompting for the name and email
    configuration values.

    Create the repository on a copy in a staging directory, promote it to the repository
    root, print a success message, and reset the target branch when the operation
    completes.
    """

    validate_no_prev_init(c, rp)

    validate_file_requirements(c, document_path)

    name = ask_config_input(c, c.NAME_KEY)
    email = ask_config_input(c, c.EMAIL_KEY)

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        staging_ri = RepositoryIO(staging_root, ri.repository_name, c, ri.target)
        staging_rp = RepositoryPaths(staging_root, rp.repository_name, c, rp.target)
        staging_rs = RepositoryStatus(staging_root, rs.repository_name, c, rs.target)
        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)

        create_sccs_directory_layout(c, staging_ri, staging_rp, staging_rs)

        commit_identifier = create_commit_identifier(c, name, email)

        copy_document_to_objects_as_document_and_html(
            c, document_path, commit_identifier, staging_rp
        )

        copy_document_to_repository_directory(staging_rp.root, document_path)

        write_starting_metadata(c, commit_identifier, name, email, staging_ri)

        staging_rw.write_key_to_config(c.NAME_KEY, name, staging_ri.read_config())
        staging_rw.write_key_to_config(c.EMAIL_KEY, email, staging_ri.read_config())

        finalize_repository_creation(c, document_path, rp, staging_rp)

    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_init_success_message(c)


def print_init_success_message(c: SCCSConstants) -> None:
    """
    Print a success message after a successful init operation.
    """

    print(c.INIT_SUCCESS_MESSAGE)


def validate_file_requirements(c: SCCSConstants, file: Path) -> None:
    """
    Validate the entered document by checking that it has the expected document
    extension and exists. Raise an SCCSException if the file type or path is invalid.
    """

    if file.suffix.lower() != c.DOCUMENT_EXTENSION:
        raise exceptions.SCCSException(c.INVALID_FILE_TYPE_ERROR_MESSAGE)

    if not file.is_file():
        raise exceptions.SCCSException(
            c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=file)
        )


def validate_no_prev_init(c: SCCSConstants, rp: RepositoryPaths) -> None:
    """
    Validate that the repository has not already been initialized by checking for an
    existing SCCS directory. Raise an SCCSException if the repository is already
    initialized.
    """

    if (rp.sccs_path()).is_dir():
        raise exceptions.SCCSException(c.ALREADY_INIT_ERROR_MESSAGE)


def write_starting_metadata(
    c: SCCSConstants, commit_identifier: str, name: str, email: str, ri: RepositoryIO
) -> None:
    """
    Write the starting metadata of the repository, including the initial commit history,
    log, byte hash, commit messages, and default branch data.
    """

    ri.target.set(c.MAIN_BRANCH_NAME)

    ri.write_metadata(
        {
            c.BRANCHES_DICT_KEY: {
                c.MAIN_BRANCH_NAME: {
                    c.HISTORY_DICT_KEY: {
                        c.INITIAL_COMMIT_DICT_KEY: commit_identifier,
                        c.LATEST_COMMIT_DICT_KEY: commit_identifier,
                        c.LATEST_COMMIT_NUMBER_DICT_KEY: c.INITIAL_COMMIT_NUMBER,
                        c.COMMIT_ORDER_DICT_KEY: {
                            c.INITIAL_COMMIT_NUMBER_DICT_KEY: commit_identifier
                        },
                    },
                    c.LOG_DICT_KEY: {
                        commit_identifier: {
                            c.TIMESTAMP_DICT_KEY: c.PROGRAM_START_TIME,
                            c.AUTHOR_DICT_KEY: c.COMMIT_AUTHOR_TEMPLATE.format(
                                name=name, email=email
                            ),
                            c.MESSAGE_DICT_KEY: c.INIT_COMMIT_MESSAGE,
                        }
                    },
                    c.BYTE_HASH_DICT_KEY: {
                        commit_identifier: hashlib.sha256(
                            (ri.document_html()).encode(c.UTF_8)
                        ).hexdigest()
                    },
                }
            },
            c.COMMIT_MESSAGES_DICT_KEY: {commit_identifier: c.INIT_COMMIT_MESSAGE},
            c.CURRENT_BRANCH_DICT_KEY: c.DEFAULT_BRANCH_DATA,
        }
    )


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    document_path = Path(utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX))
    repository_root = document_path.with_suffix(c.EMPTY_STRING)
    repository_name = repository_root.name
    utils.run_command(
        main,
        document_path,
        RepositoryIO(repository_root, repository_name, c, target),
        RepositoryPaths(repository_root, repository_name, c, target),
        RepositoryStatus(repository_root, repository_name, c, target),
        RepositoryWrite(repository_root, repository_name, c, target),
    )
