import os
from pathlib import Path
import shutil
import tempfile
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,    
)
from local_sccs.exceptions import SCCSException

from local_sccs.constants_classes import SCCSConstants
from test_constants import SCCSTestConstants
import pytest
from local_sccs import revert, utils
from types import FunctionType

@pytest.mark.parametrize(
    "commit_identifier, new_commit_identifier",
    [
        ("test", "new_test"),
        ("1234567890abcdef", "fedcba0987654321"),
        ("a" * 40, "b" * 40),
    ]
)
def test_revert_prints_revert_success_message(
    c: SCCSConstants, commit_identifier: str, new_commit_identifier: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test that the revert function prints the correct success message.
    """

    revert.print_revert_success_message(c, commit_identifier, new_commit_identifier)

    assert (
        capsys.readouterr().out
        == c.REVERT_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=commit_identifier[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
            new_commit_identifier=new_commit_identifier[
                : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
            ],
        )
        + "\n"
    )


def test_revert_raises_if_commit_file_does_not_exist(tc: SCCSTestConstants, c: SCCSConstants, tmp_path: Path) -> None:

    commit_path = tmp_path / tc.TEST_STRING
    staging_root = tmp_path / tc.TEST_STAGING_ROOT

    with pytest.raises(Exception) as e:
        revert.revert(c, commit_path, staging_root, tc.TEST_DOCUMENT_REPOSITORY_NAME)
    
    assert str(e.value) == tc.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
        file_name=commit_path.stem
    )


def test_revert_raises_if_copy_fails(tc: SCCSTestConstants, c: SCCSConstants, tmp_path: Path, raise_exception: FunctionType, monkeypatch: pytest.MonkeyPatch) -> None:

    commit_path = tmp_path / tc.TEST_STRING
    staging_root = tmp_path / tc.TEST_STAGING_ROOT
    
    commit_path.write_text(tc.TEST_STRING)

    monkeypatch.setattr(shutil, "copy2", raise_exception)

    with pytest.raises(Exception) as e:
        revert.revert(c, commit_path, staging_root, tc.TEST_DOCUMENT_REPOSITORY_NAME)
    
    assert str(e.value) == tc.REVERT_COPY_ERROR_MESSAGE


def test_revert_copies_commit_file_to_staging(tc: SCCSTestConstants, c: SCCSConstants, tmp_path: Path) -> None:

    commit_path = tmp_path / tc.TEST_STRING
    staging_root = tmp_path / tc.TEST_STAGING_ROOT
    destination_path = (staging_root / tc.TEST_DOCUMENT_REPOSITORY_NAME).with_suffix(c.DOCUMENT_EXTENSION)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    
    commit_path.write_text(tc.TEST_STRING)

    revert.revert(c, commit_path, staging_root, tc.TEST_DOCUMENT_REPOSITORY_NAME)

    assert destination_path.read_text() == tc.TEST_STRING



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
def test_revert_main_raises_for_each_missing_resource(
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
        revert.main(c, tc.TEST_COMMIT_HASH, rd, rp, rs, rw)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_revert_main_raises_if_commit_identifier_is_invalid_length(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
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
        revert.main(c, tc.TEST_STRING, rd, rp, rs, rw)

    assert str(e.value) == tc.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE

@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (os, "rename"), (shutil, "copytree")]
)
def test_revert_main_staged_repository_creation_fails(
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

    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        revert.main(c, tc.TEST_COMMIT_HASH, rd, rp, rs, rw)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        initialized_repository.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


def test_revert_main_prints_success_message(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(utils, "create_commit_identifier", lambda *args, **kwargs: tc.TEST_COMMIT_HASH)

    revert.main(c, tc.TEST_COMMIT_HASH, rd, rp, rs, rw)

    assert (capsys.readouterr().out).startswith(
        tc.REVERT_SUCCESS_MESSAGE_TEMPLATE.format(
            commit_identifier=tc.TEST_COMMIT_HASH[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
            new_commit_identifier=tc.TEST_COMMIT_HASH[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
        )
    )


def test_revert_main_resets_target_branch(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    revert.main(c, tc.TEST_COMMIT_HASH, rd, rp, rs, rw)

    assert target.get() is None

# test_revert_main_reverts_to_specified_commit

def test_revert_main_reverts_to_specified_commit(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rp = RepositoryPaths(repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    rs = RepositoryStatus(repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with open(rs.paths.document_path(), "rb") as f:
        original_content = f.read()

    revert.main(c, tc.TEST_COMMIT_HASH, rd, rp, rs, rw)

    with open(rs.paths.document_path(), "rb") as f:
        reverted_content = f.read()

    assert original_content != reverted_content

    with open(
        rs.paths.objects_path() / tc.DOCUMENT_DIRECTORY / (tc.TEST_COMMIT_HASH + tc.DOCUMENT_EXTENSION), "rb"
    ) as f:
        commit_content = f.read()

    assert reverted_content == commit_content

