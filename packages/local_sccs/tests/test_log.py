import shutil
from typing import Any

from local_sccs.constants_classes import SCCSConstants
from local_sccs import log
import pytest
from test_constants import SCCSTestConstants
from local_sccs.repository_layout import RepositoryData, RepositoryIO, RepositoryPaths, RepositoryStatus, RepositoryWrite, TargetBranch
from pathlib import Path
from local_sccs.exceptions import SCCSException
from types import FunctionType

@pytest.mark.parametrize(
    "log_data, expected_output",
    [
        ( 
            {
                "ef4a6cd9a3fa5fd50c9f8ed03ea569671b3a41f6485d0446f891bda0ee2dd06f": {
                    "timestamp": "1970-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "Initial commit (This is a default commit message for the initial version)"
                },
                "f797d149c9887b91ebf065685775156ac33c29ccee0cb40b68f98d715114fe45": {
                    "timestamp": "1971-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "Second commit"
                },
            },            
            "------------------------------\n"
            "Commit File: ef4a6cd9a3\n"
            "Author: test <test@example.com>\n"
            "Date: 1970-01-01T00:00:00\n"
            "Message: Initial commit (This is a default commit message for the initial version)\n"
            "------------------------------\n"
            "------------------------------\n"
            "Commit File: f797d149c9\n"
            "Author: test <test@example.com>\n"
            "Date: 1971-01-01T00:00:00\n"
            "Message: Second commit\n"
            "------------------------------\n"
        ),
        (
            {
                "test": {
                    "timestamp": "1970-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "test"
                },
                "test2": {
                    "timestamp": "1971-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "test"
                }
            },
        "------------------------------\n"
        "Commit File: test\n"
        "Author: test <test@example.com>\n"
        "Date: 1970-01-01T00:00:00\n"
        "Message: test\n"
        "------------------------------\n"
        "------------------------------\n"
        "Commit File: test2\n"
        "Author: test <test@example.com>\n"
        "Date: 1971-01-01T00:00:00\n"
        "Message: test\n"
        "------------------------------\n"
        )
    ]
)
def test_print_log_prints_log_entries(
    c: SCCSConstants,
    expected_output: str,
    log_data: dict,
    capsys: pytest.CaptureFixture[str]
) -> None:
    log.print_log(c, log_data)
    assert capsys.readouterr().out == expected_output


@pytest.mark.parametrize(
    "log_data, expected_output",
    [
        ( 
            {
                "ef4a6cd9a3fa5fd50c9f8ed03ea569671b3a41f6485d0446f891bda0ee2dd06f": {
                    "timestamp": "1970-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "Initial commit (This is a default commit message for the initial version)"
                },
                "f797d149c9887b91ebf065685775156ac33c29ccee0cb40b68f98d715114fe45": {
                    "timestamp": "1971-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "Second commit"
                },
            },            
            "------------------------------\n"
            "Commit File: ef4a6cd9a3\n"
            "Author: test <test@example.com>\n"
            "Date: 1970-01-01T00:00:00\n"
            "Message: Initial commit (This is a default commit message for the initial version)\n"
            "------------------------------\n"
            "------------------------------\n"
            "Commit File: f797d149c9\n"
            "Author: test <test@example.com>\n"
            "Date: 1971-01-01T00:00:00\n"
            "Message: Second commit\n"
            "------------------------------\n"
        ),
        (
            {
                "test": {
                    "timestamp": "1970-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "test"
                },
                "test2": {
                    "timestamp": "1971-01-01T00:00:00",
                    "author": "test <test@example.com>",
                    "message": "test"
                }
            },
        "------------------------------\n"
        "Commit File: test\n"
        "Author: test <test@example.com>\n"
        "Date: 1970-01-01T00:00:00\n"
        "Message: test\n"
        "------------------------------\n"
        "------------------------------\n"
        "Commit File: test2\n"
        "Author: test <test@example.com>\n"
        "Date: 1971-01-01T00:00:00\n"
        "Message: test\n"
        "------------------------------\n"
        )
    ]
)
def test_log_main_prints_correct_log_entries(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    log_data: dict,
    expected_output: str,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    monkeypatch.setattr(RepositoryIO, "read_log", lambda *args, **kwargs: log_data)
    
    log.main(c, rd, ri, rs)
    assert capsys.readouterr().out == expected_output


def test_log_main_prints_log(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    log.main(c, rd, ri, rs)
    assert capsys.readouterr().out == tc.TEST_REPOSITORY_LOG_OUTPUT


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
def test_log_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    missing_resource_path_name: str,
    expected_reported_resource_path_name: str,
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
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
        log.main(c, rd, ri, rs)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


@pytest.mark.parametrize(
    "module, method_name",
    [
        (RepositoryData, "current_branch"),
        (RepositoryIO, "read_log"),
    ]
)
def test_log_main_raises_if_method_raises(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    method_name: str,
    raise_exception: FunctionType
) -> None:
    rd = RepositoryData(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    ri = RepositoryIO(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    rs = RepositoryStatus(initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)

    monkeypatch.setattr(module, method_name, raise_exception)
    with pytest.raises(Exception):
        log.main(c, rd, ri, rs)


def test_log_main_resets_target_on_error(
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
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(RepositoryStatus, "validate_repository_layout", raise_exception)

    with pytest.raises(Exception):
        log.main(c, rd, ri, rs)

    assert target.get() is None