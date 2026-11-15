import shutil
from types import FunctionType

import pytest
from pathlib import Path
from test_constants import SCCSTestConstants
from remote_sccs.constants_classes import RemoteSCCSConstants
from remote_sccs import main
from fastapi import HTTPException, UploadFile
import zipfile
import io
import json
import os
from types import FunctionType
from unittest import mock
import importlib


@pytest.mark.parametrize(
    "repository_name, error_raised",
    [
        ("..", True),
        ("../repo", True),
        ("repo/..", True),
        (".", True),
        ("./repo", True),
        ("repo/.", True),
        ("repo!@#$%^&*()", True),
        ("repo with spaces", True),
        ("valid_repo_name", False),
        ("another-valid-repo-name", False),
        ("repo123", False),
    ],
)
def test_validate_repository_name_returns_resolved_name(
    repository_name: str, error_raised: bool, tc: SCCSTestConstants
) -> None:

    if error_raised:
        with pytest.raises(HTTPException) as e:
            main.validate_repository_name(repository_name)


        assert e.value.status_code == tc.STATUS_CODE_400
        assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE
    else:
        assert repository_name == main.validate_repository_name(repository_name).value


@pytest.mark.parametrize(
    "directory",
    [
        ("dir/dir2/dir3"),
        ("path/path")
    ]
)
def test_repository_base_directory_returns_resolved_path(
    rc: RemoteSCCSConstants, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants, directory: str, tmp_path: Path
) -> None:

    nest_path = tmp_path / directory
    nest_path.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.chdir(nest_path)

    expected_path = Path(nest_path) / tc.REPOSITORIES_BASE_DIRECTORY

    assert main.repository_base_directory(rc) == expected_path.resolve()


@pytest.mark.parametrize(
    "repository_name, error_raised",
    [
        ("..", True),
        ("../repo", True),
        ("repo/..", True),
        (".", True),
        ("./repo", True),
        ("repo/.", True),
        ("repo!@#$%^&*()", True),
        ("repo with spaces", True),
        ("valid_repo_name", False),
        ("another-valid-repo-name", False),
        ("repo123", False),
    ],
)
def test_repository_directory_raises_if_repository_name_is_invalid(
    repository_name: str, error_raised: bool, tc: SCCSTestConstants, rc: RemoteSCCSConstants
) -> None:

    if error_raised:
        with pytest.raises(HTTPException) as e:
            main.repository_directory(rc, repository_name)


        assert e.value.status_code == tc.STATUS_CODE_400
        assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE
    else:
        main.repository_directory(rc, repository_name)


def test_repository_directory_raises_if_repository_path_is_outside_base_directory(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants
) -> None:
    
    with pytest.raises(HTTPException) as e:
        main.repository_directory(rc, tc.INVALID_REPOSITORY_NAME)



    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


def test_repository_directory_returns_resolved_path(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants
) -> None:

    expected = (Path(tc.REPOSITORIES_BASE_DIRECTORY) / tc.VALID_REPOSITORY_NAME).resolve()

    assert expected == main.repository_directory(rc, tc.VALID_REPOSITORY_NAME)


