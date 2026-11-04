import json
import os
import shutil
import tempfile
from pathlib import Path
from types import FunctionType

import pytest
from local_sccs import merge
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)
from test_constants import SCCSTestConstants


def test_copy_branch_data_copies_branch_data(
    repository_with_multiple_branches: Path,
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    merge.copy_branch_data(c, tc.TEST_STRING, rd, ri)

    with open(
        repository_with_multiple_branches / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r"
    ) as f:
        assert json.load(f) == tc.TWO_BRANCHES_MERGED_METADATA_BEFORE_COMMIT


@pytest.mark.parametrize(
    "branch, current_branch",
    [
        ("test", "main"),
        ("main", "test"),
    ],
)
def test_print_merge_success_message_prints_success_message(
    capsys: pytest.CaptureFixture,
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    branch: str,
    current_branch: str,
) -> None:
    rd = RepositoryData(
        Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(
        RepositoryData, "current_branch", lambda *args, **kwargs: current_branch
    )

    merge.print_merge_success_message(c, branch, rd)

    assert capsys.readouterr().out.strip() == tc.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(
        branch_name=branch, current_branch=current_branch
    )


def test_merge_main_raises_if_branch_is_empty(
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
    repository_with_multiple_branches: Path,
) -> None:

    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(Exception) as e:
        merge.validate_branch(c, "", rs)

    assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
        field=tc.BRANCH_NAME_FIELD_NAME
    )


def test_validate_branch_raises_if_branch_is_current_branch(
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
    repository_with_multiple_branches: Path,
) -> None:

    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(Exception) as e:
        merge.validate_branch(c, tc.MAIN_BRANCH_NAME, rs)

    assert str(e.value) == tc.CURRENT_BRANCH_MERGE_ERROR_MESSAGE.format(
        branch_name=tc.MAIN_BRANCH_NAME
    )


def test_validate_branch_raises_if_branch_does_not_exist(
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
    repository_with_multiple_branches: Path,
) -> None:

    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(Exception) as e:
        merge.validate_branch(c, "nonexistent_branch", rs)

    assert str(e.value) == tc.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
        branch_name="nonexistent_branch"
    )


@pytest.mark.parametrize(
    ("missing_resource_name"),
    [
        "view_html_objects_path",
        "html_objects_path",
        "sccs_path",
        "document_objects_path",
        "document_path",
        "metadata_path",
        "objects_path",
    ],
)
def test_merge_main_raises_for_each_missing_resource(
    repository_with_multiple_branches: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    missing_resource_name: str,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    missing_resource = getattr(rs.paths, missing_resource_name)()
    expected_reported_resource = getattr(rs.paths, missing_resource_name)()

    assert missing_resource.exists()

    if missing_resource.is_dir():
        shutil.rmtree(missing_resource)
    else:
        missing_resource.unlink()

    with pytest.raises(SCCSException) as e:
        merge.main(c, tc.TEST_STRING, rd, ri, rp, rs, rw)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_branch_main_raises_if_uncommitted_changes_exist(
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        merge.main(c, tc.MAIN_BRANCH_NAME, rd, ri, rp, rs, rw)
    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE


def test_validate_branch_raises_if_branch_is_empty(
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
    repository_with_multiple_branches: Path,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(Exception) as e:
        merge.main(c, "", rd, ri, rp, rs, rw)

    assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
        field=tc.BRANCH_NAME_FIELD_NAME
    )


def test_validate_branch_raises_if_branch_is_current(
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
    repository_with_multiple_branches: Path,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(Exception) as e:
        merge.main(c, tc.MAIN_BRANCH_NAME, rd, ri, rp, rs, rw)

    assert str(e.value) == tc.CURRENT_BRANCH_MERGE_ERROR_MESSAGE


def test_merge_main_raises_if_branch_does_not_exist(
    tc: SCCSTestConstants,
    c: SCCSConstants,
    target: TargetBranch,
    repository_with_multiple_branches: Path,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(Exception) as e:
        merge.main(c, tc.SECOND_TEST_STRING, rd, ri, rp, rs, rw)

    assert str(e.value) == tc.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
        branch_name=tc.SECOND_TEST_STRING
    )


@pytest.mark.parametrize(
    "module, function", [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_merge_main_staged_repository_creation_fails(
    repository_with_multiple_branches: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    function: str,
    raise_exception: FunctionType,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        merge.main(c, tc.TEST_STRING, rd, ri, rp, rs, rw)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        repository_with_multiple_branches.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )

    assert not staging_dirs


def test_merge_main_prints_success_message(
    repository_with_multiple_branches: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    merge.main(c, tc.TEST_STRING, rd, ri, rp, rs, rw)

    assert capsys.readouterr().out.strip() == tc.MERGE_SUCCESS_MESSAGE_TEMPLATE.format(
        branch_name=tc.TEST_STRING, current_branch=rd.current_branch()
    )


def test_merge_main_resets_target_branch_on_failure(
    repository_with_multiple_branches: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)

    with pytest.raises(SCCSException):
        merge.main(c, tc.TEST_STRING, rd, ri, rp, rs, rw)

    assert rs.target.get() is None


def test_merge_main_merges_branch_into_current_branch_and_commits_changes(
    repository_with_multiple_branches: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_branches, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(
        SCCSConstants,
        tc.PROGRAM_START_TIME_SCCS_CONSTANTS_ATTRIBUTE_NAME,
        tc.EPOCH_ISO_DATETIME,
    )

    merge.main(c, tc.TEST_STRING, rd, ri, rp, rs, rw)

    with open(
        repository_with_multiple_branches / tc.SCCS_DIRECTORY / tc.METADATA_JSON
    ) as f:
        assert json.load(f) == tc.TWO_BRANCHES_MERGED_METADATA_AFTER_COMMIT

    with open(repository_with_multiple_branches / tc.TEST_DOCUMENT_FILENAME, "rb") as f:
        document_bytes = f.read()

    with open(
        Path(__file__).parent
        / tc.TEST_DOCUMENTS_DIRECTORY
        / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        "rb",
    ) as f:
        assert f.read() == document_bytes
