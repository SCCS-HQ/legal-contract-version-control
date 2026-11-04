import os
import shutil
import tempfile
from pathlib import Path
from types import FunctionType

import pytest
from local_sccs import open as local_open
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


def test_copy_commit_file(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    commit_file = tmp_path / tc.TEST_STRING
    commit_file.write_text(tc.TEST_STRING)

    output_file_path = tmp_path / tc.TEST_TEXT_FILENAME

    local_open.copy_commit_file(c, commit_file, output_file_path)

    assert output_file_path.exists()
    assert output_file_path.read_text() == tc.TEST_STRING


def test_copy_commit_file_raises_exception(
    monkeypatch: pytest.MonkeyPatch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    raise_exception: FunctionType,
) -> None:

    monkeypatch.setattr(shutil, "copy2", raise_exception)

    try:
        local_open.copy_commit_file(c, Path(tc.TEST_STRING), Path(tc.TEST_STRING))
    except SCCSException as e:
        assert str(e) == tc.OPEN_COPY_ERROR_MESSAGE


@pytest.mark.parametrize(
    "commit_identifier, output_file_path",
    [
        ("abc123", "test.txt"),
        ("abc", "abc.html"),
        ("abc123xyz", "abc"),
        ("a" * 40, "o" * 10 + ".txt"),
    ],
)
def test_print_open_success_message(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture,
    commit_identifier: str,
    output_file_path: str,
) -> None:

    local_open.print_open_success_message(c, commit_identifier, Path(output_file_path))

    expected_output = tc.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
        commit_identifier=commit_identifier[: tc.COMMIT_IDENTIFIER_DISPLAY_LENGTH],
        output_file=output_file_path,
    )

    assert capsys.readouterr().out.strip() == expected_output


@pytest.mark.parametrize(
    "commit_identifier, error_raised",
    [
        ("1234567890", False),
        ("1" * 64, False),
        ("1" * 65, True),
        ("g1234567890", True),
        ("1" * 63 + "g", True),
        ("!1234567890", True),
        ("1" * 63 + "!", True),
    ],
)
def test_validate_commit_identifier_valid(
    initialized_repository: Path,
    target: TargetBranch,
    tc: SCCSTestConstants,
    c: SCCSConstants,
    commit_identifier: str,
    error_raised: bool,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    if error_raised:
        with pytest.raises(SCCSException) as e:
            local_open.validate_commit_identifier(c, commit_identifier, rd)
        assert str(e.value) == tc.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE
    else:
        local_open.validate_commit_identifier(c, commit_identifier, rd)


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
def test_open_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    missing_resource_name: str,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    missing_resource = getattr(rs.paths, missing_resource_name)()
    expected_reported_resource = getattr(rs.paths, missing_resource_name)()

    assert missing_resource.exists()

    if missing_resource.is_dir():
        shutil.rmtree(missing_resource)
    else:
        missing_resource.unlink()

    with pytest.raises(SCCSException) as e:
        local_open.main(c, tc.TEST_STRING, rd, rs)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_publish_main_raises_for_uncommitted_changes(
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        local_open.main(c, tc.TEST_STRING, rd, rs)

    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE


@pytest.mark.parametrize(
    "commit_identifier, error_raised",
    [
        ("ef4a6cd9a3", False),
        (SCCSTestConstants.TEST_COMMIT_IDENTIFIER, False),
        ("1" * 65, True),
    ],
)
def test_open_main_raises_for_commit_identifier_length(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    commit_identifier: str,
    error_raised: bool,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    if error_raised:
        with pytest.raises(SCCSException) as e:
            local_open.main(c, commit_identifier, rd, rs)

        assert str(e.value) == tc.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE
    else:
        local_open.main(c, commit_identifier, rd, rs)


@pytest.mark.parametrize(
    "module, function", [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_open_main_staged_repository_creation_fails(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    function: str,
    raise_exception: FunctionType,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        local_open.main(c, tc.TEST_COMMIT_IDENTIFIER, rd, rs)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        initialized_repository.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )

    assert not staging_dirs


def test_open_main_prints_success_message(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    local_open.main(c, tc.TEST_COMMIT_IDENTIFIER, rd, rs)

    assert capsys.readouterr().out.strip() == tc.OPEN_SUCCESS_MESSAGE_TEMPLATE.format(
        commit_identifier=tc.TEST_COMMIT_IDENTIFIER[
            : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
        ],
        output_file=Path(
            c.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(
                commit_identifier=tc.TEST_COMMIT_IDENTIFIER[
                    : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
                ]
            )
        ).with_suffix(c.DOCUMENT_EXTENSION),
    )


def test_open_main_resets_target_branch_on_failure(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    raise_exception: FunctionType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)

    with pytest.raises(SCCSException):
        local_open.main(c, tc.TEST_COMMIT_IDENTIFIER, rd, rs)

    assert rd.target.get() is None


def test_open_main_opens_commit(
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

    local_open.main(c, tc.TEST_COMMIT_IDENTIFIER, rd, rs)

    with open(
        initialized_repository
        / Path(
            c.OPEN_OUTPUT_FILE_NAME_TEMPLATE.format(
                commit_identifier=tc.TEST_COMMIT_IDENTIFIER[
                    : c.COMMIT_IDENTIFIER_DISPLAY_LENGTH
                ]
            )
        ).with_suffix(c.DOCUMENT_EXTENSION),
        "rb",
    ) as f:
        open_content = f.read()

    assert (
        open_content
        == rd.commit_identifier_to_full_path(
            tc.TEST_COMMIT_IDENTIFIER, c.DOCUMENT_DIRECTORY
        ).read_bytes()
    )