def test_repository_directory_raises_if_resolved_path_escapes_via_symlink(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    base = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY
    base.mkdir(parents=True, exist_ok=True)
    (base / tc.TEST_STRING).symlink_to(tmp_path.parent, target_is_directory=True)

    monkeypatch.chdir(tmp_path)

    with pytest.raises(HTTPException) as e:
        main.repository_directory(rc, tc.TEST_STRING)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


def test_ensure_repository_exists_raises_if_repository_directory_does_not_exist(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        main.ensure_repository_exists(rc, Path(tc.VALID_REPOSITORY_NAME))



    assert e.value.status_code == tc.STATUS_CODE_404
    assert e.value.detail == tc.REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(repository_name=tc.VALID_REPOSITORY_NAME)


def test_safe_extract_zip_raises_if_member_path_is_absolute_path(
    rc: RemoteSCCSConstants, tc: SCCSTestConstants, tmp_path: Path
) -> None:

    with pytest.raises(HTTPException) as e:
        main.safe_extract_zip(
            rc,
            zipfile.ZipFile(tmp_path / tc.TEST_ZIP_FILE_NAME, mode="w"),
            tc.ABSOLUTE_PATH,
            tmp_path
        )



    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_FILE_PATH_IN_ZIP_ERROR_MESSAGE


def test_safe_extract_zip_raises_if_member_path_contains_double_period(
    rc: RemoteSCCSConstants, tc: SCCSTestConstants, tmp_path: Path
) -> None:

    with pytest.raises(HTTPException) as e:
        main.safe_extract_zip(
            rc,
            zipfile.ZipFile(tmp_path / tc.TEST_ZIP_FILE_NAME, mode="w"),
            tc.ABSOLUTE_PATH_WITH_DOUBLE_PERIOD,
            tmp_path
        )



    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_FILE_PATH_IN_ZIP_ERROR_MESSAGE


def test_safe_extract_zip_raises_if_target_path_is_outside_base_directory(
    rc: RemoteSCCSConstants, tc: SCCSTestConstants, tmp_path: Path
) -> None:

    with pytest.raises(HTTPException) as e:
        main.safe_extract_zip(
            rc,
            zipfile.ZipFile(tmp_path / tc.TEST_ZIP_FILE_NAME, mode="w"),
            str(tmp_path) + tc.TEST_STRING + tc.ABSOLUTE_PATH_WITH_DOUBLE_PERIOD,
            tmp_path / tc.SECOND_TEST_STRING
        )



    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_FILE_PATH_IN_ZIP_ERROR_MESSAGE


def test_safe_extract_zip_raises_if_target_path_escapes_via_symlink(
    rc: RemoteSCCSConstants, tc: SCCSTestConstants, tmp_path: Path
) -> None:

    (tmp_path / tc.TEST_STRING).symlink_to(tmp_path.parent, target_is_directory=True)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.PATH_SEPARATOR + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    buffer.seek(0)

    with zipfile.ZipFile(buffer, mode="r") as zf:
        with pytest.raises(HTTPException) as e:
            main.safe_extract_zip(rc, zf, tc.TEST_STRING + tc.PATH_SEPARATOR + tc.TEXT_FILE_EXTENSION, tmp_path)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_FILE_PATH_IN_ZIP_ERROR_MESSAGE


def test_safe_extract_zip_extracts_files_to_target_directory(
    rc: RemoteSCCSConstants, tc: SCCSTestConstants, tmp_path: Path
) -> None:

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
        zf.writestr(tc.TEST_STRING + tc.PATH_SEPARATOR + tc.SECOND_TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.SECOND_TEST_STRING)

    buffer.seek(0)

    with zipfile.ZipFile(buffer, mode="r") as zf:
        for member in zf.infolist():
            main.safe_extract_zip(rc, zf, member.filename, tmp_path)

    with open(tmp_path / (tc.TEST_STRING + tc.TEXT_FILE_EXTENSION), "r") as f:
        assert f.read() == tc.TEST_STRING

    with open(tmp_path / tc.TEST_STRING / (tc.SECOND_TEST_STRING + tc.TEXT_FILE_EXTENSION), "r") as f:
        assert f.read() == tc.SECOND_TEST_STRING


def test_safe_extract_zip_extracts_directory_members(
    rc: RemoteSCCSConstants, tc: SCCSTestConstants, tmp_path: Path
) -> None:

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.PATH_SEPARATOR, tc.EMPTY_STRING)
        zf.writestr(
            tc.TEST_STRING + tc.PATH_SEPARATOR + tc.SECOND_TEST_STRING + tc.TEXT_FILE_EXTENSION,
            tc.SECOND_TEST_STRING,
        )

    buffer.seek(0)

    with zipfile.ZipFile(buffer, mode="r") as zf:
        for member in zf.infolist():
            main.safe_extract_zip(rc, zf, member.filename, tmp_path)

    assert (tmp_path / tc.TEST_STRING).is_dir()
    with open(
        tmp_path / tc.TEST_STRING / (tc.SECOND_TEST_STRING + tc.TEXT_FILE_EXTENSION), "r"
    ) as f:
        assert f.read() == tc.SECOND_TEST_STRING


@pytest.mark.asyncio
async def test_root_returns_easter_egg_message(
    tc: SCCSTestConstants
) -> None:

    assert await main.root() == {tc.MESSAGE_DICT_KEY: tc.EASTER_EGG_MESSAGE}


@pytest.mark.asyncio
async def test_publish_raises_if_repository_name_is_outside_base_directory(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.INVALID_REPOSITORY_NAME)



    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_repository_already_exists(
    rc: RemoteSCCSConstants, tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer)
    mock_data = json.dumps({rc.REMOTE_KEY: tc.TEST_STRING})

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)



    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.REPOSITORY_EXISTS_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_json_loads_fails(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer)
    mock_data = tc.TEST_STRING

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_JSON_DATA_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_remote_is_empty(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer)
    mock_data = json.dumps({tc.REMOTE_DICT_KEY: tc.EMPTY_STRING})

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.REMOTE_URL_REQUIRED_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_filename_is_empty(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.EMPTY_STRING, file=zip_buffer)
    mock_data = json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING})

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_filename_stem_is_not_repository_name(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.TEST_STRING, file=zip_buffer)
    mock_data = json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING})

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_len_of_zf_infolist_is_greater_than_1000(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: [None] * 1001)

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer)
    mock_data = json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING})

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.TOO_MANY_FILES_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_zf_infolist_total_upload_size_is_greater_than_100mb(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    infolist = zipfile.ZipInfo()
    infolist.file_size = 101 * 1024 * 1024

    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: [infolist])

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer)
    mock_data = json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING})

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.UPLOAD_TOO_LARGE_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_any_file_in_zf_infolist_is_larger_than_10mb(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    infolist_acceptable_item = zipfile.ZipInfo()
    infolist_acceptable_item.file_size = 1 * 1024 * 1024
    infolist_large_item = zipfile.ZipInfo()
    infolist_large_item.file_size = 11 * 1024 * 1024
    infolist_large_item.filename = tc.TEST_STRING + tc.TEXT_FILE_EXTENSION

    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: [infolist_large_item] + [infolist_acceptable_item] * 8)

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)
    mock_file = UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer)
    mock_data = json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING})

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, mock_file, mock_data)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE.format(filename=tc.TEST_STRING + tc.TEXT_FILE_EXTENSION)


