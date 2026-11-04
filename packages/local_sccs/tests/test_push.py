from pathlib import Path
import shutil
import zipfile
from local_sccs.constants_classes import SCCSConstants

from types import FunctionType

from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import RepositoryData, RepositoryPaths, TargetBranch, RepositoryIO, RepositoryWrite, RepositoryStatus
from test_constants import SCCSTestConstants
import os
from local_sccs import push
import pytest
import json
import requests
import io
from unittest import mock
import tempfile


def test_snapshot_file_hard_links_src_to_dst(
    tmp_path: Path, tc: SCCSTestConstants
) -> None:
    source = tmp_path / tc.TEST_STRING
    destination = tmp_path / tc.SECOND_TEST_STRING

    source.write_text(tc.TEST_STRING)

    push.snapshot_file(source, destination)

    assert destination.exists()
    assert os.stat(source).st_ino == os.stat(destination).st_ino


def test_snapshot_file_copies_src_to_dst_on_oserror(
    tmp_path: Path, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, raise_exception: FunctionType
) -> None:
    source = tmp_path / tc.TEST_STRING
    destination = tmp_path / tc.SECOND_TEST_STRING

    source.write_text(tc.TEST_STRING)

    monkeypatch.setattr(os, "link", raise_exception)

    assert not destination.exists()

    try:
        push.snapshot_file(source, destination)
    except OSError:
        pass

    assert destination.exists()
    assert destination.read_text() == tc.TEST_STRING


def test_clear_updated_branches_clears_updated_branches(
    initialized_repository: Path, target: TargetBranch, tc: SCCSTestConstants, c: SCCSConstants
) -> None:
    ri = RepositoryIO(initialized_repository, tc.TEST_STRING, c, target)

    with open(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r+") as f:
        metadata = json.load(f)
        metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY].append(tc.TEST_STRING)
        f.seek(0)
        json.dump(metadata, f)
        f.truncate()

    push.clear_updated_branches(ri)

    with open(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r") as f:
        metadata = json.load(f)
        assert metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY] == []


def test_compare_commit_identifier_lists_returns_objects_to_upload(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    
    local_objects = ["a", "b", "c"]
    remote_objects = ["a", "b"]

    monkeypatch.setattr(RepositoryData, "repository_objects", lambda *args, **kwargs: local_objects)

    objects_to_upload = push.compare_commit_identifier_lists(c, remote_objects, rd)

    assert objects_to_upload == ["c"]


def test_compare_commit_identifier_lists_raises_exception_if_local_objects_is_missing_remote_objects(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    
    local_objects = ["a", "b"]
    remote_objects = ["a", "b", "c"]

    monkeypatch.setattr(RepositoryData, "repository_objects", lambda *args, **kwargs: local_objects)

    with pytest.raises(push.SCCSException) as e:
        push.compare_commit_identifier_lists(c, remote_objects, rd)

    assert str(e.value) == c.MISSING_REMOTE_OBJECTS_ERROR_MESSAGE


def test_fetch_remote_objects_returns_response(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    
    response = requests.Response()
    response.status_code = 200
    response._content = b"test content"

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_STRING)

    assert push.fetch_remote_objects(c, rd) == response


def test_fetch_remote_objects_raises_exception_on_request_failure(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch, raise_exception: FunctionType
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: raise_exception())
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_STRING)

    with pytest.raises(push.SCCSException) as e:
        push.fetch_remote_objects(c, rd)

    assert str(e.value) == c.PUSH_HTTP_REQUEST_ERROR_MESSAGE


def test_upload_objects_makes_post_request_of_buffer_to_remote_repository(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_REPOSITORY_URL_ENDING)

    buffer = io.BytesIO(tc.TEST_STRING.encode(tc.UTF_8))

    with mock.patch("requests.post") as mock_post:
        push.upload_objects(c, buffer, rd, rp)

        args, kwargs = mock_post.call_args
        assert kwargs["files"][0][1][1] == buffer


def test_upload_objects_raises_exception_on_request_failure(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch, raise_exception: FunctionType
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_REPOSITORY_URL_ENDING)

    monkeypatch.setattr(requests, "post", raise_exception)

    buffer = io.BytesIO(tc.TEST_STRING.encode(tc.UTF_8))

    with pytest.raises(push.SCCSException) as e:
        push.upload_objects(c, buffer, rd, rp)
    assert str(e.value) == c.PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE.format(url=tc.TEST_REPOSITORY_URL_ENDING)


def test_upload_objects_raises_exception_if_remote_has_invalid_ending(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_STRING)

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: None)

    buffer = io.BytesIO(tc.TEST_STRING.encode(tc.UTF_8))

    with pytest.raises(push.SCCSException) as e:
        push.upload_objects(c, buffer, rd, rp)
    assert str(e.value) == tc.INVALID_PATH_ENDING_ERROR_MESSAGE


