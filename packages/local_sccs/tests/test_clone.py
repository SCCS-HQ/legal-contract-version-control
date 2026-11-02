from types import FunctionType
from typing import Any, NoReturn

from local_sccs.constants_classes import SCCSConstants
from test_constants import SCCSTestConstants
import pytest
import requests
from local_sccs import clone, utils
from local_sccs.exceptions import SCCSException
import io
import os
import zipfile
from pathlib import Path

def test_print_clone_success_message(
    c: SCCSConstants, tc: SCCSTestConstants, capsys: pytest.CaptureFixture[str]
) -> None:

    response = requests.Response()
    response.status_code = tc.STATUS_CODE_ONE_HUNDRED

    clone.print_clone_success_message(c, response)

    assert capsys.readouterr().out == (
        tc.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=tc.STATUS_CODE_ONE_HUNDRED)
        + tc.CLONE_SUCCESS_MESSAGE
    )


@pytest.mark.parametrize(
    "url, error_raised, expected_value",
    [
        ("http://127.0.0.1:8000/test/clone/test", True, None),
        ("http://127.0.0.1:8000/clone/", True, None),
        ("http://127.0.0.1:8000", True, None),
        ("http://127.0.0.1:8000/clone", True, None),
        ("http://127.0.0.1:8000/test/test/clone", False, "test")
    ]
)
def test_repository_name_from_url_raises_if_url_is_missing_path_components(
    c: SCCSConstants, tc: SCCSTestConstants, url: str, error_raised: bool, expected_value: str | None
) -> None:

    if error_raised:
        with pytest.raises(SCCSException) as e:
            clone.repository_name_from_url(c, url)
        if url.endswith(tc.CLONE_ENDPOINT):
            assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=tc.REPOSITORY_NAME_FIELD_NAME
            )
        else:
            assert str(e.value) == tc.INVALID_ENDING_ERROR_MESSAGE
    else:
        assert clone.repository_name_from_url(c, url) == expected_value


@pytest.mark.parametrize(
    "status_code, error_raised",
    [(100, False), (200, False), (300, False), (400, True), (500, True)]
)
def test_request_repository_raises_if_http_error_occurred(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, status_code: int, error_raised: bool
) -> None:
    
    response = requests.Response()
    response.status_code = status_code

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    if error_raised:
        with pytest.raises(SCCSException) as e:
            clone.request_repository(c, tc.NO_PATH_TEST_URL)
        assert str(e.value) == tc.HTTP_REQUEST_ERROR_MESSAGE
    else:
        assert clone.request_repository(c, tc.NO_PATH_TEST_URL) == response


def test_request_repository_raises_if_request_exception_is_raised(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, raise_request_exception: FunctionType
) -> None:


    monkeypatch.setattr(requests, "get", raise_request_exception)

    with pytest.raises(SCCSException) as e:
        clone.request_repository(c, tc.NO_PATH_TEST_URL)
    assert str(e.value) == tc.HTTP_REQUEST_ERROR_MESSAGE


@pytest.mark.parametrize(
    "url, error_raised", [
        ("htp://127.0.0.1:8000/clone", True),
        ("http://127.0.0.1:8000", True),
        ("", True),
        ("http://127.0.0.1:8000/test/test/clone", False),
        ("https://example.com/repos/my-repo/clone", False),
        ("http://localhost/clone", False),
        ("https://127.0.0.1:8080/a/b/c/test/clone", False),
    ]
)
def test_validate_entered_url_raises_if_invalid(
    c: SCCSConstants, tc: SCCSTestConstants, url: str, error_raised: bool
) -> None:
    if error_raised:
        with pytest.raises(SCCSException) as e:
            clone.validate_entered_url(c, url)
        if url == "":
            assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=tc.URL_FIELD_NAME
            )
        elif url == "http://127.0.0.1:8000":
            assert str(e.value) == tc.INVALID_ENDING_ERROR_MESSAGE
        else:
            assert str(e.value) == tc.INVALID_URL_ERROR_MESSAGE
    else:
        clone.validate_entered_url(c, url)


