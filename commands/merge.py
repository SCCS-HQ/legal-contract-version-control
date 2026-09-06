#!/usr/bin/env python3

import shutil
from pathlib import Path

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def validate_branch(c: SCCSConstants, branch: str | None, rd: RepositoryData) -> None:

    if not branch:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.BRANCH_NAME_FIELD_NAME)
        )
    if branch.lower() == rd.current_branch().lower():
        raise exceptions.SCCSException(c.CURRENT_BRANCH_MERGE_ERROR_MESSAGE)
    if branch.lower() not in (i.lower() for i in rd.branches()):
        raise exceptions.SCCSException(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch)
        )


def copy_branch_data(
    c: SCCSConstants, branch: str, rd: RepositoryData, ri: RepositoryIO
) -> None:

    ri.target.set(branch.lower())
    branch_to_merge_data = ri.read_branch_data()

    ri.target.set(rd.current_branch())
    current_branch_data = ri.read_branch_data()

    log = {
        **current_branch_data[c.LOG_DICT_KEY],
        **branch_to_merge_data[c.LOG_DICT_KEY],
    }

    byte_hash = {
        **current_branch_data[c.BYTE_HASH_DICT_KEY],
        **branch_to_merge_data[c.BYTE_HASH_DICT_KEY],
    }

    history = {
        **current_branch_data[c.HISTORY_DICT_KEY],
        **branch_to_merge_data[c.HISTORY_DICT_KEY],
    }

    commit_order = dict(
        current_branch_data[c.HISTORY_DICT_KEY][c.COMMIT_ORDER_DICT_KEY]
    )
    seen_commit_identifiers = set(commit_order.values())
    latest_commit_number = int(
        current_branch_data[c.HISTORY_DICT_KEY][c.LATEST_COMMIT_NUMBER_DICT_KEY]
    )

    source_commit_order = branch_to_merge_data[c.HISTORY_DICT_KEY][
        c.COMMIT_ORDER_DICT_KEY
    ]
    for i in sorted(source_commit_order, key=int):
        commit_identifier = source_commit_order[i]
        if commit_identifier not in seen_commit_identifiers:
            latest_commit_number += 1
            commit_order[str(latest_commit_number)] = commit_identifier
            seen_commit_identifiers.add(commit_identifier)

    history[c.COMMIT_ORDER_DICT_KEY] = commit_order
    history[c.LATEST_COMMIT_NUMBER_DICT_KEY] = latest_commit_number
    history[c.LATEST_COMMIT_DICT_KEY] = branch_to_merge_data[c.HISTORY_DICT_KEY][
        c.LATEST_COMMIT_DICT_KEY
    ]

    merged_branch_data = {
        **current_branch_data,
        c.HISTORY_DICT_KEY: history,
        c.LOG_DICT_KEY: log,
        c.BYTE_HASH_DICT_KEY: byte_hash,
    }

    ri.write_branch_data(merged_branch_data)


def copy_repository_document(
    c: SCCSConstants, branch: str, rd: RepositoryData, rp: RepositoryPaths
) -> None:

    original_target = rd.target.get()
    rd.target.set(branch.lower())

    try:
        shutil.copy2(
            rd.commit_identifier_to_full_path(
                rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
            ),
            rp.document_path(),
        )
    except Exception as e:
        raise exceptions.SCCSException(c.MERGE_DOCUMENT_COPY_ERROR_MESSAGE) from e
    finally:
        rd.target.set(original_target)


def print_merge_success_message(
    c: SCCSConstants, branch: str, rd: RepositoryData
) -> None:

    print(
        c.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(
            branch_name=branch, current_branch=rd.current_branch()
        )
    )


def main(
    c: SCCSConstants,
    branch: str,
    rd: RepositoryData,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_branch(c, branch, rd)

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        shutil.copytree(rp.root, staging_root, dirs_exist_ok=True)

        staging_ri = RepositoryIO(staging_root, ri.repository_name, c, ri.target)
        staging_rp = RepositoryPaths(staging_root, rp.repository_name, c, rp.target)
        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)

        copy_repository_document(c, branch, rd, staging_rp)

        copy_branch_data(c, branch, rd, staging_ri)

        staging_rw.commit_changes(
            c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(
                branch_name=branch, current_branch=rd.current_branch()
            ),
            allow_empty_commit=True,
        )

        utils.promote_staging(c, staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_merge_success_message(c, branch, rd)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryIO(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )
