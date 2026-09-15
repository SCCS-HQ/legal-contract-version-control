#!/usr/bin/env python3

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


def copy_branch_data(
    c: SCCSConstants, branch: str, rd: RepositoryData, ri: RepositoryIO
) -> None:
    """
    Merge the history, log, and byte hash data of the entered branch into the current
    branch and write the merged data to the current branch metadata.
    """

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
            latest_commit_number += c.COMMIT_NUMBER_INCREMENT
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

def main(
    c: SCCSConstants,
    branch: str,
    rd: RepositoryData,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the merge command by setting the current branch as the target, validating the
    repository layout and entered branch, and merging the branch into the current branch
    on a copy of the repository in a staging directory.

    Commit the merged document, promote the staging directory to the repository root,
    print a success message, and reset the target branch when the operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    rs.raise_for_uncommitted_changes()

    validate_branch(c, branch, rs)

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:

        staging_ri = RepositoryIO(staging_root, ri.repository_name, c, ri.target)
        staging_rp = RepositoryPaths(staging_root, rp.repository_name, c, rp.target)
        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)

        utils.copy_latest_commit_document(
            rd,
            branch,
            staging_rp.document_path(),
            c.MERGE_DOCUMENT_COPY_ERROR_MESSAGE,
        )

        copy_branch_data(c, branch, rd, staging_ri)

        staging_rw.commit_changes(
            c.MERGE_COMMIT_MESSAGE_TEMPLATE.format(
                branch_name=branch, current_branch=rd.current_branch()
            ),
            allow_empty_commit=True,
        )

    print_merge_success_message(c, branch, rd)

    rs.target.reset()

def print_merge_success_message(
    c: SCCSConstants, branch: str, rd: RepositoryData
) -> None:
    """
    Print a success message indicating that the entered branch has been merged into the
    current branch.
    """

    print(
        c.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(
            branch_name=branch, current_branch=rd.current_branch()
        )
    )

def validate_branch(c: SCCSConstants, branch: str | None, rs: RepositoryStatus) -> None:
    """
    Validate the entered branch by checking that it is not empty, is not the current
    branch, and exists in the repository. Raise an SCCSException if any validation
    fails.
    """

    utils.raise_if_empty(c, branch, c.BRANCH_NAME_FIELD_NAME)

    if rs.is_current_branch(branch):
        raise exceptions.SCCSException(c.CURRENT_BRANCH_MERGE_ERROR_MESSAGE)

    if not rs.branch_exists(branch):
        raise exceptions.SCCSException(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(branch_name=branch)
        )


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryIO(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )
