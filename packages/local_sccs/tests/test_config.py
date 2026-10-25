from local_sccs import config
import pytest
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from test_constants import SCCSTestConstants
from local_sccs.repository_layout import (
    RepositoryData, RepositoryPaths, RepositoryStatus, RepositoryWrite, TargetBranch
)
from pathlib import Path
import shutil
import tempfile
import os
from typing import NoReturn
import json

@pytest.mark.parametrize(
    "key, value",
    [
        ("test", "test"),
        ("remote", "http://127.0.0.1"),
        ("name", "Jeff"),
        ("email", "jeff123@foo.com")
    ]
)
def test_print_config_success_message_prints_correct_message(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str],
    key: str,
    value: str
) -> None:
    config.print_config_success_message(c, key, value)

    assert (
        capsys.readouterr().out
        == tc.CONFIG_SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value)
    )


@pytest.mark.parametrize(
    "key, value, error_raised",
    [
        ("remote", "http://127.0.0.1:8000/test/", False),
        ("remote", "https://127.0.0.1:8000/test", False),
        ("remote", "HTTP://127.0.0.1:8000/test", False),
        ("remote", "HTTPS://127.0.0.1:8000/test", False),
        ("remote", "htp://127.0.0.1:8000/test", True),
        ("remote", "://127.0.0.1:8000/test", True),
        ("remote", "://127.0.0.1:8000/test", True),
        ("remote", "http:///test", True),
        ("remote", "https:///test", True),
        ("remote", "http://127.0.0.1:8000/test?name=test", True),
        ("remote", "https://127.0.0.1:8000/test?name=test", True),
        ("remote", "http://127.0.0.1:8000/test#test", True),
        ("remote", "https://127.0.0.1:8000/test#test", True),
        ("remote", "", True),
        ("remote", " ", True),
        ("name", "", True),
        ("name", " ", True),
        ("name", "test", False),
        ("email", "", True),
        ("email", " ", True),
        ("email", "test", False),
        ("test", "", True),
        ("test", "test", True)
    ]
)
def test_resolve_key_value_raises_correctly(
    c: SCCSConstants, tc: SCCSTestConstants, key: str, value: str, error_raised: bool
) -> None:
    if error_raised:
        with pytest.raises(SCCSException) as e:
            config.resolve_key_value(c, tc.TEST_STRING, key, value)
        if key == "test":
            assert str(e.value) == tc.INVALID_KEY_ERROR_MESSAGE
        elif key in ("name", "email") or (key == "remote" and not value.strip()):
            assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
        elif key == "remote":
            assert str(e.value) == tc.INVALID_URL_ERROR_MESSAGE
    else:
        config.resolve_key_value(c, tc.TEST_STRING, key, value)


@pytest.mark.parametrize(
    "key, value, expected_value",
    [
        ("remote", "http://127.0.0.1:8000/test", "http://127.0.0.1:8000/test/"),
        ("remote", "http://127.0.0.1:8000", "http://127.0.0.1:8000/repos/test/"),

        ("email", "test", "test"),
    ]
)
def test_resolve_key_value_returns_correct_string_if_error_is_not_raised(
    c: SCCSConstants, tc: SCCSTestConstants, key: str, value: str, expected_value: str
) -> None:
    assert config.resolve_key_value(c, tc.TEST_STRING, key, value) == expected_value


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
def test_config_main_raises_for_each_missing_resource(
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
        config.main(c, tc.TEST_STRING, tc.TEST_STRING, rd, rp, rs, rw)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


@pytest.mark.parametrize(
    "key, value, error_raised",
    [
        ("remote", "http://127.0.0.1:8000/test/", False),
        ("remote", "https://127.0.0.1:8000/test", False),
        ("remote", "HTTP://127.0.0.1:8000/test", False),
        ("remote", "HTTPS://127.0.0.1:8000/test", False),
        ("remote", "htp://127.0.0.1:8000/test", True),
        ("remote", "://127.0.0.1:8000/test", True),
        ("remote", "://127.0.0.1:8000/test", True),
        ("remote", "http:///test", True),
        ("remote", "https:///test", True),
        ("remote", "http://127.0.0.1:8000/test?name=test", True),
        ("remote", "https://127.0.0.1:8000/test?name=test", True),
        ("remote", "http://127.0.0.1:8000/test#test", True),
        ("remote", "https://127.0.0.1:8000/test#test", True),
        ("remote", "", True),
        ("remote", " ", True),
        ("name", "", True),
        ("name", " ", True),
        ("name", "test", False),
        ("email", "", True),
        ("email", " ", True),
        ("email", "test", False),
        ("test", "", True),
        ("test", "test", True)
    ]
)
def test_config_main_raises_correctly_given_key_value_provided(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    key: str,
    value: str, 
    error_raised: bool,
    initialized_repository: Path,
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
    if error_raised:
        with pytest.raises(SCCSException) as e:
            config.main(c, key, value, rd, rp, rs, rw)
        if key == "test":
            assert str(e.value) == tc.INVALID_KEY_ERROR_MESSAGE
        elif key in ("name", "email") or (key == "remote" and not value.strip()):
            assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
        elif key == "remote":
            assert str(e.value) == tc.INVALID_URL_ERROR_MESSAGE
    else:
        config.main(c, key, value, rd, rp, rs, rw)


@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_config_main_staged_repository_creation_fails(
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
    rp = RepositoryPaths(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
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

    with pytest.raises(SCCSException) as e:
        config.main(c, tc.NAME_KEY, tc.TEST_STRING, rd, rp, rs, rw)
    assert str(e.value) == tc.COMMIT_STAGED_REPOSITORY_ERROR_MESSAGE

    staging_dirs = list(
        repository_with_multiple_commits.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    
    assert not staging_dirs


def test_repository_write_write_key_to_config_writes_key_value_to_config(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    metadata_path = (
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON
    )

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

    config.main(c, tc.NAME_KEY, tc.TEST_STRING, rd, rp, rs, rw)

    with open(metadata_path, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        metadata = json.load(f)

    assert metadata[tc.CONFIG_DICT_KEY][tc.NAME_KEY] == tc.TEST_STRING


def test_config_main_prints_success_message(
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str],
    initialized_repository: Path,
    target: TargetBranch,
    c: SCCSConstants
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
    config.main(c, tc.NAME_KEY, tc.TEST_STRING, rd, rp, rs, rw)
    
    assert capsys.readouterr().out == tc.CONFIG_SUCCESS_MESSAGE_TEMPLATE.format(
        key=tc.NAME_KEY, value=tc.TEST_STRING
    )
