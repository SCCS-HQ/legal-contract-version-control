from typing import Any, NoReturn

from local_sccs.constants_classes import SCCSConstants
from test_constants import SCCSTestConstants
import pytest
import requests
from local_sccs import clone, utils
from local_sccs.exceptions import SCCSException
from typing import Any
import io
import zipfile
from pathlib import Path

def test_print_clone_success_message(
    capsys: pytest.CaptureFixture[str], tc: SCCSTestConstants, c: SCCSConstants
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
    c: SCCSConstants, url: str, error_raised: bool, expected_value: str | None
) -> None:

    if error_raised:
        with pytest.raises(SCCSException):
            clone.repository_name_from_url(c, url)
    else:
        assert clone.repository_name_from_url(c, url) == expected_value


@pytest.mark.parametrize(
    "status_code, error_raised",
    [(100, False), (200, False), (300, False), (400, True), (500, True)]
)
def test_request_repository_raises_if_http_error_occurred(
    monkeypatch: pytest.MonkeyPatch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    status_code: int,
    error_raised: bool
) -> None:
    
    response = requests.Response()
    response.status_code = status_code

    def return_response(*args: Any, **kwargs: Any) -> requests.Response:
        return response

    monkeypatch.setattr(requests, "get", return_response)

    if error_raised:
        with pytest.raises(SCCSException):
            clone.request_repository(c, tc.NO_PATH_TEST_URL)
    else:
        assert clone.request_repository(c, tc.NO_PATH_TEST_URL) == response


def test_request_repository_raises_if_request_exception_is_raised(
    monkeypatch: pytest.MonkeyPatch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
) -> None:

    def raise_request_exception(*args: Any, **kwargs: Any) -> NoReturn:
        raise requests.RequestException

    monkeypatch.setattr(requests, "get", raise_request_exception)

    with pytest.raises(SCCSException):
        clone.request_repository(c, tc.NO_PATH_TEST_URL)


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
    url: str, c: SCCSConstants, error_raised: bool
) -> None:
    if error_raised:
        with pytest.raises(SCCSException):
            clone.validate_entered_url(c, url)
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
        ("my-repo", False),
        ("my_repo", False),
        ("my.repo", False),
        ("myrepo123", False),
        ("A", False),
        ("a" * 64, False),
        ("My-Repo_123.X", False),
    ],
)
def test_validate_repository_name_invalid(
    name: str, c: SCCSConstants, error_raised: bool
) -> None:
    if error_raised:
        with pytest.raises(SCCSException):
            clone.validate_repository_name(c, name)
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
    tmp_path: Path, c: SCCSConstants, url: str
) -> None:

    with pytest.raises(SCCSException):
        clone.unzip_repository_file(c, io.BytesIO(), url, tmp_path)


def test_unzip_repository_file_extracts_files(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    member_path = tc.TEST_FOLDER_DIRECTORY + tc.PATH_SEPARATOR + tc.TEST_TEXT_FILENAME

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr(member_path, tc.TEST_STRING)
    buffer.seek(c.FILE_START_POSITION)

    clone.unzip_repository_file(c, buffer, tc.TEST_REPOSITORY_CLONE_URL, tmp_path)

    assert (tmp_path / tc.TEST_STRING / member_path).read_text() == tc.TEST_STRING


def test_unzip_repository_file_extracts_directories(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    member_path = tc.TEST_FOLDER_DIRECTORY + tc.PATH_SEPARATOR

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr(member_path, tc.EMPTY_STRING)
    buffer.seek(c.FILE_START_POSITION)

    clone.unzip_repository_file(c, buffer, tc.TEST_REPOSITORY_CLONE_URL, tmp_path)

    assert (tmp_path / tc.TEST_STRING / tc.TEST_FOLDER_DIRECTORY).is_dir()


@pytest.mark.parametrize(
    "member_path",
    [
        "../test.txt",
        "/test.txt",
    ],
)
def test_unzip_repository_file_raises_if_member_path_escapes_destination(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants, member_path: str
) -> None:

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr(member_path, tc.TEST_STRING)
    buffer.seek(c.FILE_START_POSITION)

    with pytest.raises(SCCSException):
        clone.unzip_repository_file(
            c, buffer, tc.TEST_REPOSITORY_CLONE_URL, tmp_path
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

    with pytest.raises(zipfile.BadZipFile):
        clone.unzip_repository_file(
            c,
            io.BytesIO(content),
            "http://127.0.0.1:8000/test/test/clone",
            tmp_path,
        )


@pytest.mark.parametrize(
    "url", ["htp://127.0.0.1:8000/clone", "http://127.0.0.1:8000", ""]
)
def test_clone_main_raises_if_url_is_invalid(url: str, c: SCCSConstants) -> None:
    with pytest.raises(SCCSException):
        clone.main(c, url)


@pytest.mark.parametrize(
    "status_code",
    [400, 500]
)
def test_clone_main_raises_if_http_error_occurred(
    monkeypatch: pytest.MonkeyPatch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    status_code: int,
) -> None:
    response = requests.Response()
    response.status_code = status_code

    def return_response(*args: Any, **kwargs: Any) -> requests.Response:
        return response

    def do_nothing(*args: Any, **kwargs: Any) -> None:
        ...

    monkeypatch.setattr(clone, "validate_entered_url", do_nothing)
    monkeypatch.setattr(requests, "get", return_response)
    
    with pytest.raises(SCCSException):
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)


def test_clone_main_raises_if_request_exception_is_raised(
    monkeypatch: pytest.MonkeyPatch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
) -> None:

    def raise_request_exception(*args: Any, **kwargs: Any) -> NoReturn:
        raise requests.RequestException

    def do_nothing(*args: Any, **kwargs: Any) -> None:
        ...

    monkeypatch.setattr(clone, "validate_entered_url", do_nothing)
    monkeypatch.setattr(requests, "get", raise_request_exception)

    with pytest.raises(SCCSException):
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)

@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/test/clone/test",
        "http://127.0.0.1:8000/clone/",
        "http://127.0.0.1:8000",
    ]
)
def test_clone_main_raises_if_repository_name_cannot_be_retrieved(
    c: SCCSConstants, url: str, monkeypatch: pytest.MonkeyPatch
) -> None:

    def do_nothing(*args: Any, **kwargs: Any) -> None:
        ...

    def mock_request_repository(*args: Any, **kwargs: Any) -> requests.Response:
        response = requests.Response()
        response._content = b""
        return response

    monkeypatch.setattr(clone, "validate_entered_url", do_nothing)
    monkeypatch.setattr(clone, "request_repository", mock_request_repository)
    monkeypatch.setattr(io, "BytesIO", do_nothing)

    with pytest.raises(SCCSException):
        clone.main(c, url)

