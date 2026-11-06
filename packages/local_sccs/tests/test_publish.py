from pathlib import Path
from local_sccs.constants_classes import SCCSConstants
from local_sccs.repository_layout import RepositoryData, RepositoryPaths, RepositoryStatus, RepositoryWrite, TargetBranch
import pytest

from test_constants import SCCSTestConstants
import requests
from local_sccs import publish
from unittest import mock
import io
from types import FunctionType
from local_sccs.exceptions import SCCSException
import zipfile
import shutil
import tempfile
import os

def test_publish_returns_response(
    c: SCCSConstants, tc: SCCSTestConstants, initialized_repository: Path, target: TargetBranch, monkeypatch: pytest.MonkeyPatch
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )

    response = requests.Response()
    response.status_code = 200
    response._content = b""
    
    mock_post = mock.Mock()
    mock_post.return_value = response
    monkeypatch.setattr(requests, "post", mock_post)

    buffer = io.BytesIO(tc.TEST_STRING.encode(tc.UTF_8))
    assert publish.post_repository(c, buffer, tc.NO_PATH_TEST_URL, rd, rp) == response

    mock_post.assert_called_once()
    assert mock_post.call_args[0][0] == tc.NO_PATH_TEST_URL
    assert mock_post.call_args.kwargs["files"] == [
        (
            c.POST_FILE_FIELD_NAME,
            (
                str(Path(rp.repository_name).with_suffix(c.ZIP_EXTENSION)),
                buffer,
                c.CONTENT_TYPE_ZIP,
            ),
        ),
    ]


def test_pull_raises_exception_on_request_failure(
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

    monkeypatch.setattr(requests, "post", raise_exception)

    buffer = io.BytesIO(tc.TEST_STRING.encode(tc.UTF_8))
    
    with pytest.raises(SCCSException) as e:
        publish.post_repository(c, buffer, tc.NO_PATH_TEST_URL, rd, rp)
    assert str(e.value) == tc.HTTP_REQUEST_ERROR_MESSAGE


def test_zip_current_directory_zips_files(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )

    monkeypatch.setattr(SCCSConstants, "WALK_ROOT", str(initialized_repository))

    buffer = publish.zip_current_directory(c)

    with zipfile.ZipFile(buffer, "r") as zf:
        path_zip = [
            Path("/" + i).relative_to(initialized_repository)
            for i in zf.namelist()
        ]

    assert set(path_zip) == {
        Path(tc.TEST_DOCUMENT_FILENAME),
        Path(tc.SCCS_DIRECTORY) / tc.METADATA_JSON,
        Path(tc.SCCS_DIRECTORY)
        / tc.OBJECTS_DIRECTORY
        / tc.HTML_DIRECTORY
        / (tc.TEST_COMMIT_IDENTIFIER + tc.HTML_EXTENSION),
        Path(tc.SCCS_DIRECTORY)
        / tc.OBJECTS_DIRECTORY
        / tc.VIEW_HTML_DIRECTORY
        / (tc.TEST_COMMIT_IDENTIFIER + tc.HTML_EXTENSION),
        Path(tc.SCCS_DIRECTORY)
        / tc.OBJECTS_DIRECTORY
        / tc.DOCUMENT_DIRECTORY
        / (tc.TEST_COMMIT_IDENTIFIER + tc.DOCUMENT_EXTENSION),
    }
    

@pytest.mark.parametrize(
    "module, function, error_message",
    [
        (io, "BytesIO", SCCSTestConstants.ZIP_BUFFER_CREATION_FAILED_ERROR_MESSAGE),
        (zipfile, "ZipFile", SCCSTestConstants.ZIPPING_FILE_ERROR_MESSAGE),
    ]
)
def test_zip_current_directory_raises_exception_failure(
    initialized_repository: Path,
    c: SCCSConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    module: str,
    function: str,
    error_message: str,
) -> None:

    monkeypatch.setattr(SCCSConstants, "WALK_ROOT", str(initialized_repository))
    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        publish.zip_current_directory(c)
    assert str(e.value) == error_message


def test_zip_current_directory_raises_exception_on_seek_failure(
    initialized_repository: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:

    monkeypatch.setattr(SCCSConstants, "WALK_ROOT", str(initialized_repository))
    class FailingSeekBytesIO(io.BytesIO):
        def seek(self, *args, **kwargs) -> None: #pyright: ignore[reportIncompatibleMethodOverride]
            raise_exception()

    monkeypatch.setattr(io, "BytesIO", FailingSeekBytesIO)

    with pytest.raises(SCCSException) as e:
        publish.zip_current_directory(c)
    assert str(e.value) == tc.ZIP_BUFFER_SEEK_ERROR_MESSAGE


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
def test_publish_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    missing_resource_name: str,
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
        publish.main(c, rd, rp, rs, rw)

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
        publish.main(c, rd, rp, rs, rw)

    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE


@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_publish_main_staged_repository_creation_fails(
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

    monkeypatch.setattr(publish, "post_repository", lambda *args, **kwargs: requests.Response())

    with pytest.raises(SCCSException) as e:
        publish.main(c, rd, rp, rs, rw)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        initialized_repository.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


def test_publish_main_prints_success_message(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
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

    response = requests.Response()
    response.status_code = 200
    response._content = b""
    
    mock_post = mock.Mock()
    mock_post.return_value = response
    monkeypatch.setattr(requests, "post", mock_post)

    publish.main(c, rd, rp, rs, rw)

    assert capsys.readouterr().out == tc.STATUS_CODE_MESSAGE_TEMPLATE.format(
        status_code=response.status_code
    ) + tc.PUBLISH_SUCCESS_MESSAGE_TEMPLATE.format(
        status_code=response.status_code,
        url=tc.PUBLISH_ENDPOINT_TEMPLATE.format(base_url=rd.base_repository_url()),
    )


def test_publish_main_resets_target_on_error(
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
        publish.main(c, rd, rp, rs, rw)

    assert target.get() is None


@pytest.mark.parametrize(
    "status_code, error_raised",
    [
        (400, True),
        (404, True),
        (500, True),
        (200, False),
    ]
)
def test_publish_main_raises_for_4xx_or_5xx_response(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
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

    response = requests.Response()
    response.status_code = status_code
    response._content = b""
    
    mock_post = mock.Mock()
    mock_post.return_value = response
    monkeypatch.setattr(requests, "post", mock_post)

    if error_raised:
        with pytest.raises(SCCSException) as e:
            publish.main(c, rd, rp, rs, rw)
        assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE
    else:
        publish.main(c, rd, rp, rs, rw)

def test_publish_main_sets_current_branch_to_main(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
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

    response = requests.Response()
    response.status_code = 200

    monkeypatch.setattr(publish, "post_repository", lambda *args, **kwargs: response)

    publish.main(c, rd, rp, rs, rw)

    assert rd.current_branch() == c.MAIN_BRANCH_NAME