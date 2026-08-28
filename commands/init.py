#!/usr/bin/env python3

import hashlib
import json
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
    TargetBranch,
)


def validate_no_prev_init(c: SCCSConstants, rp: RepositoryPaths) -> None:

    if (rp.sccs_path()).is_dir():
        raise exceptions.SCCSException(c.ALREADY_INIT_ERROR_MESSAGE)


def validate_file_requirements(c: SCCSConstants, file: Path) -> None:

    if file.suffix.lower() != c.DOCUMENT_EXTENSION:
        raise exceptions.SCCSException(c.INVALID_FILE_TYPE_ERROR_MESSAGE)

    if not file.is_file():
        raise exceptions.SCCSException(
            c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(file_path=file)
        )


def create_sccs_directory_layout(
    c: SCCSConstants, rp: RepositoryPaths, rs: RepositoryStatus
) -> None:

    rs.target.set(c.MAIN_BRANCH_NAME)

    paths = [
        rp.sccs_path(),
        rp.objects_path(),
        rp.document_objects_path(),
        rp.html_objects_path(),
        rp.view_html_objects_path(),
        rp.branches_path(),
        rp.branch_path(c.MAIN_BRANCH_NAME),
        rp.history_directory_path(),
        rp.byte_hash_directory_path(),
        rp.commit_messages_directory_path(),
        rp.config_directory_path(),
        rp.current_branch_directory_path(),
    ]

    try:
        rp.root.mkdir(parents=True, exist_ok=True)

        for i in paths:
            (i).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise exceptions.SCCSException(c.INIT_CREATE_ERROR_MESSAGE) from e

    rs.target.reset()


def config_inputs(c: SCCSConstants, rp: RepositoryPaths, *data: str) -> dict[str, str]:

    values = []

    for i in data:
        data_value = input(c.INPUT_CONFIG_VALUE_TEMPLATE.format(config_key=i)).strip()
        if not data_value:
            raise exceptions.SCCSException(
                c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=i)
            )
        values.append(data_value)

    with open(rp.config_path(), "w", encoding=c.UTF_8, newline=c.NEWLINE) as f:
        config = {}

        for i, value in enumerate(values):
            config_key = data[i]
            config[config_key] = value

        f.seek(0)
        json.dump(config, f, indent=4)
    return config


def create_commit_identifier(c: SCCSConstants, name: str, email: str) -> str:

    commit_identifier_parts = [
        c.PROGRAM_START_TIME,
        c.INITIAL_VERSION_COMMIT_MESSAGE,
        name,
        email,
    ]

    return hashlib.sha256(
        c.PATH_SEPARATOR.join(commit_identifier_parts).encode(c.UTF_8)
    ).hexdigest()


def copy_document_to_objects_as_document_and_html(
    c: SCCSConstants, document_path: Path, commit_identifier: str, rp: RepositoryPaths
) -> None:

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


def write_history_data(
    c: SCCSConstants,
    name: str,
    email: str,
    commit_identifier: str,
    ri: RepositoryIO,
    rs: RepositoryStatus,
) -> None:

    rs.target.set(c.MAIN_BRANCH_NAME)

    history_data = {
        c.HISTORY_DICT_KEY: {
            c.INITIAL_COMMIT_DICT_KEY: commit_identifier,
            c.LATEST_COMMIT_DICT_KEY: commit_identifier,
            c.LATEST_COMMIT_NUMBER_DICT_KEY: 1,
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
    }

    ri.write_history(history_data)

    rs.target.reset()


def write_commit_message_data(
    c: SCCSConstants, commit_identifier: str, ri: RepositoryIO
) -> None:

    commit_message_data = {commit_identifier: c.INIT_COMMIT_MESSAGE}
    ri.write_commit_messages(commit_message_data)


def write_byte_hash(
    c: SCCSConstants,
    document_path: Path,
    commit_identifier: str,
    ri: RepositoryIO,
    rs: RepositoryStatus,
) -> None:

    rs.target.set(c.MAIN_BRANCH_NAME)

    try:
        with open(document_path, "rb") as f:
            byte_hash_file = hashlib.sha256(
                mammoth.convert_to_html(f).value.encode(c.UTF_8)
            ).hexdigest()
    except Exception as e:
        raise exceptions.SCCSException(c.INIT_BYTE_HASH_DATA_ERROR_MESSAGE) from e

    byte_hash = {commit_identifier: byte_hash_file}

    ri.write_byte_hash(byte_hash)

    rs.target.reset()


def write_branch_data(c: SCCSConstants, rp: RepositoryPaths) -> None:

    try:
        with open(
            rp.current_branch_data_file_path(),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            json.dump(c.DEFAULT_BRANCH_DATA, f, indent=4)
    except Exception as e:
        raise exceptions.SCCSException(c.INIT_BRANCH_DATA_ERROR_MESSAGE) from e


def move_document_to_repository_directory(
    repository_path: Path, document_path: Path
) -> None:

    shutil.move(document_path, repository_path)


def print_init_success_message(c: SCCSConstants) -> None:

    print(c.INIT_SUCCESS_MESSAGE)


def initialize_repository(
    c: SCCSConstants,
    document_path: Path,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:
    try:
        validate_no_prev_init(c, rp)

        validate_file_requirements(c, document_path)

        create_sccs_directory_layout(c, rp, rs)

        config = config_inputs(c, rp, c.NAME_KEY, c.EMAIL_KEY)

        name = config[c.NAME_KEY]
        email = config[c.EMAIL_KEY]

        commit_identifier = create_commit_identifier(c, name, email)

        copy_document_to_objects_as_document_and_html(
            c, document_path, commit_identifier, rp
        )

        write_history_data(c, name, email, commit_identifier, ri, rs)

        write_commit_message_data(c, commit_identifier, ri)

        write_byte_hash(c, document_path, commit_identifier, ri, rs)

        write_branch_data(c, rp)

        move_document_to_repository_directory(rp.root, document_path)

    except Exception as e:
        delete_repository_after_error(rp.root, e)
        


def delete_repository_after_error(repository_path: Path, e: Exception) -> None:
    shutil.rmtree(repository_path, ignore_errors=True)
    raise exceptions.SCCSException(c.INIT_CREATE_ERROR_MESSAGE) from e


def main(
    c: SCCSConstants,
    document_path: Path,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:

    initialize_repository(c, document_path, ri, rp, rs)

    print_init_success_message(c)


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    document_path = Path(utils.entered_argument(c, 2))
    utils.run_command(
        main,
        document_path,
        RepositoryIO(document_path.with_suffix(c.EMPTY_STRING), c, target),
        RepositoryPaths(document_path.with_suffix(c.EMPTY_STRING), c, target),
        RepositoryStatus(document_path, c, target),
    )