def test_upload_objects_returns_response_on_success(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, target: TargetBranch
) -> None:
    rd = RepositoryData(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    response = requests.Response()
    response.status_code = 200
    response._content = b"test content"
    
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_REPOSITORY_URL_ENDING)
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)

    buffer = io.BytesIO(tc.TEST_STRING.encode(tc.UTF_8))
    
    assert push.upload_objects(c, buffer, rd, rp) == response
    

def test_zip_files_to_upload_returns_zip_archive_of_remote_objects_and_document_and_metadata_in_buffer(
    initialized_repository: Path, c: SCCSConstants, tc: SCCSTestConstants, target: TargetBranch
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    buffer = io.BytesIO()

    files_to_upload = ([
        i.resolve()
        for i in Path(initialized_repository / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY).glob("*")
        if i.is_file()
    ] + [
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    ] + [
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON
    ])

    staging_root = initialized_repository.parent / tc.TEST_STAGING_ROOT
    
    for i in files_to_upload:
        dst = staging_root / i.relative_to(rp.root)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(i, dst)

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in files_to_upload:
            snapshot_path = staging_root / i.relative_to(rp.root)
            zf.write(snapshot_path, arcname=i.relative_to(rp.root))

    buffer.seek(0)

    zip_buffer = push.zip_files_to_upload(c, [tc.TEST_COMMIT_IDENTIFIER], rd, rp)
    assert zip_buffer.getvalue() == buffer.getvalue()


def test_zip_files_to_upload_deletes_staging(
    initialized_repository: Path, c: SCCSConstants, tc: SCCSTestConstants, target: TargetBranch
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    buffer = io.BytesIO()

    files_to_upload = ([
        i.resolve()
        for i in Path(initialized_repository / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY).glob("*")
        if i.is_file()
    ] + [
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    ] + [
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON
    ])

    staging_root = initialized_repository.parent / tc.TEST_STAGING_ROOT
    
    for i in files_to_upload:
        dst = staging_root / i.relative_to(rp.root)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(i, dst)

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in files_to_upload:
            snapshot_path = staging_root / i.relative_to(rp.root)
            zf.write(snapshot_path, arcname=i.relative_to(rp.root))

    buffer.seek(0)

    push.zip_files_to_upload(c, [tc.TEST_COMMIT_IDENTIFIER], rd, rp)

    staging_dirs = list(
        initialized_repository.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs



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
def test_push_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    missing_resource_name: str,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
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
        push.main(c, rd, ri, rp, rs)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_push_main_raises_if_remote_objects_request_fails(
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
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(requests, "get", raise_exception)

    with pytest.raises(SCCSException) as e:
        push.main(c, rd, ri, rp, rs)

    assert str(e.value) == c.PUSH_HTTP_REQUEST_ERROR_MESSAGE


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
def test_push_main_raises_remote_objects_request_has_4xx_or_5xx_status_code(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    response = requests.Response()
    response.status_code = status_code
    response._content = b"test content"

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(SCCSException) as e:
        push.main(c, rd, ri, rp, rs)

    assert str(e.value) == tc.PUSH_HTTP_REQUEST_ERROR_MESSAGE


@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_push_main_staged_repository_creation_fails(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    function: str,
    raise_exception: FunctionType
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: requests.Response())
    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        push.main(c, rd, ri, rp, rs)
    assert str(e.value) == c.STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        repository_with_multiple_commits.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


def test_push_main_raises_if_upload_objects_request_fails(
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
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(requests, "post", raise_exception)

    with pytest.raises(SCCSException) as e:
        push.main(c, rd, ri, rp, rs)

    assert str(e.value) == tc.PUSH_HTTP_REQUEST_ERROR_MESSAGE


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
def test_push_main_raises_if_upload_objects_request_has_4xx_or_5xx_status_code(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    status_code: int,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    get_response = requests.Response()
    get_response.status_code = 200
    get_response._content = b"test content"

    response = requests.Response()
    response.status_code = status_code
    response._content = b"test content"

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)
    monkeypatch.setattr(requests, "post", response)
    monkeypatch.setattr(RepositoryIO, "mutate_updated_branches", lambda *args, **kwargs: None)

    with pytest.raises(SCCSException) as e:
        push.main(c, rd, ri, rp, rs)
    
    assert str(e.value) == tc.PUSH_HTTP_REQUEST_ERROR_MESSAGE



def test_push_main_prints_success_message_on_success(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    get_response = requests.Response()
    get_response.status_code = 200
    get_response._content = b"test content"
    get_response.json = lambda: {c.HTTP_OBJECTS_DICT_KEY: [tc.TEST_COMMIT_IDENTIFIER]} # pyright: ignore[reportAttributeAccessIssue]

    post_response = requests.Response()
    post_response.status_code = 200
    post_response._content = b"test content"

    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_REPOSITORY_URL_ENDING)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: post_response)
    

    push.main(c, rd, ri, rp, rs)

    assert capsys.readouterr().out.strip() == tc.STATUS_CODE_MESSAGE_TEMPLATE.format(
        status_code=tc.STATUS_CODE_TWO_HUNDRED
    ) + tc.NEWLINE + tc.PUSH_SUCCESS_MESSAGE_TEMPLATE.format(
        status_code=tc.STATUS_CODE_TWO_HUNDRED, url=rd.base_repository_url()
    )

def test_push_main_resets_target_branch_on_failure(
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
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)

    with pytest.raises(SCCSException) as e:
        push.main(c, rd, ri, rp, rs)
        assert str(e.value) == c.STAGED_REPOSITORY_ERROR_MESSAGE
        assert rs.target.get() is None


def test_push_main_clears_updated_branches_on_success(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    get_response = requests.Response()
    get_response.status_code = 200
    get_response._content = b"test content"
    get_response.json = lambda: {c.HTTP_OBJECTS_DICT_KEY: [tc.TEST_COMMIT_IDENTIFIER]} # pyright: ignore[reportAttributeAccessIssue]

    response = requests.Response()
    response.status_code = 200
    response._content = b"test content"

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_REPOSITORY_URL_ENDING)

    with open(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r+") as f:
        metadata = json.load(f)
        metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY].append(tc.TEST_STRING)
        f.seek(0)
        json.dump(metadata, f)
        f.truncate()

    push.main(c, rd, ri, rp, rs)

    with open(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r") as f:
        metadata = json.load(f)
        assert metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY] == []


def test_push_main_does_not_clear_updated_branches_on_failure(
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
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    get_response = requests.Response()
    get_response.status_code = 200
    get_response._content = b"test content"
    get_response.json = lambda: {c.HTTP_OBJECTS_DICT_KEY: [tc.TEST_COMMIT_IDENTIFIER]} # pyright: ignore[reportAttributeAccessIssue]

    response = requests.Response()
    response.status_code = 500
    response._content = b"test content"

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)
    monkeypatch.setattr(RepositoryData, "base_repository_url", lambda *args, **kwargs: tc.TEST_REPOSITORY_URL_ENDING)

    with open(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r+") as f:
        metadata = json.load(f)
        metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY].append(tc.TEST_STRING)
        f.seek(0)
        json.dump(metadata, f)
        f.truncate()

    with pytest.raises(SCCSException) as e:
        push.main(c, rd, ri, rp, rs)
    assert str(e.value) == tc.PUSH_HTTP_REQUEST_ERROR_MESSAGE

    with open(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r") as f:
        metadata = json.load(f)
        assert metadata[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY] == [tc.TEST_STRING]


