import avora.utils as utils
from avora.constants_classes import AvoraConstants
from avora.exceptions import AvoraException
from avora.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
)


def print_reset_success_message(c: AvoraConstants) -> None:
    """
    Print a success message after a successful reset operation.
    """

    print(c.RESET_SUCCESS_MESSAGE)


def main(
    c: AvoraConstants,
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

        with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:
            rd.copy_latest_commit_document(
                rd.current_branch(),
                staging_root / rd.paths.document_path().name,
                c.RESET_ERROR_MESSAGE,
            )

        print_reset_success_message(c)
    except AvoraException:
        raise
    except Exception as e:
        raise AvoraException(c.STAGED_REPOSITORY_ERROR_MESSAGE) from e
    finally:
        rs.target.reset()