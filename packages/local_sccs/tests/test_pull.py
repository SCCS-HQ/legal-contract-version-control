from ast import FunctionType
import io
from token import NEWLINE
import zipfile

import pytest
import requests
from local_sccs import pull
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import RepositoryData, RepositoryPaths, RepositoryStatus, TargetBranch, RepositoryWrite
from pathlib import Path
from test_constants import SCCSTestConstants
import shutil
import tempfile
import os


def test_pull_returns_response(
    initialized_repository: Path, c: SCCSConstants, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants, target: TargetBranch
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    response = requests.Response()
    response.status_code = 200
    response._content = b"test content"

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)

    result = pull.pull(c, rd)

    assert result == response


def test_pull_raises_exception_if_request_fails(
    initialized_repository: Path, c: SCCSConstants, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants, target: TargetBranch, raise_exception: FunctionType
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    monkeypatch.setattr(requests, "post", raise_exception)

    with pytest.raises(SCCSException) as e:
        pull.pull(c, rd)
        assert str(e.value) == tc.HTTP_REQUEST_ERROR_MESSAGE


def test_update_repository_files_extracts_files_and_copies_commit_document(
    initialized_repository: Path, c: SCCSConstants, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants, target: TargetBranch
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    rd.target.set(tc.MAIN_BRANCH_NAME)

    monkeypatch.setattr(
        RepositoryData,
        "commit_identifier_to_full_path",
        lambda *args, **kwargs: initialized_repository / tc.TEST_TEXT_FILENAME,
    )

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr(tc.TEST_TEXT_FILENAME, tc.TEST_STRING)

    response = requests.Response()
    response.status_code = 200
    response._content = buffer.getvalue()

    pull.update_repository_files(c, response, rd, rp)

    with open(initialized_repository / tc.TEST_TEXT_FILENAME, "r") as f:
        assert f.read() == tc.TEST_STRING

    with open(initialized_repository / tc.TEST_DOCUMENT_FILENAME, "r") as f:
        assert f.read() == tc.TEST_STRING


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
def test_pull_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    missing_resource_name: str,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    missing_resource = getattr(rs.paths, missing_resource_name)()
    expected_reported_resource = getattr(
        rs.paths, missing_resource_name
    )()

    assert missing_resource.exists()

    if missing_resource.is_dir():
        shutil.rmtree(missing_resource)
    else:
        missing_resource.unlink()

    with pytest.raises(SCCSException) as e:
        pull.main(c, rd, rp, rs)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_pull_main_raises_is_uncommitted_changes_exist(
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        pull.main(c, rd, rp, rs)

    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE


@pytest.mark.parametrize(
    ("status_code"),
    [
        400,
        401,
        403,
        404,
        500,
        502,
        503,
    ],
)
def test_pull_main_raises_if_status_code_is_4xx_or_5xx(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    status_code: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    response = requests.Response()
    response.status_code = status_code
    response._content = b"test content"

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)

    with pytest.raises(SCCSException) as e:
        pull.main(c, rd, rp, rs)
    assert str(e.value) == tc.HTTP_REQUEST_ERROR_MESSAGE


@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_pull_main_raises_if_staged_repository_creation_fails(
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
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: requests.Response())
    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        pull.main(c, rd, rp, rs)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        initialized_repository.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


def test_pull_main_updates_repository_files(
    initialized_repository: Path, c: SCCSConstants, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants, target: TargetBranch
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rd.target.set(tc.MAIN_BRANCH_NAME)

    monkeypatch.setattr(
        RepositoryData,
        "commit_identifier_to_full_path",
        lambda self, *args, **kwargs: self.root / tc.TEST_TEXT_FILENAME,
    )

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr(tc.TEST_TEXT_FILENAME, tc.TEST_STRING)

    response = requests.Response()
    response.status_code = 200
    response._content = buffer.getvalue()

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)

    pull.main(c, rd, rp, rs)

    with open(initialized_repository / tc.TEST_TEXT_FILENAME, "r") as f:
        assert f.read() == tc.TEST_STRING

    with open(initialized_repository / tc.TEST_DOCUMENT_FILENAME, "r") as f:
        assert f.read() == tc.TEST_STRING


def test_pull_main_prints_success_message(
    initialized_repository: Path, c: SCCSConstants, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants, target: TargetBranch, capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rd.target.set(tc.MAIN_BRANCH_NAME)

    monkeypatch.setattr(
        RepositoryData,
        "commit_identifier_to_full_path",
        lambda self, *args, **kwargs: self.root / tc.TEST_TEXT_FILENAME,
    )


    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr(tc.TEST_TEXT_FILENAME, tc.TEST_STRING)

    response = requests.Response()
    response.status_code = 200
    response._content = buffer.getvalue()

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)

    pull.main(c, rd, rp, rs)

    assert capsys.readouterr().out.strip() == (
        tc.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=tc.STATUS_CODE_TWO_HUNDRED) + tc.NEWLINE + tc.PULL_SUCCESS_MESSAGE_TEMPLATE.format(url=tc.TEST_REPOSITORY_CLONE_URL)
    )

def test_pull_main_resets_target_branch_if_failure_occurs(
    initialized_repository: Path, c: SCCSConstants, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants, target: TargetBranch, capsys: pytest.CaptureFixture[str], raise_exception: FunctionType
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    rd.target.set(tc.MAIN_BRANCH_NAME)

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)
    with pytest.raises(SCCSException):
        pull.main(c, rd, rp, rs)

    assert rd.target.get() is None
