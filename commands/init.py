#!/usr/bin/env python3

import hashlib
import json
import shutil
from pathlib import Path
import mammoth

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryPaths, TargetBranch, RepositoryIO, RepositoryStatus
)


def config_inputs(c: SCCSConstants, rp: RepositoryPaths, *data: str) -> dict[str, str]:

    values = []

    for i in data:
        data_value = input(c.INPUT_CONFIG_VALUE_TEMPLATE.format(config_key=i)).strip()
        if not data_value:
            raise exceptions.InvalidInputError(
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


def check_for_prev_init(c: SCCSConstants, rp: RepositoryPaths) -> None:

    if (rp.sccs_path()).is_dir():
        raise exceptions.AlreadyInitializedError(c.ALREADY_INITIALIZED_ERROR_MESSAGE)


def check_file_requirements(c: SCCSConstants, file: Path) -> None:

    if file.suffix.lower() != c.DOCX_EXTENSION:
        raise exceptions.InvalidFileTypeError(c.INVALID_FILE_TYPE_ERROR_MESSAGE)

    if not file.is_file():
        raise exceptions.FileDoesNotExistError(
            c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
                file_path=file
            )
        )


def create_commit_sha_hash(c: SCCSConstants, name: str, email: str) -> str:

    hash_parts = [c.PROGRAM_START_TIME, c.INITIAL_VERSION_COMMIT_MESSAGE, name, email]

    return hashlib.sha256(
            c.PATH_SEPARATOR.join(hash_parts).encode(c.UTF_8)
        ).hexdigest()


def create_sccs_directory_layout(
    c: SCCSConstants, rs: RepositoryStatus, rp: RepositoryPaths
) -> None:

    rs.target.set(c.MAIN_BRANCH_NAME)

    paths = [
        rp.sccs_path(),
        rp.objects_path(),
        rp.docx_objects_path(),
        rp.html_objects_path(),
        rp.view_html_objects_path(),
        rp.branches_path(),
        rp.branch_path(c.MAIN_BRANCH_NAME),
        rp.history_dir_path(),
        rp.byte_hashes_dir_path(),
        rp.commit_messages_dir_path(),
        rp.config_dir_path(),
        rp.current_branch_dir_path()
    ]

    try:
        rp.root.mkdir(parents=True, exist_ok=True)

        for i in paths:
            (i).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise exceptions.FileCreateError() from e

    rs.target.reset()

def move_document_to_repo_directory(repo_path: Path, docx_path: Path) -> None:

    shutil.move(docx_path, repo_path)


def copy_document_to_objects_as_docx_and_html(
    c: SCCSConstants, docx_path: Path, sha_hash: str, rp: RepositoryPaths
) -> None:

    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f).value
    except Exception as e:
        raise exceptions.ConvertingDocumentToHTMLError() from e

    try:
        shutil.copy2(
            docx_path,
            (rp.docx_objects_path() / sha_hash).with_suffix(c.DOCX_EXTENSION),
        )
    except Exception as e:
        raise exceptions.FileCopyError() from e

    try:
        with open(
            (rp.html_objects_path() / sha_hash).with_suffix(c.HTML_EXTENSION),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            f.write(c.DEFAULT_HTML_STYLES + result)
    except Exception as e:
        raise exceptions.FileWriteError() from e

    try:
        with open(
            (rp.view_html_objects_path() / sha_hash).with_suffix(c.HTML_EXTENSION),
            "w",
            encoding=c.UTF_8,
            newline=c.NEWLINE,
        ) as f:
            f.write(utils.wrap_html(c, result, c.DEFAULT_HTML_STYLES))
    except Exception as e:
        raise exceptions.FileWriteError() from e


def write_history_data(
    c: SCCSConstants, name: str, email: str, sha_hash: str,
    rs: RepositoryStatus, ri: RepositoryIO,
) -> None:

    rs.target.set(c.MAIN_BRANCH_NAME)

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
                c.AUTHOR_DICT_KEY: c.COMMIT_AUTHOR_TEMPLATE.format(
                    name=name, email=email
                ),
                c.MESSAGE_DICT_KEY: c.INITIAL_COMMIT_MESSAGE,
            }
        },
    }

    ri.write_history(history_data)

    rs.target.reset()


def write_commit_message_data(
    c: SCCSConstants, sha_hash: str, ri: RepositoryIO
) -> None:

    commit_message_data = {
        sha_hash: c.INITIAL_COMMIT_MESSAGE
    }
    ri.write_commit_messages(commit_message_data)


def write_hashed_file_commit_data(
        c: SCCSConstants,
        docx_path: Path,
        sha_hash: str,
        rs: RepositoryStatus,
        ri: RepositoryIO
    ) -> None:

    rs.target.set(c.MAIN_BRANCH_NAME)

    try:
        with open(docx_path, "rb") as f:
            hasher = hashlib.sha256()
            while i := f.read(c.MAX_FILE_READ_SIZE):
                hasher.update(i)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        raise exceptions.DocumentHashingError() from e

    

    commit_file_hash_data = {sha_hash: hashed_file}

    ri.write_byte_hashes(commit_file_hash_data)

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
        raise exceptions.UpdatingMetadataError() from e


def delete_repository_after_error(repo_path: Path) -> None:
    shutil.rmtree(repo_path, ignore_errors=True)


def print_init_success_message(c: SCCSConstants) -> None:

    print(c.INIT_SUCCESS_MESSAGE)


def main(
    c: SCCSConstants, docx_path: Path, rs: RepositoryStatus, rp: RepositoryPaths,
    ri: RepositoryIO,
) -> None:

    try:
        check_for_prev_init(c, rp)

        check_file_requirements(c, docx_path)

        create_sccs_directory_layout(c, rs, rp)

        config = config_inputs(c, rp, c.NAME_KEY, c.EMAIL_KEY)

        name = config[c.NAME_KEY]
        email = config[c.EMAIL_KEY]

        sha_hash = create_commit_sha_hash(c, name, email)

        move_document_to_repo_directory(rp.root, docx_path)

        copy_document_to_objects_as_docx_and_html(c, docx_path, sha_hash, rp)

        write_history_data(c, name, email, sha_hash, rs, ri)

        write_commit_message_data(c, sha_hash, ri)

        write_hashed_file_commit_data(c, docx_path, sha_hash, rs, ri)

        write_branch_data(c, rp)

        print_init_success_message(c)

    except Exception:
        delete_repository_after_error(rp.root)
        raise


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        RepositoryStatus(
            Path(utils.entered_argument(2)), c, target
        ),
        RepositoryPaths(
            Path(utils.entered_argument(2)), c, target
        ),
        RepositoryIO(
            Path(utils.entered_argument(2)), c, target
        ),
    )
