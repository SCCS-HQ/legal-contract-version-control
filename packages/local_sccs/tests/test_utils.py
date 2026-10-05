import hashlib
import io
import os
import re
import sys
import unittest
import unittest.mock
import zipfile
from pathlib import Path
from typing import Any, NoReturn

import pytest
from local_sccs import utils
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from test_constants import SCCSTestConstants


def test_cleanup_staging_deletes_staging_root(
    tmp_path: Path, tc: SCCSTestConstants
) -> None:

    test_directory = tmp_path / tc.TEST_STRING

    (test_directory).mkdir()

    utils.cleanup_staging(test_directory)

    assert not test_directory.exists()


def test_create_commit_identifier_returns_correct_hash(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    test_parts = [tc.TIMESTAMP_DICT_KEY, tc.TEST_STRING]

    expected = hashlib.sha256(
        tc.PATH_SEPARATOR.join(test_parts).encode(tc.UTF_8)
    ).hexdigest()

    assert expected == utils.create_commit_identifier(c, test_parts)


def test_create_staging_directory_returns_sibling_of_sibling_of_parameter(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    sibling_path = tmp_path / tc.TEST_STRING

    assert utils.create_staging_directory(c, sibling_path).parent == sibling_path.parent


def test_create_staging_directory_uses_correct_default_prefix(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    sibling_path = tmp_path / tc.TEST_STRING

    assert utils.create_staging_directory(c, sibling_path).name.startswith(
        tc.TEMPORARY_DIRECTORY_PREFIX
    )


def test_create_staging_directory_uses_prefix_parameter(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    sibling_path = tmp_path / tc.TEST_STRING

    assert utils.create_staging_directory(
        c, sibling_path, tc.TEST_STRING
    ).name.startswith(tc.TEST_STRING)


def test_entered_argument_returns_correct_argument(
    monkeypatch: pytest.MonkeyPatch, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    monkeypatch.setattr(sys, tc.ARGV_OBJECT_NAME, [tc.TEST_STRING])

    assert utils.entered_argument(c, tc.FIRST_ELEMENT_INDEX) == tc.TEST_STRING


def test_entered_argument_raises_if_argument_does_not_exist(
    monkeypatch: pytest.MonkeyPatch, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    monkeypatch.setattr(sys, tc.ARGV_OBJECT_NAME, [tc.TEST_STRING])

    with pytest.raises(SCCSException):
        utils.entered_argument(c, tc.SECOND_ELEMENT_INDEX)


def test_entered_argument_does_not_raise_if_raise_on_not_provided_is_false(
    monkeypatch: pytest.MonkeyPatch, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    monkeypatch.setattr(sys, tc.ARGV_OBJECT_NAME, [tc.TEST_STRING])

    utils.entered_argument(c, tc.SECOND_ELEMENT_INDEX, raise_on_not_provided=False)


def test_working_directory_returns_cwd(c: SCCSConstants) -> None:

    assert utils.working_directory(c) == Path.cwd()


def test_working_directory_raises_if_cwd_raises_and_pwd_does_not_exist(
    monkeypatch: pytest.MonkeyPatch, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    def raise_error() -> NoReturn:
        raise OSError

    monkeypatch.setattr(Path, tc.CWD_OBJECT_NAME, raise_error)
    monkeypatch.setenv(tc.PWD_ENVIRONMENT_VARIABLE, tc.EMPTY_STRING)

    with pytest.raises(OSError):
        utils.working_directory(c)


def test_working_directory_sets_cwd_to_pwd_if_cwd_raises(
    monkeypatch: pytest.MonkeyPatch,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path
) -> None:

    original_cwd = Path.cwd()
    call_counter = tc.INITIAL_CALL_COUNTER_VALUE

    def raise_error_on_first_call() -> Path:
        nonlocal call_counter
        call_counter += tc.INCREMENT_ONE

        if call_counter > tc.ONE_CALL:
            return original_cwd
        else:
            raise OSError

    monkeypatch.setattr(Path, tc.CWD_OBJECT_NAME, raise_error_on_first_call)
    monkeypatch.setenv(tc.PWD_ENVIRONMENT_VARIABLE, str(original_cwd))
    monkeypatch.chdir(tmp_path)

    assert utils.working_directory(c) == Path.cwd()
    assert os.environ.get(tc.PWD_ENVIRONMENT_VARIABLE) == str(Path.cwd())


def test_print_remote_success_message_prints_correct_message(
    capsys: pytest.CaptureFixture[str], c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    expected = (
        tc.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=tc.STATUS_CODE_ONE_HUNDRED)
        + tc.NEWLINE
        + tc.TEST_MESSAGE_TEMPLATE.format(url=tc.TEST_URL)
        + tc.NEWLINE
    )

    utils.print_remote_success_message(
        c, tc.STATUS_CODE_ONE_HUNDRED, tc.TEST_URL, tc.TEST_MESSAGE_TEMPLATE
    )

    assert capsys.readouterr().out == expected


def test_promote_staging_allows_non_existent_final_root(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    final_root = tmp_path / tc.TEST_FINAL_ROOT
    staging_root = tmp_path / tc.TEST_STAGING_ROOT

    staging_root.mkdir()

    with open(
        staging_root / tc.TEST_TEXT_FILENAME, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.TEST_STRING)

    utils.promote_staging(c, staging_root, final_root)

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == tc.TEST_STRING


def test_promote_staging_allows_empty_final_root(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    final_root = tmp_path / tc.TEST_FINAL_ROOT
    staging_root = tmp_path / tc.TEST_STAGING_ROOT

    final_root.mkdir()
    staging_root.mkdir()

    with open(
        staging_root / tc.TEST_TEXT_FILENAME, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.TEST_STRING)

    utils.promote_staging(c, staging_root, final_root)

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == tc.TEST_STRING


def test_promote_staging_allows_non_empty_final_root(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    final_root = tmp_path / tc.TEST_FINAL_ROOT
    staging_root = tmp_path / tc.TEST_STAGING_ROOT

    staging_root.mkdir()
    (final_root / tc.TEST_FINAL_ROOT).mkdir(parents=True)

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.SECOND_TEST_STRING)

    with open(
        staging_root / tc.TEST_TEXT_FILENAME, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.TEST_STRING)

    utils.promote_staging(c, staging_root, final_root)

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == tc.TEST_STRING


def test_promote_staging_restores_final_root_if_promotion_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
) -> None:

    final_root = tmp_path / tc.TEST_FINAL_ROOT
    staging_root = tmp_path / tc.TEST_STAGING_ROOT

    final_root.mkdir()
    staging_root.mkdir()

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.SECOND_TEST_STRING)

    original_rename = os.rename

    def rename(source: Any, destination: Any) -> None:
        if Path(source) == staging_root:
            raise OSError

        original_rename(source, destination)

    monkeypatch.setattr(os, tc.RENAME_FUNCTION_NAME, rename)

    with pytest.raises(OSError):
        utils.promote_staging(c, staging_root, final_root)

    assert {path.name for path in tmp_path.iterdir()} == {
        final_root.name,
        staging_root.name,
    }

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == tc.SECOND_TEST_STRING


def test_raise_if_empty_raises_if_value_is_empty(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    utils.raise_if_empty(c, tc.TEST_STRING, tc.TEST_STRING)

    with pytest.raises(SCCSException):
        utils.raise_if_empty(c, tc.EMPTY_STRING, tc.TEST_STRING)


def test_safe_extract_zip_extracts_properly(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    zip_path = tmp_path / tc.TEST_ZIP_FILENAME
    destination_path = tmp_path / tc.DESTINATION_DIRECTORY
    member_path = tc.TEST_FOLDER_DIRECTORY + tc.PATH_SEPARATOR + tc.TEST_TEXT_FILENAME
    destination_path.mkdir()

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(member_path, tc.TEST_STRING)

    with zipfile.ZipFile(zip_path) as zf:
        utils.safe_extract_zip(c, zf, member_path, destination_path)

    assert (destination_path / member_path).read_text() == tc.TEST_STRING


def test_safe_extract_zip_extracts_directories_properly(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    zip_path = tmp_path / tc.TEST_ZIP_FILENAME
    destination_path = tmp_path / tc.DESTINATION_DIRECTORY
    member_path = tc.TEST_FOLDER_DIRECTORY + tc.PATH_SEPARATOR
    destination_path.mkdir()

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(member_path, tc.EMPTY_STRING)

    with zipfile.ZipFile(zip_path) as zf:
        utils.safe_extract_zip(c, zf, member_path, destination_path)

    assert (destination_path / tc.TEST_FOLDER_DIRECTORY).is_dir()


def test_safe_extract_zip_rejects_absolute_paths(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    archive = unittest.mock.Mock()
    member_path = str(tmp_path / tc.TEST_TEXT_FILENAME)

    with pytest.raises(
        SCCSException,
        match=re.escape(
            c.PATH_IS_ABSOLUTE_OR_CONTAINS_DOUBLE_PERIOD_ERROR_MESSAGE.format(
                entry_path=Path(member_path)
            )
        ),
    ):
        utils.safe_extract_zip(
            c,
            archive,
            member_path,
            tmp_path,
        )


@pytest.mark.parametrize(
    "member_path",
    [
        "../file.txt",
        "folder/../file.txt",
        "folder/../../file.txt",
    ],
)
def test_safe_extract_zip_rejects_double_period(
    tmp_path: Path, c: SCCSConstants, member_path: str
) -> None:

    archive = unittest.mock.Mock()

    with pytest.raises(SCCSException):
        utils.safe_extract_zip(
            c,
            archive,
            member_path,
            tmp_path,
        )


def test_safe_extract_zip_rejects_symlink_escape(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    destination_path = tmp_path / tc.DESTINATION_DIRECTORY
    outside_path = tmp_path / tc.TEST_STRING

    destination_path.mkdir()
    (destination_path / tc.TEST_SYMLINK_DIRECTORY).symlink_to(
        outside_path, target_is_directory=True
    )

    with pytest.raises(SCCSException):
        utils.safe_extract_zip(c, None, tc.TEST_SYMLINK_DIRECTORY, destination_path) # pyright: ignore[reportArgumentType]


def test_safe_extract_zip_missing_member(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    zip_path = tmp_path / tc.TEST_ZIP_FILENAME
    destination_path = tmp_path / tc.DESTINATION_DIRECTORY

    destination_path.mkdir()

    with zipfile.ZipFile(zip_path, "w") as zf, pytest.raises(KeyError):
        utils.safe_extract_zip(
            c,
            zf,
            tc.TEST_TEXT_FILENAME,
            destination_path,
        )


def test_safe_extract_zip_creates_parent_directories(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    zip_path = tmp_path / tc.TEST_ZIP_FILENAME
    destination_path = tmp_path / tc.DESTINATION_DIRECTORY

    nested_file_path = (
        tc.TEST_FOLDER_DIRECTORY
        + tc.PATH_SEPARATOR
        + tc.TEST_FOLDER_DIRECTORY
        + tc.PATH_SEPARATOR
        + tc.TEST_TEXT_FILENAME
    )

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(nested_file_path, tc.TEST_STRING)

    with zipfile.ZipFile(zip_path, "r") as zf:
        utils.safe_extract_zip(
            c,
            zf,
            nested_file_path,
            destination_path,
        )

    assert (
        destination_path
        / tc.TEST_FOLDER_DIRECTORY
        / tc.TEST_FOLDER_DIRECTORY
        / tc.TEST_TEXT_FILENAME
    ).read_text() == tc.TEST_STRING


def test_staged_repository_yields_sibling_temp_dir_of_sibling_root(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    sibling_root = tmp_path / tc.TEST_STRING
    final_root = tmp_path / tc.TEST_FINAL_ROOT

    with utils.staged_repository(c, sibling_root, final_root) as staging_root:
        assert staging_root.parent == sibling_root.parent


def test_staged_repository_promotes_staging_root_to_final_root(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    sibling_root = tmp_path / tc.TEST_STRING
    final_root = tmp_path / tc.TEST_FINAL_ROOT

    with utils.staged_repository(c, sibling_root, final_root) as staging_root, open(
        staging_root / tc.TEST_TEXT_FILENAME,
        "w",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        f.write(tc.TEST_STRING)

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == tc.TEST_STRING


def test_staged_repository_raises(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    sibling_root = tmp_path / tc.TEST_STRING
    final_root = tmp_path / tc.TEST_FINAL_ROOT

    staging_root: Path | None = None

    with pytest.raises(Exception):
        with utils.staged_repository(c, sibling_root, final_root) as staging_root:
            with open(
                staging_root / tc.TEST_TEXT_FILENAME,
                "w",
                encoding=tc.UTF_8,
                newline=tc.NEWLINE,
            ) as f:
                f.write(tc.TEST_STRING)

            raise Exception

    assert staging_root is not None
    assert not staging_root.exists()


def test_staged_repository_copies_copy_from_into_final_root(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    sibling_root = tmp_path / tc.TEST_STRING
    copy_from = tmp_path / tc.COPY_FROM_DIRECTORY
    final_root = tmp_path / tc.TEST_FINAL_ROOT

    (copy_from / tc.TEST_FOLDER_DIRECTORY).mkdir(parents=True)

    with open(
        copy_from / tc.TEST_TEXT_FILENAME, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.SECOND_TEST_STRING)

    with open(
        copy_from / tc.TEST_FOLDER_DIRECTORY / tc.TEST_TEXT_FILENAME,
        "w",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        f.write(tc.TEST_STRING)

    with utils.staged_repository(
        c, sibling_root, final_root, copy_from=copy_from
    ) as staging_root:
        with open(
            staging_root / tc.TEST_TEXT_FILENAME,
            "r",
            encoding=tc.UTF_8,
            newline=tc.NEWLINE,
        ) as f:
            assert f.read() == tc.SECOND_TEST_STRING

        assert (staging_root / tc.TEST_FOLDER_DIRECTORY).is_dir()

    with open(
        final_root / tc.TEST_TEXT_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == tc.SECOND_TEST_STRING

    with open(
        final_root / tc.TEST_FOLDER_DIRECTORY / tc.TEST_TEXT_FILENAME,
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        assert f.read() == tc.TEST_STRING


def test_wrap_html_returns_correct_html(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    assert utils.wrap_html(c, tc.TEST_STRING, tc.TEST_STRING) == (
        tc.HTML_BOILERPLATE_TEMPLATE.format(styles=tc.TEST_STRING, html=tc.TEST_STRING)
    )


def test_zip_buffer_yield_buffer_and_zipfile_object(c: SCCSConstants) -> None:

    with utils.zip_buffer(c) as (buffer, zf):
        assert type(buffer) == io.BytesIO
        assert type(zf) == zipfile.ZipFile


def test_zip_buffer_zips_buffer(c: SCCSConstants, tc: SCCSTestConstants) -> None:

    with utils.zip_buffer(c) as (buffer, zf):
        zf.writestr(tc.TEST_STRING, tc.TEST_STRING)

    with zipfile.ZipFile(buffer, "r") as zf:
        assert zf.read(tc.TEST_STRING) == tc.TEST_STRING.encode(tc.UTF_8)


def test_zip_buffer_raises_if_buffer_creation_fails(
    monkeypatch: pytest.MonkeyPatch, c: SCCSConstants
) -> None:

    def raise_error() -> NoReturn:
        raise Exception

    monkeypatch.setattr(io, "BytesIO", raise_error)

    with pytest.raises(SCCSException), utils.zip_buffer(c):
        pass


def test_zip_buffer_raises_if_error_occurs_during_zipping(c: SCCSConstants) -> None:

    with pytest.raises(SCCSException), utils.zip_buffer(c) as (buffer, zf):
        raise Exception


def test_zip_buffer_raises_if_buffer_seek_fails(
    monkeypatch: pytest.MonkeyPatch, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    class FailingSeekBuffer(io.BytesIO):
        def seek(self, offset: int, *args: Any, **kwargs: Any) -> int:
            if sys._getframe(1).f_globals.get("__name__") == tc.ZIPFILE_MODULE_NAME:
                return super().seek(offset, *args, **kwargs)
            raise Exception

    monkeypatch.setattr(io, "BytesIO", FailingSeekBuffer)

    with pytest.raises(SCCSException), utils.zip_buffer(c) as (buffer, zf):
        zf.writestr(tc.TEST_STRING, tc.TEST_STRING)