@pytest.mark.parametrize(
    "name, error_raised",
    [
        ("", True),
        ("my repo", True),
        ("repo/name", True),
        (".", True),
        ("..", True),
        ("repo\\name", True),
        ("repo\nname", True),
        ("repo\tname", True),
        ("repo name", True),
        ("répo", True),
        ("repo!", True),
        ("repo@", True),
        (".hidden", False),
        ("trailing.", False),
        ("my-repo", False),
        ("my_repo", False),
        ("my.repo", False),
        ("myrepo123", False),
        ("A", False),
        ("a" * 64, False),
        ("a" * 256, False),
        ("My-Repo_123.X", False),
    ],
)
def test_validate_repository_name_invalid(
    c: SCCSConstants, tc: SCCSTestConstants, name: str, error_raised: bool
) -> None:
    if error_raised:
        with pytest.raises(SCCSException) as e:
            clone.validate_repository_name(c, name)
        assert str(e.value) == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE
    else:
        clone.validate_repository_name(c, name)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/test/clone/test",
        "http://127.0.0.1:8000/clone/",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8000//clone/",        
        "http://127.0.0.1:8000/my repo/clone/",
        "http://127.0.0.1:8000/./clone/",
        "http://127.0.0.1:8000/../clone/",
    ],
)
def test_unzip_repository_file_raises_if_url_is_missing_path_components(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants, url: str
) -> None:

    with pytest.raises(SCCSException) as e:
        clone.unzip_repository_file(c, io.BytesIO(), url, tmp_path)
    assert str(e.value) == tc.INVALID_ENDING_ERROR_MESSAGE


def test_unzip_repository_file_extracts_files(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    member_path = tc.TEST_FOLDER_DIRECTORY + tc.PATH_SEPARATOR + tc.TEST_TEXT_FILENAME

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr(member_path, tc.TEST_STRING)
    buffer.seek(tc.FILE_START_POSITION)

    clone.unzip_repository_file(c, buffer, tc.TEST_REPOSITORY_CLONE_URL, tmp_path)

    assert (tmp_path / tc.TEST_STRING / member_path).read_text() == tc.TEST_STRING


def test_unzip_repository_file_extracts_directories(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    member_path = tc.TEST_FOLDER_DIRECTORY + tc.PATH_SEPARATOR

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr(member_path, tc.EMPTY_STRING)
    buffer.seek(tc.FILE_START_POSITION)

    clone.unzip_repository_file(c, buffer, tc.TEST_REPOSITORY_CLONE_URL, tmp_path)

    assert (tmp_path / tc.TEST_STRING / tc.TEST_FOLDER_DIRECTORY).is_dir()


@pytest.mark.parametrize(
    "member_path",
    [
        "../test.txt",
        "/test.txt",
        "foo/../../bar.txt",
        "foo/../../../etc/passwd",
        "./../escape.txt",
    ]
)
def test_unzip_repository_file_raises_if_member_path_escapes_destination(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants, member_path: str
) -> None:

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr(member_path, tc.TEST_STRING)
    buffer.seek(tc.FILE_START_POSITION)

    with pytest.raises(SCCSException) as e:
        clone.unzip_repository_file(
            c, buffer, tc.TEST_REPOSITORY_CLONE_URL, tmp_path
        )
    assert str(e.value) == tc.PATH_IS_ABSOLUTE_OR_CONTAINS_DOUBLE_PERIOD_ERROR_MESSAGE.format(
        entry_path=Path(member_path)
    )


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b"not a zip file",
    ],
)
def test_unzip_repository_file_raises_if_zip_buffer_is_invalid(
    tmp_path: Path, c: SCCSConstants, content: bytes
) -> None:

    with pytest.raises(zipfile.BadZipFile) as e:
        clone.unzip_repository_file(
            c,
            io.BytesIO(content),
            "http://127.0.0.1:8000/test/test/clone",
            tmp_path,
        )


@pytest.mark.parametrize(
    "url", ["htp://127.0.0.1:8000/clone", "http://127.0.0.1:8000", ""]
)
def test_clone_main_raises_if_url_is_invalid(
    c: SCCSConstants, tc: SCCSTestConstants, url: str
) -> None:
    with pytest.raises(SCCSException) as e:
        clone.main(c, url)
    if url == "":
        assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
            field=tc.URL_FIELD_NAME
        )
    elif url == "http://127.0.0.1:8000":
        assert str(e.value) == tc.INVALID_ENDING_ERROR_MESSAGE
    else:
        assert str(e.value) == tc.INVALID_URL_ERROR_MESSAGE


@pytest.mark.parametrize(
    "status_code",
    [400, 500]
)
def test_clone_main_raises_if_http_error_occurred(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, status_code: int
) -> None:
    response = requests.Response()
    response.status_code = status_code

    monkeypatch.setattr(clone, "validate_entered_url", lambda *args, **kwargs: None)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(SCCSException) as e:
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)
    assert str(e.value) == tc.HTTP_REQUEST_ERROR_MESSAGE