@pytest.mark.asyncio
async def test_publish_raises_if_member_path_is_absolute_path(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    
    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.PATH_SEPARATOR + tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer), json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING}))

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_FILE_PATH_IN_ZIP_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_raises_if_member_path_contains_double_period(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    
    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.PATH_SEPARATOR + tc.DOUBLE_PERIOD + tc.PATH_SEPARATOR + tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    with pytest.raises(HTTPException) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer), json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING}))

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_FILE_PATH_IN_ZIP_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_publish_publishes_files_to_repositories_directory(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    
    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    await main.publish(tc.VALID_REPOSITORY_NAME, UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer), json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING}))

    with open(tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME / (tc.TEST_STRING + tc.TEXT_FILE_EXTENSION), "r") as f:
        assert f.read() == tc.TEST_STRING


@pytest.mark.asyncio
async def test_publish_returns_success_message(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    
    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    assert {
        tc.MESSAGE_DICT_KEY: tc.FILE_PUBLISHED_MESSAGE,
        tc.REPOSITORY_URL_DICT_KEY: tc.TEST_STRING 
    } == await main.publish(tc.VALID_REPOSITORY_NAME, UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer), json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING}))


@pytest.mark.asyncio
async def test_publish_deletes_staging_root_if_exception_occurs(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raise_exception: FunctionType
) -> None:
    
    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(json, "loads", raise_exception)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    with pytest.raises(OSError) as e:
        await main.publish(tc.VALID_REPOSITORY_NAME, UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer), json.dumps({tc.REMOTE_DICT_KEY: tc.TEST_STRING}))

    staging_dirs = list(
        tmp_path.glob(
            tc.SCCS_TEMP_DIRECTORY_GLOB_PATTERN
        )
    )

    assert not staging_dirs