@pytest.mark.parametrize(
    "name",
    ["", "my repo", "repo/name", ".", ".."],
)
def test_clone_main_raises_if_repository_name_is_invalid(
    c: SCCSConstants, name: str, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants
) -> None:

    def do_nothing(*args: Any, **kwargs: Any) -> None:
        ...

    def return_name(*args: Any, **kwargs: Any) -> str:
        return name

    def mock_request_repository(*args: Any, **kwargs: Any) -> requests.Response:
        response = requests.Response()
        response._content = b""
        return response

    monkeypatch.setattr(clone, "validate_entered_url", do_nothing)
    monkeypatch.setattr(clone, "request_repository", mock_request_repository)
    monkeypatch.setattr(io, "BytesIO", do_nothing)
    monkeypatch.setattr(clone, "repository_name_from_url", return_name)

    with pytest.raises(SCCSException):
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)


def test_clone_main_raises_if_local_repository_already_exists(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch
) -> None:
    
    def do_nothing(*args: Any, **kwargs: Any) -> None:
        ...

    def return_string(*args: Any, **kwargs: Any) -> str:
        return tc.TEST_STRING

    def mock_request_repository(*args: Any, **kwargs: Any) -> requests.Response:
        response = requests.Response()
        response._content = bytes(tc.EMPTY_STRING, tc.UTF_8)
        return response

    monkeypatch.setattr(clone, "validate_entered_url", do_nothing)
    monkeypatch.setattr(clone, "request_repository", mock_request_repository)
    monkeypatch.setattr(io, "BytesIO", do_nothing)
    monkeypatch.setattr(clone, "repository_name_from_url", return_string)
    monkeypatch.setattr(clone, "validate_repository_name", do_nothing)
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
    
    def mock_request_repository(*args: Any, **kwargs: Any) -> requests.Response:
        response = requests.Response()
        response.status_code = tc.STATUS_CODE_TWO_HUNDRED
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(tc.TEST_TEXT_FILENAME, tc.TEST_STRING)
        response._content = buffer.getvalue()

        return response

    monkeypatch.setattr(clone, "request_repository", mock_request_repository)
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
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    module: object,
    function: str
) -> None:
        
    def mock_request_repository(*args: Any, **kwargs: Any) -> requests.Response:
        response = requests.Response()
        response.status_code = tc.STATUS_CODE_TWO_HUNDRED
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(tc.TEST_TEXT_FILENAME, tc.TEST_STRING)
        response._content = buffer.getvalue()

        return response

    def return_tmp_path(*args: Any, **kwargs: Any) -> Path:
        return tmp_path

    def raise_exception(*args: Any, **kwargs: Any) -> NoReturn:
        raise Exception

    monkeypatch.setattr(clone, "request_repository", mock_request_repository)
    monkeypatch.setattr(utils, "create_staging_directory", return_tmp_path)
    monkeypatch.setattr(module, function, raise_exception)


    with pytest.raises(Exception):
        clone.main(c, tc.TEST_REPOSITORY_CLONE_URL)
    assert not tmp_path.exists()

