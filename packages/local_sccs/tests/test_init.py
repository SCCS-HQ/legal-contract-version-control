import json
import os
import shutil
import tempfile
from pathlib import Path
from types import FunctionType
from unittest import mock

import pytest
from local_sccs import init, utils
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import (
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)
from test_constants import SCCSTestConstants


@pytest.mark.parametrize("key", ["name", "email", "test"])
def test_ask_config_input_raises_if_empty(
    key: str, c: SCCSConstants, tc: SCCSTestConstants
) -> None:

    with mock.patch("builtins.input", return_value=""):
        with pytest.raises(SCCSException) as e:
            init.ask_config_input(c, key)

    assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
        field=key.capitalize()
    )


@pytest.mark.parametrize(
    "key, value",
    [("name", "John Doe"), ("email", "john.doe@example.com"), ("test", "test_value")],
)
def test_ask_config_input_returns_input(c: SCCSConstants, key: str, value: str) -> None:

    with mock.patch("builtins.input", return_value=value):
        assert init.ask_config_input(c, key) == value


def test_copy_document_to_objects_as_document_and_html_raises_document_read_fails(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    with mock.patch("builtins.open", side_effect=Exception):
        with pytest.raises(SCCSException) as e:
            init.copy_document_to_objects_as_document_and_html(
                c, document_path, tc.TEST_COMMIT_IDENTIFIER, rp
            )
        assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_copy_document_to_objects_as_document_and_html_raises_if_copy_fails(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    with mock.patch("shutil.copy2", side_effect=Exception):
        with pytest.raises(SCCSException) as e:
            init.copy_document_to_objects_as_document_and_html(
                c, document_path, tc.TEST_COMMIT_IDENTIFIER, rp
            )
        assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_copy_document_to_objects_as_document_and_html_raises_if_html_write_fails(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    with mock.patch("builtins.open", side_effect=[tc.TEST_STRING, Exception]):
        with pytest.raises(SCCSException) as e:
            init.copy_document_to_objects_as_document_and_html(
                c, Path(tc.TEST_STRING), tc.TEST_COMMIT_IDENTIFIER, rp
            )
        assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_copy_document_to_objects_as_document_and_html_raises_if_view_html_write_fails(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    rp = RepositoryPaths(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    with mock.patch(
        "builtins.open", side_effect=[tc.TEST_STRING, tc.TEST_STRING, Exception]
    ):
        with pytest.raises(SCCSException) as e:
            init.copy_document_to_objects_as_document_and_html(
                c, Path(tc.TEST_STRING), tc.TEST_COMMIT_IDENTIFIER, rp
            )
        assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_copy_document_to_objects_as_document_and_html_copies_and_converts_document_to_html(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    document_path = tmp_path / tc.TEST_DOCUMENT_FILENAME

    shutil.copy(
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME,
        document_path,
    )

    document_objects_path = Path(
        tmp_path / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY / tc.DOCUMENT_DIRECTORY
    )
    html_objects_path = Path(
        tmp_path / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY / tc.HTML_DIRECTORY
    )
    view_html_objects_path = Path(
        tmp_path / tc.SCCS_DIRECTORY / tc.OBJECTS_DIRECTORY / tc.VIEW_HTML_DIRECTORY
    )

    directories = [
        document_objects_path,
        html_objects_path,
        view_html_objects_path,
    ]

    for i in directories:
        i.mkdir(parents=True, exist_ok=True)

    init.copy_document_to_objects_as_document_and_html(
        c, document_path, tc.TEST_COMMIT_IDENTIFIER, rp
    )

    with open(document_path, "rb") as f:
        document_content = f.read()

    with open(
        Path(document_objects_path / tc.TEST_COMMIT_IDENTIFIER).with_suffix(
            c.DOCUMENT_EXTENSION
        ),
        "rb",
    ) as f:
        document_object_content = f.read()

    with open(
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME,
        "rb",
    ) as f:
        original_document_content = f.read()

        assert original_document_content == document_content
        assert original_document_content == document_object_content

    with open(
        Path(html_objects_path / tc.TEST_COMMIT_IDENTIFIER).with_suffix(
            c.HTML_EXTENSION
        ),
        "r",
        encoding=c.UTF_8,
    ) as f:
        assert f.read() == tc.DEFAULT_HTML_STYLES + tc.TEST_DOCUMENT_HTML

    with open(
        Path(view_html_objects_path / tc.TEST_COMMIT_IDENTIFIER).with_suffix(
            c.HTML_EXTENSION
        ),
        "r",
        encoding=c.UTF_8,
    ) as f:
        assert f.read() == tc.HTML_BOILERPLATE_TEMPLATE.format(
            styles=tc.DEFAULT_HTML_STYLES, html=tc.TEST_DOCUMENT_HTML
        )


def test_copy_document_to_repository_directory_raises_if_copy_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:

    monkeypatch.setattr(shutil, "copy2", raise_exception)

    with pytest.raises(SCCSException) as e:
        init.copy_document_to_repository_directory(
            c, Path(tc.TEST_STRING), Path(tc.TEST_STRING)
        )

    assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_copy_document_to_repository_directory_copies_document_to_repository_directory(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    init.copy_document_to_repository_directory(c, tmp_path, document_path)

    with open(Path(tmp_path / tc.TEST_DOCUMENT_FILENAME), "rb") as f:
        repository_document_content = f.read()

    with open(document_path, "rb") as f:
        original_document_content = f.read()

        assert original_document_content == repository_document_content


def test_create_sccs_directory_layout_creates_expected_directories(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants, target: TargetBranch
) -> None:
    rp = RepositoryPaths(
        tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME,
        tc.TEST_DOCUMENT_REPOSITORY_NAME,
        c,
        target,
    )

    paths = [
        rp.sccs_path(),
        rp.objects_path(),
        rp.document_objects_path(),
        rp.html_objects_path(),
        rp.view_html_objects_path(),
    ]

    init.create_sccs_directory_layout(c, rp, rs)

    for i in paths:
        assert i.is_dir()


def test_create_sccs_directory_layout_raises_if_directory_creation_fails(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    rp = RepositoryPaths(
        tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME,
        tc.TEST_DOCUMENT_REPOSITORY_NAME,
        c,
        target,
    )

    monkeypatch.setattr(Path, "mkdir", raise_exception)

    with pytest.raises(SCCSException) as e:
        init.create_sccs_directory_layout(c, rp, rs)

    assert str(e.value) == tc.INIT_CREATE_ERROR_MESSAGE


def test_create_sccs_directory_layout_resets_target_even_after_failure(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    rp = RepositoryPaths(
        tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    rs = RepositoryStatus(
        tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME,
        tc.TEST_DOCUMENT_REPOSITORY_NAME,
        c,
        target,
    )

    monkeypatch.setattr(Path, "mkdir", raise_exception)

    with pytest.raises(SCCSException) as e:
        init.create_sccs_directory_layout(c, rp, rs)

    assert rs.target.get() is None


def test_finalize_repository_creation_prints_warning_if_document_deletion_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    capsys: pytest.CaptureFixture,
) -> None:
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    staging_rp = RepositoryPaths(
        tmp_path / tc.SECOND_TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )

    monkeypatch.setattr(utils, "promote_staging", lambda *args, **kwargs: None)
    monkeypatch.setattr(os, "remove", raise_exception)

    init.finalize_repository_creation(c, Path(tc.TEST_STRING), rp, staging_rp)

    assert (
        capsys.readouterr().out.strip()
        == tc.SOURCE_FILE_DELETION_ERROR_WARNING_TEMPLATE.format(
            document_path=tc.TEST_STRING
        )
    )


def test_finalize_repository_creation_raises_if_staging_deletion_fails(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    staging_rp = RepositoryPaths(
        tmp_path / tc.SECOND_TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )

    for i in [rp.root, staging_rp.root]:
        i.mkdir(parents=True, exist_ok=True)

    call_count = 0

    def fake_rename(*a, **k) -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise OSError

    monkeypatch.setattr(os, "rename", fake_rename)
    monkeypatch.setattr(os, "remove", lambda *a, **k: None)

    with pytest.raises(OSError):
        init.finalize_repository_creation(c, Path(tc.TEST_STRING), rp, staging_rp)


def test_finalize_repository_creation_promotes_staging_to_repository_deletes_staging_and_deletes_document(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    staging_rp = RepositoryPaths(
        tmp_path / tc.SECOND_TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    document_path = tmp_path / tc.TEST_STRING / tc.TEST_DOCUMENT_FILENAME

    for i in [rp.root, staging_rp.root]:
        i.mkdir(parents=True, exist_ok=True)

    document_path.write_text(tc.TEST_STRING)

    init.finalize_repository_creation(c, Path(tc.TEST_STRING), rp, staging_rp)

    assert not staging_rp.root.exists()

    assert not document_path.exists()


def test_finalize_repository_creation_promotes_staging_to_repository_and_deletes_staging_even_if_document_deletion_fails(
    tmp_path: Path,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    staging_rp = RepositoryPaths(
        tmp_path / tc.SECOND_TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c
    )
    document_path = tmp_path / tc.TEST_DOCUMENT_FILENAME

    for i in [rp.root, staging_rp.root]:
        i.mkdir(parents=True, exist_ok=True)

    document_path.write_text(tc.TEST_STRING)

    monkeypatch.setattr(os, "remove", raise_exception)

    init.finalize_repository_creation(c, Path(tc.TEST_STRING), rp, staging_rp)

    assert not staging_rp.root.exists()

    assert document_path.exists()


def test_print_init_success_message_prints_expected_message(
    capsys: pytest.CaptureFixture, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    init.print_init_success_message(c)

    assert capsys.readouterr().out.strip() == tc.INIT_SUCCESS_MESSAGE


def test_validate_file_requirements_raises_if_path_does_not_exist(
    c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    with pytest.raises(SCCSException) as e:
        init.validate_file_requirements(c, Path(tc.TEST_STRING))

        assert str(
            e.value
        ) == tc.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
            file_path=Path(tc.TEST_STRING)
        )


def test_validate_file_requirements_raises_if_path_is_not_a_file(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    directory_path = tmp_path / tc.TEST_STRING
    directory_path.mkdir(parents=True, exist_ok=True)

    with pytest.raises(SCCSException) as e:
        init.validate_file_requirements(c, directory_path)

        assert str(
            e.value
        ) == tc.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
            file_path=directory_path
        )


def test_validate_file_requirements_raises_if_path_is_not_a_docx_file(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    file_path = (tmp_path / tc.TEST_STRING).with_suffix(tc.HTML_EXTENSION)

    with pytest.raises(SCCSException) as e:
        init.validate_file_requirements(c, file_path)

        assert str(e.value) == tc.INVALID_FILE_TYPE_ERROR_MESSAGE


def test_validate_file_requirements_passes_if_path_is_a_existing_docx_file(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    file_path = (tmp_path / tc.TEST_STRING).with_suffix(tc.DOCUMENT_EXTENSION)
    file_path.write_text(tc.TEST_STRING)

    init.validate_file_requirements(c, file_path)


def test_validate_no_prev_init_raises_if_sccs_directory_exists(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    (tmp_path / tc.TEST_STRING / c.SCCS_DIRECTORY).mkdir(parents=True, exist_ok=True)

    with pytest.raises(SCCSException) as e:
        init.validate_no_prev_init(c, rp)

        assert str(e.value) == tc.ALREADY_INIT_ERROR_MESSAGE


def test_validate_no_prev_init_passes_if_sccs_directory_does_not_exist(
    tmp_path: Path, c: SCCSConstants, tc: SCCSTestConstants
) -> None:
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)

    init.validate_no_prev_init(c, rp)


def test_write_starting_metadata_raises_if_write_to_commit_metadata_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    target: TargetBranch,
) -> None:
    ri = RepositoryIO(Path(tc.TEST_STRING), tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    monkeypatch.setattr(
        ri, "document_html_byte_hash", lambda *args, **kwargs: tc.TEST_STRING
    )
    monkeypatch.setattr(ri, "write_metadata", raise_exception)

    with pytest.raises(SCCSException) as e:
        init.write_starting_metadata(
            c, tc.TEST_COMMIT_IDENTIFIER, tc.TEST_STRING, tc.TEST_STRING, ri
        )

    assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_write_starting_metadata_writes_expected_metadata_to_commit_metadata_file(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    target: TargetBranch,
    tmp_path: Path,
) -> None:
    ri = RepositoryIO(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(
        ri, "document_html_byte_hash", lambda *args, **kwargs: tc.TEST_STRING
    )
    monkeypatch.setattr(SCCSConstants, "PROGRAM_START_TIME", tc.EPOCH_ISO_DATETIME)

    metadata_path = tmp_path / tc.TEST_STRING / tc.SCCS_DIRECTORY / tc.METADATA_JSON
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    init.write_starting_metadata(
        c, tc.TEST_COMMIT_IDENTIFIER, tc.TEST_STRING, tc.TEST_STRING, ri
    )

    with open(metadata_path, "r", encoding=c.UTF_8) as f:
        assert json.load(f) == {
            tc.BRANCHES_DICT_KEY: {
                tc.MAIN_BRANCH_NAME: {
                    tc.HISTORY_DICT_KEY: {
                        tc.INITIAL_COMMIT_DICT_KEY: tc.TEST_COMMIT_IDENTIFIER,
                        tc.LATEST_COMMIT_DICT_KEY: tc.TEST_COMMIT_IDENTIFIER,
                        tc.LATEST_COMMIT_NUMBER_DICT_KEY: tc.INITIAL_COMMIT_NUMBER,
                        tc.COMMIT_ORDER_DICT_KEY: {
                            tc.INITIAL_COMMIT_NUMBER_DICT_KEY: tc.TEST_COMMIT_IDENTIFIER
                        },
                    },
                    tc.LOG_DICT_KEY: {
                        tc.TEST_COMMIT_IDENTIFIER: {
                            tc.TIMESTAMP_DICT_KEY: tc.EPOCH_ISO_DATETIME,
                            tc.AUTHOR_DICT_KEY: tc.COMMIT_AUTHOR_TEMPLATE.format(
                                name=tc.TEST_STRING, email=tc.TEST_STRING
                            ),
                            tc.MESSAGE_DICT_KEY: tc.INIT_COMMIT_MESSAGE,
                        }
                    },
                    tc.BYTE_HASH_DICT_KEY: {
                        tc.TEST_COMMIT_IDENTIFIER: ri.document_html_byte_hash()
                    },
                }
            },
            tc.COMMIT_MESSAGES_DICT_KEY: {
                tc.TEST_COMMIT_IDENTIFIER: tc.INIT_COMMIT_MESSAGE
            },
            tc.CURRENT_BRANCH_DICT_KEY: dict(tc.DEFAULT_BRANCH_DATA),
        }


def test_init_main_raises_if_sccs_directory_exists(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    initialized_repository: Path,
    target: TargetBranch,
) -> None:
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        init.main(c, Path(tc.TEST_STRING), ri, rp, rs, rw)
    assert str(e.value) == tc.ALREADY_INIT_ERROR_MESSAGE


def test_init_main_raises_if_document_path_does_not_exist(
    c: SCCSConstants, tc: SCCSTestConstants, tmp_path: Path, target: TargetBranch
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = Path(tc.TEST_STRING).with_suffix(tc.DOCUMENT_EXTENSION)

    with pytest.raises(SCCSException) as e:
        init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
        file_path=document_path
    )


def test_init_main_raises_if_document_path_is_not_a_file(
    c: SCCSConstants, tc: SCCSTestConstants, tmp_path: Path, target: TargetBranch
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    directory_path = Path(tmp_path / tc.TEST_STRING).with_suffix(tc.DOCUMENT_EXTENSION)

    directory_path.mkdir(parents=True, exist_ok=True)

    with pytest.raises(SCCSException) as e:
        init.main(c, directory_path, ri, rp, rs, rw)
    assert str(e.value) == tc.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
        file_path=directory_path
    )


def test_init_main_raises_if_document_path_is_not_a_docx_file(
    c: SCCSConstants, tc: SCCSTestConstants, tmp_path: Path, target: TargetBranch
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = Path(tc.TEST_STRING).with_suffix(tc.HTML_EXTENSION)

    with pytest.raises(SCCSException) as e:
        init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.INVALID_FILE_TYPE_ERROR_MESSAGE


def test_init_main_raises_if_staging_directory_creation_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    monkeypatch.setattr(tempfile, "mkdtemp", raise_exception)

    with pytest.raises(OSError) as e:
        init.main(c, document_path, ri, rp, rs, rw)


def test_init_main_raises_if_directory_creation_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    monkeypatch.setattr(Path, "mkdir", raise_exception)

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        with pytest.raises(SCCSException) as e:
            init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.INIT_CREATE_ERROR_MESSAGE


def test_init_main_raises_if_document_read_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    monkeypatch.setattr("builtins.open", raise_exception)

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        with pytest.raises(SCCSException) as e:
            init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_init_main_raises_if_write_to_commit_metadata_fails(
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    monkeypatch.setattr(RepositoryIO, "write_metadata", raise_exception)

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        with pytest.raises(SCCSException) as e:
            init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.INIT_COPY_ERROR_MESSAGE


def test_init_main_raises_if_name_is_empty(
    c: SCCSConstants, tc: SCCSTestConstants, tmp_path: Path, target: TargetBranch
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    with mock.patch("builtins.input", side_effect=["", tc.TEST_STRING]):
        with pytest.raises(SCCSException) as e:
            init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field="Name")


def test_init_main_raises_if_email_is_empty(
    c: SCCSConstants, tc: SCCSTestConstants, tmp_path: Path, target: TargetBranch
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    with mock.patch("builtins.input", side_effect=[tc.TEST_STRING, ""]):
        with pytest.raises(SCCSException) as e:
            init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field="Email")


def test_init_main_raises_if_name_contains_invalid_characters(
    c: SCCSConstants, tc: SCCSTestConstants, tmp_path: Path, target: TargetBranch
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    with mock.patch(
        "builtins.input", side_effect=[tc.TEST_STRING + "<", tc.TEST_STRING]
    ):
        with pytest.raises(SCCSException) as e:
            init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.INVALID_CHARACTER_IN_NAME_OR_EMAIL_ERROR_MESSAGE


def test_init_main_raises_if_email_contains_invalid_characters(
    c: SCCSConstants, tc: SCCSTestConstants, tmp_path: Path, target: TargetBranch
) -> None:
    ri = RepositoryIO(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rp = RepositoryPaths(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rw = RepositoryWrite(tmp_path, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    with mock.patch(
        "builtins.input", side_effect=[tc.TEST_STRING, tc.TEST_STRING + "<"]
    ):
        with pytest.raises(SCCSException) as e:
            init.main(c, document_path, ri, rp, rs, rw)
    assert str(e.value) == tc.INVALID_CHARACTER_IN_NAME_OR_EMAIL_ERROR_MESSAGE


def test_init_main_raises_if_document_deletion_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    capsys: pytest.CaptureFixture,
) -> None:
    ri = RepositoryIO(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    monkeypatch.setattr(os, "remove", raise_exception)

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        init.main(c, document_path, ri, rp, rs, rw)

    assert (
        capsys.readouterr()
        .out.strip()
        .startswith(
            tc.SOURCE_FILE_DELETION_ERROR_WARNING_TEMPLATE.format(
                document_path=document_path
            )
        )
    )


def test_init_main_raises_if_staging_deletion_fails(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    capsys: pytest.CaptureFixture,
) -> None:
    ri = RepositoryIO(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    monkeypatch.setattr(os, "rename", raise_exception)

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        with pytest.raises(OSError) as e:
            init.main(c, document_path, ri, rp, rs, rw)
        assert not str(e.value)


def test_init_main_deletes_staging_directory_if_error_occurs(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    capsys: pytest.CaptureFixture,
) -> None:
    ri = RepositoryIO(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    document_path = (
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME
    )

    monkeypatch.setattr(os, "rename", raise_exception)

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        with pytest.raises(OSError) as e:
            init.main(c, document_path, ri, rp, rs, rw)
            assert not str(e.value)

        staging_dirs = list(
            (tmp_path / tc.TEST_STRING).parent.glob(
                tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
            )
        )

    assert not staging_dirs


def test_init_main_prints_success_message(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    capsys: pytest.CaptureFixture,
) -> None:
    ri = RepositoryIO(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    document_path = tmp_path / tc.TEST_DOCUMENT_FILENAME

    shutil.copy(
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME,
        document_path,
    )

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        init.main(c, document_path, ri, rp, rs, rw)

    assert capsys.readouterr().out.strip() == tc.INIT_SUCCESS_MESSAGE


def test_init_main_properly_initializes_repository_with_expected_files_and_directories(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    tmp_path: Path,
    target: TargetBranch,
    initialized_repository: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        SCCSConstants,
        tc.PROGRAM_START_TIME_SCCS_CONSTANTS_ATTRIBUTE_NAME,
        tc.EPOCH_ISO_DATETIME,
    )

    ri = RepositoryIO(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rp = RepositoryPaths(tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c)
    rs = RepositoryStatus(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw = RepositoryWrite(
        tmp_path / tc.TEST_STRING, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    document_path = tmp_path / tc.TEST_DOCUMENT_FILENAME

    shutil.copy(
        Path(__file__).parent / tc.TEST_DOCUMENTS_DIRECTORY / tc.TEST_DOCUMENT_FILENAME,
        document_path,
    )

    with mock.patch("builtins.input", return_value=tc.TEST_STRING):
        init.main(c, document_path, ri, rp, rs, rw)

    with open(
        Path(initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON),
        "r+",
        encoding=c.UTF_8,
    ) as f:
        metadata = json.load(f)
        metadata[tc.CONFIG_DICT_KEY].pop(tc.REMOTE_KEY, None)
        f.seek(0)
        f.truncate()
        json.dump(metadata, f, indent=tc.JSON_INDENT)

    files_a = {
        i.relative_to(initialized_repository)
        for i in initialized_repository.rglob("*")
        if i.is_file()
    }

    files_b = {
        i.relative_to(tmp_path / tc.TEST_STRING)
        for i in (tmp_path / tc.TEST_STRING).rglob("*")
        if i.is_file()
    }

    assert files_a == files_b

    for i in files_a:
        assert (initialized_repository / i).read_bytes() == (
            tmp_path / tc.TEST_STRING / i
        ).read_bytes()
