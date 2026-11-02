from local_sccs.exceptions import SCCSException
import local_sccs.utils as utils
from local_sccs.constants_classes import SCCSConstants
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
)


def print_reset_success_message(c: SCCSConstants) -> None:
    """
    Print a success message after a successful reset operation.
    """

    print(c.RESET_SUCCESS_MESSAGE)


def main(
    c: SCCSConstants,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
) -> None:
    """
    Run the reset command by setting the current branch as the target, validating the
    repository layout, and restoring the latest commit document on a copy of the
    repository in a staging directory.

    Promote the staging directory to the repository root, print a success message, and
    reset the target branch when the operation completes.
    """

    try:
        rs.validate_repository_layout()
        rs.target.set(rd.current_branch())

        with utils.staged_repository(c, rp.root, rp.root) as staging_root:
            rd.copy_latest_commit_document(
                rd.current_branch(),
                staging_root / rd.paths.document_path().name,
                c.RESET_ERROR_MESSAGE,
            )

        print_reset_success_message(c)
    except SCCSException:
        raise
    except Exception as e:
        raise SCCSException(c.STAGED_REPOSITORY_ERROR_MESSAGE) from e
    finally:
        rs.target.reset()