@pytest.mark.asyncio
async def test_clone_raises_if_repository_name_is_outside_base_directory(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.clone(tc.INVALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_clone_raises_if_repository_does_not_exist(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.clone(tc.VALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_404
    assert e.value.detail == tc.REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(repository_name=tc.VALID_REPOSITORY_NAME)


@pytest.mark.asyncio
async def test_clone_raises_if_total_number_of_files_in_repository_is_greater_than_1000(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: [None] * 1001)

    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    with open(repository_path / (tc.TEST_STRING + tc.TEXT_FILE_EXTENSION), "w") as f:
        f.write(tc.TEST_STRING)

    with pytest.raises(HTTPException) as e:
        await main.clone(tc.VALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.TOO_MANY_FILES_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_clone_raises_if_total_upload_size_of_files_in_repository_is_greater_than_100mb(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    infolist = zipfile.ZipInfo()
    infolist.file_size = 101 * 1024 * 1024

    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: [infolist])

    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    with open(repository_path / (tc.TEST_STRING + tc.TEXT_FILE_EXTENSION), "w") as f:
        f.write(tc.TEST_STRING)

    with pytest.raises(HTTPException) as e:
        await main.clone(tc.VALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.UPLOAD_TOO_LARGE_ERROR_MESSAGE

@pytest.mark.asyncio
async def test_clone_raises_if_any_file_in_repository_is_larger_than_10mb(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    infolist_acceptable_item = zipfile.ZipInfo()
    infolist_acceptable_item.file_size = 1 * 1024 * 1024
    infolist_large_item = zipfile.ZipInfo()
    infolist_large_item.file_size = 11 * 1024 * 1024
    infolist_large_item.filename = tc.TEST_STRING + tc.TEXT_FILE_EXTENSION

    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: [infolist_large_item] + [infolist_acceptable_item] * 8)


    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    with open(repository_path / (tc.TEST_STRING + tc.TEXT_FILE_EXTENSION), "w") as f:
        f.write(tc.TEST_STRING)

    with pytest.raises(HTTPException) as e:
        await main.clone(tc.VALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE.format(filename=tc.TEST_STRING + tc.TEXT_FILE_EXTENSION)


@pytest.mark.asyncio
async def test_clone_returns_repository(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)

    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    with open(repository_path / (tc.TEST_STRING + tc.TEXT_FILE_EXTENSION), "w") as f:
        f.write(tc.TEST_STRING)

    response = await main.clone(tc.VALID_REPOSITORY_NAME)

    response_body = tc.EMPTY_STRING.encode()
    async for chunk in response.body_iterator:
        response_body += chunk # pyright: ignore[reportOperatorIssue]

    with zipfile.ZipFile(io.BytesIO(response_body), mode="r") as response_zf:
        assert (
            response_zf.read(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION)
            == tc.TEST_STRING.encode()
        )


@pytest.mark.asyncio
async def test_push_raises_is_repository_name_is_outside_base_directory(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.push(tc.INVALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_push_raises_if_repository_does_not_exist(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.push(tc.VALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_404
    assert e.value.detail == tc.REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(repository_name=tc.VALID_REPOSITORY_NAME)


@pytest.mark.asyncio
async def test_push_raises_if_objects_directory_does_not_exist(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    with pytest.raises(HTTPException) as e:
        await main.push(tc.VALID_REPOSITORY_NAME)

    assert e.value.status_code == tc.STATUS_CODE_404
    assert e.value.detail == tc.OBJECTS_NOT_FOUND_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_push_returns_list_of_repository_objects(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    objects_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY
    objects_path.mkdir(parents=True, exist_ok=True)

    test_filenames = [tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.SECOND_TEST_STRING + tc.TEXT_FILE_EXTENSION]

    test_objects = [
        Path(objects_path / i) for i in test_filenames
    ]
    for i in test_objects:
        i.write_text(tc.TEST_STRING)

    assert await main.push(tc.VALID_REPOSITORY_NAME) == {tc.OBJECTS_DICT_KEY: {Path(i).stem for i in test_filenames}}


@pytest.mark.asyncio
async def test_push_upload_raises_if_repository_path_is_outside_base_directory(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.push_upload(tc.INVALID_REPOSITORY_NAME, UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=io.BytesIO()))

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_push_upload_raises_if_repository_does_not_exist(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.push_upload(tc.VALID_REPOSITORY_NAME, UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=io.BytesIO()))

    assert e.value.status_code == tc.STATUS_CODE_404
    assert e.value.detail == tc.REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(repository_name=tc.VALID_REPOSITORY_NAME)


@pytest.mark.asyncio
async def test_push_upload_raises_zip_filename_is_empty(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)

    with pytest.raises(HTTPException) as e:
        await main.push_upload(tc.VALID_REPOSITORY_NAME, UploadFile(filename="", file=io.BytesIO()))

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_push_upload_raises_if_zip_filename_stem_is_not_repository_name(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)

    with pytest.raises(HTTPException) as e:
        await main.push_upload(tc.VALID_REPOSITORY_NAME, UploadFile(filename=tc.TEST_STRING, file=io.BytesIO()))

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_push_upload_raises_if_zf_infolist_total_upload_size_is_greater_than_100mb(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)

    infolist = zipfile.ZipInfo()
    infolist.file_size = 101 * 1024 * 1024

    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: [infolist])

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    with pytest.raises(HTTPException) as e:
        await main.push_upload(
            tc.VALID_REPOSITORY_NAME,
            UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer),
        )

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.UPLOAD_TOO_LARGE_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_push_upload_raises_if_any_file_in_zf_infolist_is_larger_than_10mb(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)

    infolist_acceptable_item = zipfile.ZipInfo()
    infolist_acceptable_item.file_size = 1 * 1024 * 1024
    infolist_large_item = zipfile.ZipInfo()
    infolist_large_item.file_size = 11 * 1024 * 1024
    infolist_large_item.filename = tc.TEST_STRING + tc.TEXT_FILE_EXTENSION

    monkeypatch.setattr(
        zipfile.ZipFile,
        "infolist",
        lambda *args, **kwargs: [infolist_large_item] + [infolist_acceptable_item] * 8,
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    with pytest.raises(HTTPException) as e:
        await main.push_upload(
            tc.VALID_REPOSITORY_NAME,
            UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer),
        )

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE.format(
        filename=tc.TEST_STRING + tc.TEXT_FILE_EXTENSION
    )


@pytest.mark.asyncio
async def test_push_upload_raises_if_len_of_zf_infolist_is_greater_than_1000(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)

    infolist = [zipfile.ZipInfo() for _ in range(1001)]

    monkeypatch.setattr(zipfile.ZipFile, "infolist", lambda *args, **kwargs: infolist)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    with pytest.raises(HTTPException) as e:
        await main.push_upload(
            tc.VALID_REPOSITORY_NAME,
            UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer),
        )

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.TOO_MANY_FILES_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_push_upload_deletes_staging_root_if_exception_occurs(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raise_exception: FunctionType 
) -> None:

    monkeypatch.setattr(shutil, "copytree", raise_exception)
    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)

    with pytest.raises(OSError):
        await main.push_upload(
            tc.VALID_REPOSITORY_NAME,
            UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=io.BytesIO()),
        )


    staging_dirs = list(
        tmp_path.glob(
            tc.SCCS_TEMP_DIRECTORY_GLOB_PATTERN
        )
    )

    assert not staging_dirs


@pytest.mark.asyncio
async def test_push_upload_rolls_back_repository_if_replace_staging_fails(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)
    metadata_path = repository_path / tc.SCCS_DIRECTORY
    metadata_path.mkdir(parents=True, exist_ok=True)
    with open(metadata_path / tc.METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump({tc.CURRENT_BRANCH_DICT_KEY: {tc.UPDATED_BRANCHES_DICT_KEY: [tc.TEST_STRING]}}, f)

    original_replace = os.replace
    replace_calls = 0

    def failing_replace(src, dst):
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 1:
            raise OSError
        return original_replace(src, dst)

    monkeypatch.setattr(os, "replace", failing_replace)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    with pytest.raises(Exception):
        await main.push_upload(
            tc.VALID_REPOSITORY_NAME,
            UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer),
        )

    assert repository_path.exists()
    with open(repository_path / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "r") as f:
        assert json.load(f)[tc.CURRENT_BRANCH_DICT_KEY][tc.UPDATED_BRANCHES_DICT_KEY] == [tc.TEST_STRING]

    staging_dirs = list(tmp_path.rglob(tc.SCCS_TEMP_DIRECTORY_GLOB_PATTERN))
    assert not staging_dirs


@pytest.mark.asyncio
async def test_push_upload_returns_success_message(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)
    metadata_path = repository_path / tc.SCCS_DIRECTORY
    metadata_path.mkdir(parents=True, exist_ok=True)
    with open(metadata_path / tc.METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump({tc.CURRENT_BRANCH_DICT_KEY: {tc.UPDATED_BRANCHES_DICT_KEY: [tc.TEST_STRING]}}, f)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    response = await main.push_upload(
        tc.VALID_REPOSITORY_NAME,
        UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer),
    )

    assert response == {tc.MESSAGE_DICT_KEY: tc.PUSH_SUCCESS_MESSAGE}


@pytest.mark.asyncio
async def test_push_upload_updates_repository_objects_directory_with_uploaded_files_and_repository_document(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)
    metadata_path = repository_path / tc.SCCS_DIRECTORY
    metadata_path.mkdir(parents=True, exist_ok=True)
    with open(metadata_path / tc.METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump({tc.CURRENT_BRANCH_DICT_KEY: {tc.UPDATED_BRANCHES_DICT_KEY: [tc.TEST_STRING]}}, f)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr(tc.TEST_STRING + tc.TEXT_FILE_EXTENSION, tc.TEST_STRING)
    zip_buffer.seek(0)

    await main.push_upload(
        tc.VALID_REPOSITORY_NAME,
        UploadFile(filename=tc.VALID_REPOSITORY_NAME + tc.ZIP_FILE_EXTENSION, file=zip_buffer),
    )

    with open((repository_path / tc.TEST_STRING).with_suffix(tc.TEXT_FILE_EXTENSION), "r") as f:
        assert f.read() == tc.TEST_STRING


@pytest.mark.asyncio
async def test_pull_raises_if_repository_name_is_outside_base_directory(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.pull(tc.INVALID_REPOSITORY_NAME, {})

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_pull_raises_if_repository_does_not_exist(
    tc: SCCSTestConstants
) -> None:

    with pytest.raises(HTTPException) as e:
        await main.pull(tc.VALID_REPOSITORY_NAME, {})

    assert e.value.status_code == tc.STATUS_CODE_404
    assert e.value.detail == tc.REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE.format(repository_name=tc.VALID_REPOSITORY_NAME)


@pytest.mark.parametrize(
    "data",
    [
        "",
        {"test": "test"},
        {"objects": "not a list"},
        {"objects": [1, 2, 3]},
        {"objects": [{"not": "a string"}]},
        {"objects": ["valid_object", 123]},
        {"objects": {}},
    ],

)
@pytest.mark.asyncio
async def test_pull_raises_if_data_is_invalid(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: dict | str
) -> None:

    monkeypatch.chdir(tmp_path)
    (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME).mkdir(parents=True, exist_ok=True)

    with pytest.raises(HTTPException) as e:
        await main.pull(tc.VALID_REPOSITORY_NAME, data) # pyright: ignore[reportArgumentType]

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_JSON_DATA_ERROR_MESSAGE


@pytest.mark.asyncio
async def test_pull_raises_if_objects_directory_is_outside_base_directory(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    sccs_path = repository_path / rc.SCCS_DIRECTORY
    sccs_path.mkdir(parents=True, exist_ok=True)

    objects_path = sccs_path / rc.OBJECTS_DIRECTORY
    objects_path.mkdir(parents=True, exist_ok=True)

    branches_path = sccs_path / rc.BRANCHES_DIRECTORY
    branches_path.mkdir(parents=True, exist_ok=True)

    outside_dir = tmp_path / "outside"
    outside_dir.mkdir(parents=True, exist_ok=True)

    shutil.rmtree(objects_path)
    objects_path.symlink_to(outside_dir, target_is_directory=True)

    with open(objects_path / tc.TEST_STRING, "w") as f:
        f.write(tc.TEST_STRING)

    with pytest.raises(HTTPException) as e:
        await main.pull(tc.VALID_REPOSITORY_NAME, {tc.OBJECTS_DICT_KEY: [tc.TEST_STRING]})

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE
    

@pytest.mark.asyncio
async def test_pull_raises_if_branches_directory_is_outside_base_directory(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    objects_path = repository_path / rc.SCCS_DIRECTORY / rc.OBJECTS_DIRECTORY
    objects_path.mkdir(parents=True, exist_ok=True)

    branches_path = repository_path / rc.SCCS_DIRECTORY / rc.BRANCHES_DIRECTORY
    branches_path.mkdir(parents=True, exist_ok=True)

    outside_dir = tmp_path / "outside"
    outside_dir.mkdir(parents=True, exist_ok=True)

    shutil.rmtree(branches_path)
    branches_path.symlink_to(outside_dir, target_is_directory=True)

    with open(objects_path / tc.TEST_STRING, "w") as f:
        f.write(tc.TEST_STRING)

    with pytest.raises(HTTPException) as e:
        await main.pull(tc.VALID_REPOSITORY_NAME, {tc.OBJECTS_DICT_KEY: [tc.TEST_STRING]})

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.INVALID_REPOSITORY_NAME_ERROR_MESSAGE
    

@pytest.mark.asyncio
async def test_pull_returns_missing_repository_objects(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    objects_path = repository_path / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY
    objects_path.mkdir(parents=True, exist_ok=True)

    objects = [tc.TEST_STRING, tc.SECOND_TEST_STRING]

    for i in objects:
        with open(objects_path / i, "w") as f:
            f.write(tc.TEST_STRING)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(filename=repository_path / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY / tc.TEST_STRING, arcname=(repository_path / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY / tc.TEST_STRING).relative_to(repository_path))

    response = await main.pull(tc.VALID_REPOSITORY_NAME, {tc.OBJECTS_DICT_KEY: [tc.SECOND_TEST_STRING]})

    response_body = tc.EMPTY_STRING.encode()
    async for chunk in response.body_iterator:
        response_body += chunk # pyright: ignore[reportOperatorIssue]

    assert response_body == zip_buffer.getvalue()


@pytest.mark.asyncio
async def test_pull_raises_if_remote_is_missing_commits_from_local_repository(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)
    repository_path = tmp_path / tc.REPOSITORIES_BASE_DIRECTORY / tc.VALID_REPOSITORY_NAME
    repository_path.mkdir(parents=True, exist_ok=True)

    objects_path = repository_path / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY
    objects_path.mkdir(parents=True, exist_ok=True)

    with pytest.raises(HTTPException) as e:
        await main.pull(tc.VALID_REPOSITORY_NAME, {tc.OBJECTS_DICT_KEY: [tc.SECOND_TEST_STRING]})

    assert e.value.status_code == tc.STATUS_CODE_400
    assert e.value.detail == tc.LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE


def test_import_time_code_creates_repositories_directory_if_it_does_not_exist(
    tc: SCCSTestConstants, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    monkeypatch.chdir(tmp_path)

    assert not (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).exists()

    importlib.reload(main)

    assert (tmp_path / tc.REPOSITORIES_BASE_DIRECTORY).exists()