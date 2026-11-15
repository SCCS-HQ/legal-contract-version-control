from avora.constants_classes import AvoraConstants
from avora.exceptions import AvoraException
from avora.repository_layout import (
    RepositoryData,
    RepositoryStatus,
)


def print_status_success_message(c: AvoraConstants, uncommitted_changes: bool) -> None:
    """
    Print the status of the current document based on whether uncommitted changes were
    detected.
    """

    if uncommitted_changes:
        print(c.UNCOMMITTED_CHANGES_FOUND)
    else:
        print(c.NO_UNCOMMITTED_CHANGES)


def main(c: AvoraConstants, rd: RepositoryData, rs: RepositoryStatus) -> None:
    """
    Run the status command by setting the current branch as the target, validating the
    repository layout, and printing the status of the current document.
    """

    try:
        rs.validate_repository_layout()
        rs.target.set(rd.current_branch())

        print_status_success_message(c, rs.validate_uncommitted_changes())
    except AvoraException:
        raise
    finally:
        rs.target.reset()
