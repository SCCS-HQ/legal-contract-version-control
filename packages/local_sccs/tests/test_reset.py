from posixpath import exists
from types import FunctionType

import pytest
from local_sccs import reset
from local_sccs.constants_classes import SCCSConstants
from test_constants import SCCSTestConstants
from pathlib import Path
from local_sccs.repository_layout import RepositoryData, RepositoryPaths, RepositoryStatus, TargetBranch
from local_sccs.exceptions import SCCSException
import shutil
import tempfile
import os
import filecmp


def test_print_reset_success_message_prints_success_message(
    capsys: pytest.CaptureFixture[str], c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    """
    Test that the print_reset_success_message function prints the correct success message.
    """

    reset.print_reset_success_message(c)
    
    assert capsys.readouterr().out == tc.RESET_SUCCESS_MESSAGE

@pytest.mark.parametrize(
    ("missing_resource_path_name", "expected_reported_resource_path_name"),
    [
        ("view_html_objects_path", "view_html_objects_path"),
        ("html_objects_path", "html_objects_path"),
        ("sccs_path", "view_html_objects_path"),
        ("document_objects_path", "document_objects_path"),
        ("document_path", "document_path"),
        ("metadata_path", "metadata_path"),
    ],
)
def test_reset_main_raises_for_each_missing_resource(    
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    missing_resource_path_name: str,
    expected_reported_resource_path_name: str
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
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
        reset.main(c, rd, rp, rs)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (os, "rename")]
)
def test_reset_main_staged_repository_creation_fails(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    function: str,
    raise_exception: FunctionType
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        reset.main(c, rd, rp, rs)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        initialized_repository.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


def test_reset_main_staged_repository_cleanup_fails(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    monkeypatch.setattr(RepositoryData, "commit_identifier_to_full_path", raise_exception)

    with pytest.raises(SCCSException) as e:
        reset.main(c, rd, rp, rs)

    assert str(e.value) == tc.RESET_ERROR_MESSAGE


def test_reset_main_prints_reset_success_message(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    reset.main(c, rd, rp, rs)
    
    assert capsys.readouterr().out == tc.RESET_SUCCESS_MESSAGE


def test_reset_main_resets_target_on_error(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)

    with pytest.raises(SCCSException):
        reset.main(c, rd, rp, rs)

    assert target.get() is None

def test_reset_main_resets_repository_document_to_latest_commit(
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    initialized_repository: Path,
) -> None:

    modified_rd = RepositoryData(repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    modified_rp = RepositoryPaths(repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    modified_rs = RepositoryStatus(repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    reset.main(c, modified_rd, modified_rp, modified_rs)

    with open(initialized_repository / tc.TEST_DOCUMENT_FILENAME, "rb") as f:
        original_content = f.read()

    with open(repository_with_modified_document / tc.TEST_DOCUMENT_FILENAME, "rb") as f:
        modified_content = f.read()

    assert original_content == modified_content


def test_reset_main_resets_target_branch(
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    modified_rd = RepositoryData(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    modified_rp = RepositoryPaths(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    modified_rs = RepositoryStatus(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    latest_commit_document = (
        repository_with_modified_document
        / tc.SCCS_DIRECTORY
        / tc.OBJECTS_DIRECTORY
        / tc.DOCUMENT_DIRECTORY
        / (tc.TEST_COMMIT_HASH + tc.DOCUMENT_EXTENSION)
    )

    for i in repository_with_modified_document.rglob(tc.RGLOB_ALL_FILES_PATTERN):
        print(i)

    print((repository_with_modified_document / tc.TEST_DOCUMENT_FILENAME).exists())
    
    assert not filecmp.cmp(
        repository_with_modified_document / tc.TEST_DOCUMENT_FILENAME,
        latest_commit_document,
        shallow=False,
    )

    reset.main(c, modified_rd, modified_rp, modified_rs)
    
    assert filecmp.cmp(
        repository_with_modified_document / tc.TEST_DOCUMENT_FILENAME,
        latest_commit_document,
        shallow=False,
    )