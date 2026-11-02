import local_sccs.utils as utils
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryStatus,
    RepositoryWrite,
)


def print_commit_success_message(c: SCCSConstants, commit_identifier: str) -> None:
    """
    Print a success message after a successful commit operation, including the commit
    identifier of the new commit.
    """

    print(
        c.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[:c.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
        )
    )


def main(
    c: SCCSConstants,
    commit_message: str,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the commit command by validating the repository layout and commit message,
    setting the current branch as the target, and committing the changes to a copy of the
    repository in a staging directory.

    Promote the staging directory to the repository root, print a success message, and
    reset the target branch when the operation completes.
    """

    try:
        utils.raise_if_empty(c, commit_message, c.COMMIT_MESSAGE_FIELD_NAME, capitalize=True)

        rs.validate_repository_layout()

        rs.target.set(rd.current_branch())

        with utils.staged_repository(c, rd.root, rw.root, rd.root) as staging_root:
            staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
            commit_identifier = staging_rw.commit_changes(commit_message)

        print_commit_success_message(c, commit_identifier)
    except SCCSException:
        raise
    except Exception as e:
        raise SCCSException(c.STAGED_REPOSITORY_ERROR_MESSAGE) from e
    finally:
        rs.target.reset()