def test_clone_main_raises_if_request_exception_is_raised(
    c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, raise_request_exception: FunctionType
) -> None:

    monkeypatch.setattr(clone, "validate_entered_url", lambda *args, **kwargs: None)
    monkeypatch.setattr(requests, "get", raise_request_exception)

    with pytest.raises(SCCSException) as e:
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)
    assert str(e.value) == tc.HTTP_REQUEST_ERROR_MESSAGE

@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/test/clone/test",
        "http://127.0.0.1:8000/clone/",
        "http://127.0.0.1:8000",
    ]
)
def test_clone_main_raises_if_repository_name_cannot_be_retrieved(
    c: SCCSConstants, tc: SCCSTestConstants, url: str, monkeypatch: pytest.MonkeyPatch, raise_exception: FunctionType
) -> None:
    
    response = requests.Response()
    response._content = b""

    monkeypatch.setattr(clone, "validate_entered_url", lambda *args, **kwargs: None)
    monkeypatch.setattr(clone, "request_repository", lambda *args, **kwargs: response)
    monkeypatch.setattr(clone, "repository_name_from_url", raise_exception)

    with pytest.raises(Exception):
        clone.main(c, url)


@pytest.mark.parametrize(
    "name",
    ["", "my repo", "repo/name", ".", ".."],
)
def test_clone_main_raises_if_repository_name_is_invalid(
    c: SCCSConstants, tc: SCCSTestConstants, name: str, monkeypatch: pytest.MonkeyPatch
) -> None:

    response = requests.Response()
    response._content = b""

    monkeypatch.setattr(clone, "validate_entered_url", lambda *args, **kwargs: None)
    monkeypatch.setattr(clone, "request_repository", lambda *args, **kwargs: response)
    monkeypatch.setattr(clone, "repository_name_from_url", lambda *args, **kwargs: name)

    with pytest.raises(SCCSException) as e:
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)
    assert str(e.value) == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


def test_clone_main_raises_if_local_repository_already_exists(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch
) -> None:

    response = requests.Response()
    response._content = bytes(tc.EMPTY_STRING, tc.UTF_8)
    response.status_code = tc.STATUS_CODE_TWO_HUNDRED

    monkeypatch.setattr(clone, "validate_entered_url", lambda *args, **kwargs: None)
    monkeypatch.setattr(clone, "request_repository", lambda *args, **kwargs: response)
    monkeypatch.setattr(io, "BytesIO", lambda *args, **kwargs: None)
    monkeypatch.setattr(clone, "repository_name_from_url", lambda *args, **kwargs: tc.TEST_STRING)
    monkeypatch.setattr(clone, "validate_repository_name", lambda *args, **kwargs: None)
    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.TEST_STRING).mkdir()

    with pytest.raises(SCCSException):
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)


def test_clone_main_unzips_repository(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str]
) -> None:
    
    response = requests.Response()
    response.status_code = tc.STATUS_CODE_TWO_HUNDRED
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(tc.TEST_TEXT_FILENAME, tc.TEST_STRING)
    response._content = buffer.getvalue()

    monkeypatch.setattr(clone, "request_repository", lambda *args, **kwargs: response)
    monkeypatch.chdir(tmp_path)

    clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)

    assert (tmp_path / tc.TEST_STRING / tc.TEST_TEXT_FILENAME).read_text() == tc.TEST_STRING

    assert capsys.readouterr().out == (
        tc.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=tc.STATUS_CODE_TWO_HUNDRED)
        + tc.CLONE_SUCCESS_MESSAGE
    )


@pytest.mark.parametrize(
    "module, function",
    [(utils, "promote_staging"), (clone, "unzip_repository_file")]
)
def test_clone_main_deletes_staging_root_if_error_is_raised(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants, monkeypatch: pytest.MonkeyPatch, module: object, function: str, raise_exception: FunctionType
) -> None:
        
    response = requests.Response()
    response.status_code = tc.STATUS_CODE_TWO_HUNDRED
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(tc.TEST_TEXT_FILENAME, tc.TEST_STRING)
    response._content = buffer.getvalue()

    monkeypatch.setattr(clone, "request_repository", lambda *args, **kwargs: response)
    monkeypatch.setattr(utils, "create_staging_directory", lambda *args, **kwargs: tmp_path)
    monkeypatch.setattr(module, function, raise_exception)


    with pytest.raises(Exception) as e:
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)
    assert not tmp_path.exists()

