from typing import Any

from local_sccs.constants_classes import SCCSConstants
from test_constants import SCCSTestConstants
from local_sccs.repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite
)
from pathlib import Path
from local_sccs import branch
import json
import pytest
from local_sccs.exceptions import SCCSException
import shutil


def test_branch_create_subcommand_creates_new_branch(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    branch.branch_create_subcommand(c, tc.TEST_STRING, rd, rw)

    with open(
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON,
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE
    ) as f:
        metadata = json.load(f)

    assert tc.TEST_STRING in metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.BRANCHES_DICT_KEY]
    assert all(
        i in metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY]
        for i in [tc.TEST_STRING, tc.MAIN_BRANCH_NAME]
    )
    assert (
        tc.TEST_STRING
        == metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.CURRENT_BRANCH_DICT_KEY]
    )
    assert (
        metadata[tc.BRANCHES_DICT_KEY][tc.TEST_STRING]
        == metadata[tc.BRANCHES_DICT_KEY][tc.MAIN_BRANCH_NAME]
    )

    assert capsys.readouterr().out == tc.BRANCH_CREATE_SUCCESS_MESSAGE


def test_branch_delete_subcommand_deletes_branch(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    target.set(tc.MAIN_BRANCH_NAME)
    rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)

    branch_to_remove = tc.TEST_STRING
    branch.branch_delete_subcommand(c, branch_to_remove, rd, rw)

    with open(
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON,
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE
    ) as f:
        metadata = json.load(f)

    assert branch_to_remove not in metadata[tc.BRANCHES_DICT_KEY]
    assert branch_to_remove not in metadata[tc.CURRENT_BRANCH_DICT_KEY][
        tc.BRANCHES_DICT_KEY
    ]
    assert branch_to_remove not in metadata[tc.CURRENT_BRANCH_DICT_KEY][
        tc.UPDATED_BRANCHES_DICT_KEY
    ]
    assert (
        metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.CURRENT_BRANCH_DICT_KEY]
        == tc.MAIN_BRANCH_NAME
    )

    assert capsys.readouterr().out == tc.BRANCH_DELETE_SUCCESS_MESSAGE


def test_branch_delete_subcommand_raises_if_branch_to_remove_is_main(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        branch.branch_delete_subcommand(c, tc.MAIN_BRANCH_NAME, rd, rw)
    assert str(e.value) == tc.DELETING_MAIN_ERROR_MESSAGE


def test_branch_list_subcommand_lists_all_branches(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    rw.target.set(tc.MAIN_BRANCH_NAME)

    rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)

    branch.branch_list_subcommand(c, rd)

    assert capsys.readouterr().out == tc.TEST_BRANCH_LIST_MESSAGE


def test_run_specified_subcommand_runs_create_subcommand(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    branch.run_specified_subcommand(
        c, tc.BRANCH_CREATE_SUBCOMMAND, tc.TEST_STRING, rd, rw
    )

    with open(
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON,
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE
    ) as f:
        metadata = json.load(f)

    assert tc.TEST_STRING in metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.BRANCHES_DICT_KEY]
    assert all(
        i in metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY]
        for i in [tc.TEST_STRING, tc.MAIN_BRANCH_NAME]
    )
    assert (
        tc.TEST_STRING
        == metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.CURRENT_BRANCH_DICT_KEY]
    )
    assert (
        metadata[tc.BRANCHES_DICT_KEY][tc.TEST_STRING]
        == metadata[tc.BRANCHES_DICT_KEY][tc.MAIN_BRANCH_NAME]
    )

    assert capsys.readouterr().out == tc.BRANCH_CREATE_SUCCESS_MESSAGE


def test_run_specified_subcommand_runs_delete_subcommand(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    target.set(tc.MAIN_BRANCH_NAME)
    rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)

    branch_to_remove = tc.TEST_STRING
    branch.run_specified_subcommand(
        c, tc.BRANCH_DELETE_SUBCOMMAND, branch_to_remove, rd, rw
    )

    with open(
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON,
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE
    ) as f:
        metadata = json.load(f)

    assert branch_to_remove not in metadata[tc.BRANCHES_DICT_KEY]
    assert branch_to_remove not in metadata[tc.CURRENT_BRANCH_DICT_KEY][
        tc.BRANCHES_DICT_KEY
    ]
    assert branch_to_remove not in metadata[tc.CURRENT_BRANCH_DICT_KEY][
        tc.UPDATED_BRANCHES_DICT_KEY
    ]
    assert (
        metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.CURRENT_BRANCH_DICT_KEY]
        == tc.MAIN_BRANCH_NAME
    )

    assert capsys.readouterr().out == tc.BRANCH_DELETE_SUCCESS_MESSAGE


