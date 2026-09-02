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
    TargetBranch,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite
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
    c: SCCSConstants,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus
) -> None:

    rs.target.set(c.MAIN_BRANCH_NAME)

    paths = [
        rp.sccs_path(),
        rp.objects_path(),
        rp.document_objects_path(),
        rp.html_objects_path(),
        rp.view_html_objects_path()
    ]

    try:
        rp.root.mkdir(parents=True, exist_ok=True)

        for i in paths:
            (i).mkdir(parents=True, exist_ok=True)

        ri.write_metadata({})

    except Exception as e:
        raise exceptions.SCCSException(c.INIT_CREATE_ERROR_MESSAGE) from e

    rs.target.reset()


def ask_config_input(c: SCCSConstants, key: str) -> str:

    data_value = input(c.INPUT_CONFIG_VALUE_TEMPLATE.format(config_key=key)).strip()
    if not data_value:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key).capitalize()
        )

    return data_value


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


def write_starting_metadata(
        c: SCCSConstants,
        commit_identifier: str,
        name: str, email: str,
        ri: RepositoryIO
    ) -> None:

    ri.target.set(c.MAIN_BRANCH_NAME)

    ri.write_metadata(
        {
            c.BRANCHES_DICT_KEY: {
                c.MAIN_BRANCH_NAME: {
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
                    c.BYTE_HASH_DICT_KEY: {
                        commit_identifier: hashlib.sha256(
                            (ri.document_html()).encode(c.UTF_8)
                        ).hexdigest()
                    },
                }
            },
            c.COMMIT_MESSAGES_DICT_KEY: {commit_identifier: c.INIT_COMMIT_MESSAGE},
            c.CURRENT_BRANCH_DICT_KEY: c.DEFAULT_BRANCH_DATA
        }
    )

    print({                    
        c.BYTE_HASH_DICT_KEY: {
            commit_identifier: hashlib.sha256(
                (ri.document_html()).encode(c.UTF_8)
            ).hexdigest()
        },
    })


def move_document_to_repository_directory(
    repository_path: Path, document_path: Path
) -> None:

    shutil.move(document_path, repository_path)


def print_init_success_message(c: SCCSConstants) -> None:

    print(c.INIT_SUCCESS_MESSAGE)


def main(
    c: SCCSConstants,
    document_path: Path,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite
) -> None:
    
    validate_no_prev_init(c, rp)

    validate_file_requirements(c, document_path)

    name = ask_config_input(c, c.NAME_KEY)
    email = ask_config_input(c, c.EMAIL_KEY)

    create_sccs_directory_layout(c, ri, rp, rs)

    commit_identifier = create_commit_identifier(c, name, email)

    copy_document_to_objects_as_document_and_html(
        c, document_path, commit_identifier, rp
    )

    move_document_to_repository_directory(rp.root, document_path)

    write_starting_metadata(c, commit_identifier, name, email, ri)

    rw.write_key_to_config(c.NAME_KEY, name, ri.read_config())
    rw.write_key_to_config(c.EMAIL_KEY, email, ri.read_config())

    print_init_success_message(c)


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    document_path = Path(utils.entered_argument(c, 2))
    repository_root = document_path.with_suffix(c.EMPTY_STRING)
    utils.run_command(
        main,
        document_path,
        RepositoryIO(repository_root, c, target),
        RepositoryPaths(repository_root, c, target),
        RepositoryStatus(repository_root, c, target),
        RepositoryWrite(repository_root, c, target)
    )
