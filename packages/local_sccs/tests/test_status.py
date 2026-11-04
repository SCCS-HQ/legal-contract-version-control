from typing import Any
from types import FunctionType

from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
import pytest
from pathlib import Path
from test_constants import SCCSTestConstants
from local_sccs.repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite
)
from local_sccs import status
import shutil

@pytest.mark.parametrize(
    "uncommitted_changes, expected_message",
    [
        (True, SCCSTestConstants.UNCOMMITTED_CHANGES_FOUND),
        (False, SCCSTestConstants.NO_UNCOMMITTED_CHANGES),
    ],
)
def test_print_status_success_message_prints_success_message(
    capsys: pytest.CaptureFixture[str],
    uncommitted_changes: bool,
    expected_message: str,
    c: SCCSConstants
) -> None:
    """
    Test that the print_status_success_message function prints the correct success message
    based on whether uncommitted changes were detected.
    """

    status.print_status_success_message(c, uncommitted_changes)

    captured = capsys.readouterr()
    assert captured.out.strip() == expected_message


@pytest.mark.parametrize(
    ("missing_resource_path_name", "expected_reported_resource_path_name"),
    [
        ("view_html_objects_path", "view_html_objects_path"),
        ("html_objects_path", "html_objects_path"),
        ("sccs_path", "sccs_path"),
        ("document_objects_path", "document_objects_path"),
        ("document_path", "document_path"),
        ("metadata_path", "metadata_path"),
        ("objects_path", "objects_path")
    ],
)
def test_status_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    missing_resource_path_name: str,
    expected_reported_resource_path_name: str,
) -> None:

    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    missing_resource = getattr(rs.paths, missing_resource_path_name)()
    expected_reported_resource = getattr(
        rs.paths, expected_reported_resource_path_name
    )()

    assert missing_resource.exists()

    if missing_resource.is_dir():
        shutil.rmtree(missing_resource)
    else:
        missing_resource.unlink()

    with pytest.raises(SCCSException) as e:
        status.main(c, rd, rs)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )

def test_status_main_prints_success_message_for_no_uncommitted_changes(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    status.main(c, rd, rs)
    
    assert capsys.readouterr().out.strip() == tc.NO_UNCOMMITTED_CHANGES


def test_status_main_prints_success_message_for_uncommitted_changes(
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    status.main(c, rd, rs)
    
    assert capsys.readouterr().out.strip() == tc.UNCOMMITTED_CHANGES_FOUND


def test_status_main_resets_target_on_error(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)

    with pytest.raises(Exception):
        status.main(c, rd, rs)

    assert target.get() is None