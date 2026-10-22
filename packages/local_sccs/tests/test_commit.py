from typing import NoReturn
from local_sccs import commit
import pytest
from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import RepositoryIO
from test_constants import SCCSTestConstants
from local_sccs.constants_classes import SCCSConstants
from local_sccs.repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryStatus,
    RepositoryWrite
)
from pathlib import Path
import shutil
import filecmp
import json
import tempfile
import os

@pytest.mark.parametrize("commit_hash,expected_identifier", [
    (
        "f797d149c9887b91ebf065685775156ac33c29ccee0cb40b68f98d715114fe45",
        "f797d149c9"
    ),
    ("a" * 64, "a" * 10),
    ("abc", "abc"),
])
def test_print_commit_success_message(
    capsys: pytest.CaptureFixture[str],
    tc: SCCSTestConstants,
    c: SCCSConstants,
    commit_hash: str,
    expected_identifier: str
) -> None:
    commit.print_commit_success_message(c, commit_hash)

    assert capsys.readouterr().out == tc.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(
        commit_identifier=expected_identifier
    )


def test_commit_main_raises_if_commit_message_is_empty(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    initialized_repository: Path,
    target: TargetBranch
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        commit.main(c, tc.EMPTY_STRING, rd, rs, rw)


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
def test_commit_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    missing_resource_path_name: str,
    expected_reported_resource_path_name: str,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
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
        commit.main(c, tc.TEST_STRING, rd, rs, rw)

    assert str(e.value) == c.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_commit_main_creates_commit_and_updates_metadata(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    metadata_path = (
        repository_with_multiple_commits
        / tc.SCCS_DIRECTORY
        / tc.METADATA_JSON
    )
    
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    commit.main(c, tc.TEST_STRING, rd, rs, rw)

    with open(
        repository_with_multiple_commits
        / tc.SCCS_DIRECTORY
        / tc.OBJECTS_DIRECTORY
        / tc.HTML_DIRECTORY
        / (tc.SECOND_COMMIT_HASH + tc.HTML_EXTENSION),
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        file_content = f.read()

    assert file_content == (
        tc.DEFAULT_HTML_STYLES + tc.SECOND_COMMIT_TEST_DOCUMENT_HTML
    )

    with open(
        repository_with_multiple_commits
        / tc.SCCS_DIRECTORY
        / tc.OBJECTS_DIRECTORY
        / tc.VIEW_HTML_DIRECTORY
        / (tc.SECOND_COMMIT_HASH + tc.HTML_EXTENSION),
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        file_content = f.read()

    assert file_content == (
        tc.HTML_BOILERPLATE_TEMPLATE.format(
            styles=tc.DEFAULT_HTML_STYLES, html=tc.SECOND_COMMIT_TEST_DOCUMENT_HTML
        )
    )

    assert filecmp.cmp(
        repository_with_multiple_commits
        / tc.SCCS_DIRECTORY
        / tc.OBJECTS_DIRECTORY
        / tc.DOCUMENT_DIRECTORY
        / (tc.SECOND_COMMIT_HASH + tc.DOCUMENT_EXTENSION),
        repository_with_multiple_commits / tc.TEST_DOCUMENT_FILENAME,
        shallow=False
    )

    with open(metadata_path, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        metadata = json.load(f)

    assert metadata == tc.SECOND_COMMIT_TEST_METADATA


def test_commit_main_raises_if_no_changes(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:

    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        commit.main(c, tc.TEST_STRING, rd, rs, rw)

    assert str(e.value) == c.NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE


def test_commit_main_when_updated_branches_is_missing(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    metadata_path = (
        repository_with_multiple_commits
        / tc.SCCS_DIRECTORY
        / tc.METADATA_JSON
    )

    with open(metadata_path, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        metadata = json.load(f)

    del metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY]

    with open(metadata_path, "w", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        json.dump(metadata, f, indent=tc.JSON_INDENT)

    with open(metadata_path, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        metadata = json.load(f)

    commit.main(c, tc.TEST_STRING, rd, rs, rw)

    with open(metadata_path, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        metadata = json.load(f)

    assert (
        tc.MAIN_BRANCH_NAME
        in metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY]
    )


def test_commit_main_prints_success_message(
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str],
    repository_with_multiple_commits: Path,
    target: TargetBranch,
    c: SCCSConstants
) -> None:
    
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    commit.main(c, tc.TEST_STRING, rd, rs, rw)
    
    assert capsys.readouterr().out == tc.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE.format(
        commit_identifier=tc.SECOND_COMMIT_HASH[:tc.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
    )


def test_commit_main_resets_target_on_error(
    monkeypatch: pytest.MonkeyPatch,
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    def fail_commit_changes(*args, **kwargs) -> NoReturn:
        raise SCCSException("commit failed")

    monkeypatch.setattr(RepositoryWrite, "commit_changes", fail_commit_changes)

    with pytest.raises(SCCSException):
        commit.main(c, tc.TEST_STRING, rd, rs, rw)

    assert target.get() is None


@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_commit_main_staged_repository_creation_fails(
    monkeypatch: pytest.MonkeyPatch,
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    module: object,
    function: str
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    def raise_exception(*args, **kwargs) -> NoReturn:
        raise Exception

    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException):
        commit.main(c, tc.TEST_STRING, rd, rs, rw)

    staging_dirs = list(
        repository_with_multiple_commits.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


@pytest.mark.parametrize("method", [
    "write_history", "write_log", "write_byte_hash",
    "write_commit_messages", "write_current_branch_data",
])
def test_commit_main_handles_io_errors_on_metadata_write(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    method: str
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    
    def raise_exception(*args, **kwargs) -> NoReturn:
        raise OSError
    
    monkeypatch.setattr(RepositoryIO, method, raise_exception)
    
    with pytest.raises(SCCSException):
        commit.main(c, tc.TEST_STRING, rd, rs, rw)

    assert target.get() is None

    staging_dirs = list(
        repository_with_multiple_commits.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )

    assert not staging_dirs