import avora.utils as utils
from avora.constants_classes import AvoraConstants
from avora.exceptions import AvoraException
from avora.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
)


def print_switch_success_message(c: AvoraConstants, branch_to_switch: str) -> None:
    """
    Print a success message indicating that the entered branch has been switched to.
    """

    print(c.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(branch_name=branch_to_switch))


def validate_branch_to_switch(
    c: AvoraConstants, branch_to_switch: str, rs: RepositoryStatus
) -> None:
    """
    Validate the entered branch by checking that it is not empty and exists in the
    repository. Raise an AvoraException if any validation fails.
    """

    utils.raise_if_empty(c, branch_to_switch, c.BRANCH_NAME_FIELD_NAME)

    if not rs.branch_exists(branch_to_switch):
        raise AvoraException(
            c.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch_to_switch
            )
        )


def validate_commit_identifier(
    c: AvoraConstants,
    branch_to_switch: str,
    rd: RepositoryData,
    rs: RepositoryStatus,
) -> None:
    """
    Validate the latest commit document of the entered branch by checking that it
    exists. Raise an AvoraException if the commit document is missing.
    """

    rs.target.set(branch_to_switch)

    if not rd.commit_identifier_to_full_path(
        rd.latest_commit_identifier(), c.DOCUMENT_DIRECTORY
    ).is_file():
        raise AvoraException(
            c.SWITCH_COMMIT_FILE_MISSING_ERROR_MESSAGE_TEMPLATE.format(
                branch_name=branch_to_switch
            )
        )

    rs.target.reset()


def main(
    c: AvoraConstants,
    branch_to_switch: str,
    rd: RepositoryData,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the switch command by setting the current branch as the target, validating the
    repository layout and entered branch, and copying the latest commit document of the
    branch to the repository on a copy of the repository in a staging directory.

    Set the entered branch as the current branch, promote the staging directory to the
    repository root, print a success message, and reset the target branch when the
    operation completes.
    """

    try:
        rs.validate_repository_layout()

        rs.target.set(rd.current_branch())

        rs.raise_for_uncommitted_changes()

        validate_branch_to_switch(c, branch_to_switch, rs)

        validate_commit_identifier(c, branch_to_switch, rd, rs)

        with utils.staged_repository(c, rp.root, rp.root, rp.root) as staging_root:

            rd.copy_latest_commit_document(
                branch_to_switch,
                staging_root / rd.paths.document_path().name,
                c.SWITCH_COPY_ERROR_MESSAGE,
            )

            staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)
            staging_rw.set_current_branch(branch_to_switch)

        print_switch_success_message(c, branch_to_switch)
    except AvoraException:
        raise
    except Exception as e:
        raise AvoraException(c.STAGED_REPOSITORY_ERROR_MESSAGE) from e
    finally:
        rs.target.reset()