def test_run_specified_subcommand_runs_branch_list_subcommand(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    rw.target.set(tc.MAIN_BRANCH_NAME)

    rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)

    branch.run_specified_subcommand(c, tc.BRANCH_LIST_SUBCOMMAND, None, rd, rw)

    assert capsys.readouterr().out == tc.TEST_BRANCH_LIST_MESSAGE


@pytest.mark.parametrize(
    "subcommand, error_raised",
    [("create", True), ("delete", True), ("list", False)],
)
def test_run_specified_subcommand_raises_if_branch_name_is_none_and_create_or_delete_subcommand_is_given(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    subcommand: str,
    error_raised: bool
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    if error_raised:
        with pytest.raises(SCCSException) as e:
            branch.run_specified_subcommand(c, subcommand, None, rd, rw)
        assert str(e.value) == tc.BRANCH_NAME_MISSING_ERROR_MESSAGE
    else:
        branch.run_specified_subcommand(c, subcommand, None, rd, rw)


@pytest.mark.parametrize(
    "subcommand",
    [
        "",
        "test",
    ],
)
def test_validate_subcommand_raises_if_subcommand_is_invalid(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    subcommand: str,
) -> None:
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    with pytest.raises(SCCSException) as e:
        branch.validate_subcommand(c, subcommand, tc.MAIN_BRANCH_NAME, rs)
    assert str(e.value) == tc.INVALID_SUBCOMMAND_ERROR_MESSAGE


@pytest.mark.parametrize(
    "subcommand",
    [
        "create",
        "delete",
    ],
)
def test_validate_subcommand_raises_if_subcommand_is_create_or_delete_and_branch_name_is_empty(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    subcommand: str,
) -> None:
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    with pytest.raises(SCCSException) as e:
        branch.validate_subcommand(c, subcommand, None, rs)
    assert str(e.value) == c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
        field="branch name"
    )


@pytest.mark.parametrize(
    "branch_name, expected_message, precreate_branch",
    [
        (
            "main",
            "Branch 'main' already exists.",
            False,
        ),
        (
            "test",
            "Branch 'test' already exists.",
            True,
        ),
    ],
)
def test_validate_subcommand_raises_if_subcommand_is_create_and_branch_already_exists(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    branch_name: str,
    expected_message: str,
    precreate_branch: bool,
) -> None:
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    if precreate_branch:
        rw.target.set(tc.MAIN_BRANCH_NAME)
        rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)

    with pytest.raises(SCCSException) as e:
        branch.validate_subcommand(c, tc.BRANCH_CREATE_SUBCOMMAND, branch_name, rs)
    assert str(e.value) == expected_message


@pytest.mark.parametrize(
    "branch_name, expected_message, setup_current_branch",
    [
        (
            "test",
            "Cannot delete the current branch. Please switch to another branch first.",
            True,
        ),
        (
            "test",
            "Branch 'test' is missing from repository metadata. If the branch does not exist, please create it.",
            False,
        ),
    ],
)
def test_validate_subcommand_raises_for_delete_branch_cases(
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    branch_name: str,
    expected_message: str,
    setup_current_branch: bool,
) -> None:
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    if setup_current_branch:
        rw.target.set(tc.MAIN_BRANCH_NAME)
        rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)

    with pytest.raises(SCCSException) as e:
        branch.validate_subcommand(c, tc.BRANCH_DELETE_SUBCOMMAND, branch_name, rs)
    assert str(e.value) == expected_message


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
def test_branch_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    missing_resource_path_name: str,
    expected_reported_resource_path_name: str,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
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

    def return_string(*args: Any, **kwargs: Any) -> str:
        return tc.TEST_STRING

    monkeypatch.setattr(RepositoryData, "current_branch", return_string)

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
        branch.main(c, tc.BRANCH_CREATE_SUBCOMMAND, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_main_raises_if_uncommitted_changes_exist(
    initialized_repository: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    target: TargetBranch
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

    shutil.copy(
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )
    with pytest.raises(SCCSException) as e:
        branch.main(c, tc.BRANCH_CREATE_SUBCOMMAND, tc.MAIN_BRANCH_NAME, rd, rp, rs, rw)
    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE