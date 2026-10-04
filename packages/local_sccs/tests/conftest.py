import json
import shutil
from pathlib import Path

import pytest
from local_sccs.constants_classes import SCCSConstants
from local_sccs.repository_layout import TargetBranch
from test_constants import SCCSTestConstants


@pytest.fixture
def c() -> SCCSConstants:
    """
    Return the SCCS constants.
    """

    return SCCSConstants()


@pytest.fixture
def target(c: SCCSConstants) -> TargetBranch:
    """
    Return a target branch with no branch set.
    """

    return TargetBranch(c)


@pytest.fixture
def tc() -> SCCSTestConstants:
    """
    Return the SCCS test constants.
    """

    return SCCSTestConstants()


@pytest.fixture
def initialized_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tc: SCCSTestConstants
) -> Path:
    """
    Return a repository containing an initialized document and its first commit.
    """

    monkeypatch.setattr(
        SCCSConstants,
        tc.PROGRAM_START_TIME_SCCS_CONSTANTS_ATTRIBUTE_NAME,
        tc.EPOCH_ISO_DATETIME
    )

    repository_root = tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME
    sccs_root = repository_root / tc.SCCS_DIRECTORY
    objects_root = sccs_root / tc.OBJECTS_DIRECTORY
    docx_objects_root = objects_root / tc.DOCUMENT_DIRECTORY
    html_objects_root = objects_root / tc.HTML_DIRECTORY
    view_html_objects_root = objects_root / tc.VIEW_HTML_DIRECTORY
    test_document_path = Path(__file__).parent / tc.TEST_DOCUMENT_FILENAME
    docx_object_path = docx_objects_root / (tc.TEST_COMMIT_HASH + tc.DOCUMENT_EXTENSION)
    html_object_path = html_objects_root / (tc.TEST_COMMIT_HASH + tc.HTML_EXTENSION)
    view_html_object_path = (
        view_html_objects_root / (tc.TEST_COMMIT_HASH + tc.HTML_EXTENSION)
    )
    metadata_path = sccs_root / tc.METADATA_JSON

    docx_objects_root.mkdir(parents=True)
    html_objects_root.mkdir(parents=True)
    view_html_objects_root.mkdir(parents=True)

    with open(
        html_object_path, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.DEFAULT_HTML_STYLES + tc.TEST_DOCUMENT_HTML)

    with open(
        view_html_object_path, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(
            tc.HTML_BOILERPLATE_TEMPLATE.format(
                styles=tc.DEFAULT_HTML_STYLES, html=tc.TEST_DOCUMENT_HTML
            )
        )

    shutil.copy(test_document_path, repository_root)
    shutil.copy(test_document_path, docx_object_path)

    with open(
        metadata_path, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        json.dump(tc.TEST_INITIALIZATION_METADATA, f, indent=tc.JSON_INDENT)

    return repository_root


@pytest.fixture
def repository_with_modified_document(
    initialized_repository: Path, tc: SCCSTestConstants
) -> Path:
    """
    Return a repository whose working document differs from the committed document.
    """

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )

    return initialized_repository


@pytest.fixture
def repository_with_multiple_commits(initialized_repository: Path) -> Path:
    """
    Return a repository containing a second commit of a modified document.
    """

    tc = SCCSTestConstants()

    with open(
        initialized_repository
        / tc.SCCS_DIRECTORY
        / tc.OBJECTS_DIRECTORY
        / tc.HTML_DIRECTORY
        / (tc.SECOND_COMMIT_HASH + tc.HTML_EXTENSION), "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.DEFAULT_HTML_STYLES + tc.SECOND_COMMIT_TEST_DOCUMENT_HTML)

    with open(
        initialized_repository
        / tc.SCCS_DIRECTORY
        / tc.OBJECTS_DIRECTORY
        / tc.VIEW_HTML_DIRECTORY
        / (tc.SECOND_COMMIT_HASH + tc.HTML_EXTENSION), "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(
            tc.HTML_BOILERPLATE_TEMPLATE.format(
                styles=tc.DEFAULT_HTML_STYLES, html=tc.SECOND_COMMIT_TEST_DOCUMENT_HTML
            )
        )

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )
    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository
        / tc.SCCS_DIRECTORY
        / tc.OBJECTS_DIRECTORY
        / tc.DOCUMENT_DIRECTORY
        / (tc.SECOND_COMMIT_HASH + tc.DOCUMENT_EXTENSION)
    )

    with open(
        initialized_repository / tc.SCCS_DIRECTORY / tc.METADATA_JSON, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        json.dump(tc.SECOND_COMMIT_TEST_METADATA, f, indent=tc.JSON_INDENT)

    return initialized_repository

