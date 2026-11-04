from local_sccs import switch
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
import pytest
from test_constants import SCCSTestConstants
from local_sccs.repository_layout import (
    RepositoryData, RepositoryPaths, RepositoryStatus, RepositoryWrite, TargetBranch
)
from pathlib import Path
import shutil
import tempfile
import os
import json
from types import FunctionType

@pytest.mark.parametrize(
    ("branch_to_switch"),
    [
        ("test"),
        ("main"),
    ],
)
def test_print_switch_success_message_prints_expected_message(
    c: SCCSConstants, tc: SCCSTestConstants, branch_to_switch: str, capsys: pytest.CaptureFixture[str]
) -> None:
    switch.print_switch_success_message(c, branch_to_switch)
    
    assert capsys.readouterr().out == tc.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(
        branch_name=branch_to_switch
    )


def test_validate_branch_to_switch_raises_for_empty_branch_name(
    c: SCCSConstants, tc: SCCSTestConstants, target: TargetBranch
) -> None:

    rs = RepositoryStatus(
        Path(tc.TEST_DOCUMENT_REPOSITORY_NAME), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    
    with pytest.raises(Exception) as e:
        switch.validate_branch_to_switch(c, tc.EMPTY_STRING, rs)

    assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
        field=tc.BRANCH_NAME_FIELD_NAME
    )

@pytest.mark.parametrize(
    ("branch_to_switch, error_raised"),
    [
        ("test", True),
        ("nonexistent", True),
        ("main", False),
    ],
)
def test_validate_branch_to_switch_raises_correctly(
    c: SCCSConstants, tc: SCCSTestConstants, branch_to_switch: str, error_raised: bool, initialized_repository: Path, target: TargetBranch
) -> None:

    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    if error_raised:    
        with pytest.raises(Exception) as e:
            switch.validate_branch_to_switch(c, branch_to_switch, rs)

        assert str(e.value) == tc.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
            branch_name=branch_to_switch
        )
    else:
        switch.validate_branch_to_switch(c, branch_to_switch, rs)


def test_validate_commit_identifier_raises_for_missing_commit_file(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    initialized_repository: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch
) -> None:

    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(Path, "is_file", lambda *args, **kwargs: False)

    with pytest.raises(Exception) as e:
        switch.validate_commit_identifier(c, tc.MAIN_BRANCH_NAME, rd, rs)

    assert str(e.value) == tc.SWITCH_COMMIT_FILE_MISSING_ERROR_MESSAGE_TEMPLATE.format(
        branch_name=tc.MAIN_BRANCH_NAME
    )


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
def test_switch_main_raises_for_each_missing_resource(
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
    rw = RepositoryWrite(
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
        switch.main(c, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_switch_main_raises_for_uncommitted_changes(
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants
) -> None:
    rd = RepositoryData(
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
        switch.main(c, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)

    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE


def test_switch_main_raises_for_empty_branch_name(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants
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
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        switch.main(c, tc.EMPTY_STRING, rd, rp, rs, rw)

    assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
        field=tc.BRANCH_NAME_FIELD_NAME
    )

@pytest.mark.parametrize(
    ("branch_to_switch, error_raised"),
    [
        ("test", True),
        ("nonexistent", True),
        ("main", False),
    ],
)
def test_switch_main_raises_correctly_for_branch_to_switch(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    branch_to_switch: str,
    error_raised: bool
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
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    if error_raised:
        with pytest.raises(SCCSException) as e:
            switch.main(c, branch_to_switch, rd, rp, rs, rw)

        assert str(e.value) == tc.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(
            branch_name=branch_to_switch
        )
    
    else:
        switch.main(c, branch_to_switch, rd, rp, rs, rw)


def test_switch_main_raises_for_missing_commit_file(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    initialized_repository: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch
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
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    class DummyPath:
        def is_file(self) -> bool:
            return False

    monkeypatch.setattr(
        RepositoryData, "commit_identifier_to_full_path", lambda *args, **kwargs: DummyPath()
    )

    with pytest.raises(Exception) as e:
        switch.main(c, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)

    assert str(e.value) == tc.SWITCH_COMMIT_FILE_MISSING_ERROR_MESSAGE_TEMPLATE.format(
        branch_name=tc.MAIN_BRANCH_NAME
    )


@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_commit_main_staged_repository_creation_fails(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    function: str,
    raise_exception: FunctionType
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
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        switch.main(c, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        initialized_repository.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


def test_switch_main_sets_current_branch(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants
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
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    rw.target.set(tc.MAIN_BRANCH_NAME)
    rw.add_branch_metadata(
        tc.TEST_STRING
    )

    assert rd.current_branch() != tc.MAIN_BRANCH_NAME

    switch.main(c, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)

    assert rd.current_branch() == tc.MAIN_BRANCH_NAME


def test_switch_main_prints_switch_success_message(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
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
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    rw.target.set(tc.MAIN_BRANCH_NAME)
    rw.add_branch_metadata(
        tc.TEST_STRING
    )

    switch.main(c, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)
    assert capsys.readouterr().out == tc.SWITCH_SUCCESS_MESSAGE_TEMPLATE.format(
        branch_name=tc.MAIN_BRANCH_NAME
    )


def test_switch_main_resets_target_on_error(
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
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)

    with pytest.raises(SCCSException):
        switch.main(c, tc.TEST_STRING, rd, rp, rs, rw)

    assert target.get() is None


def test_switch_main_switches_branch_in_metadata(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants
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
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    rw.target.set(tc.MAIN_BRANCH_NAME)
    rw.add_branch_metadata(
        tc.TEST_STRING
    )

    switch.main(c, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)

    with open(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r") as f:
        assert json.load(f) == tc.METADATA_AFTER_BRANCH_SWITCH
