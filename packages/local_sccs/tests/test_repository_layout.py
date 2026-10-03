from local_sccs.repository_layout import (
    TargetBranch, RepositoryData, RepositoryIO, RepositoryPaths, RepositoryStatus, RepositoryWrite
)
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
import pytest
from pathlib import Path
import shutil
import json
from test_constants import SCCSTestConstants
import filecmp

 
@pytest.fixture
def initialized_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    tc = SCCSTestConstants()

    monkeypatch.setattr(
        SCCSConstants,
        tc.PROGRAM_START_TIME_SCCS_CONSTANTS_ATTRIBUTE_NAME,
        tc.EPOCH_ISO_DATETIME
    )

    repository_root = tmp_path / tc.TEST_DOCUMENT_REPOSITORY_NAME
    sccs_root = repository_root / tc.SCCS_PATH_SEGMENT
    objects_root = sccs_root / tc.OBJECTS_PATH_SEGMENT
    docx_objects_root = objects_root / tc.DOCX_OBJECTS_PATH_SEGMENT
    html_objects_root = objects_root / tc.HTML_OBJECTS_PATH_SEGMENT
    view_html_objects_root = objects_root / tc.VIEW_HTML_OBJECTS_PATH_SEGMENT
    test_document_path = Path(__file__).parent / tc.TEST_DOCUMENT_FILENAME
    docx_object_path = docx_objects_root / (tc.TEST_COMMIT_HASH + tc.DOCX_EXTENSION)
    html_object_path = html_objects_root / (tc.TEST_COMMIT_HASH + tc.HTML_EXTENSION)
    view_html_object_path = (
        view_html_objects_root / (tc.TEST_COMMIT_HASH + tc.HTML_EXTENSION)
    )
    metadata_path = sccs_root / tc.METADATA_JSON_FILENAME

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
def repository_with_multiple_commits(initialized_repository: Path) -> Path:
    tc = SCCSTestConstants()

    with open(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.HTML_OBJECTS_PATH_SEGMENT
        / (tc.SECOND_COMMIT_HASH + tc.HTML_EXTENSION), "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        f.write(tc.DEFAULT_HTML_STYLES + tc.SECOND_COMMIT_TEST_DOCUMENT_HTML)

    with open(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.VIEW_HTML_OBJECTS_PATH_SEGMENT
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
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.SECOND_COMMIT_HASH + tc.DOCX_EXTENSION)
    )

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME, "w", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        json.dump(tc.SECOND_COMMIT_TEST_METADATA, f, indent=tc.JSON_INDENT)

    return initialized_repository


def test_repository_data_matching_commit_files_returns_correct_commit_files(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    expected = [
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_COMMIT_HASH + tc.DOCX_EXTENSION)
    ]

    assert rd._matching_commit_files(tc.TEST_COMMIT_HASH, "docx") == expected


def test_repository_data_matching_commit_files_raises_if_commit_files_missing(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException):
        rd._matching_commit_files(tc.TEST_STRING, "docx")


def test_repository_data_matching_commit_files_raises_if_extra_commit_files_found(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    (
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_COMMIT_HASH + "2" + tc.DOCX_EXTENSION)
    ).write_text(
        tc.TEST_STRING,
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    )

    with pytest.raises(SCCSException):
        rd._matching_commit_files(tc.TEST_COMMIT_HASH, "docx")


def test_repository_data_base_repository_url_returns_correct_url(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME, "r+", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        metadata = json.load(f)
        metadata[tc.CONFIG_KEY][tc.REMOTE_KEY] = tc.TEST_STRING
        f.seek(0)
        json.dump(metadata, f, indent=tc.JSON_INDENT)
        f.truncate()

    assert rd.base_repository_url() == tc.TEST_STRING


def test_repository_data_branches_returns_correct_branches(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert rd.branches() == [tc.MAIN_BRANCH_NAME]


def test_repository_data_commit_file_bytes_returns_correct_bytes(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with open(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_COMMIT_HASH + tc.DOCX_EXTENSION),
        "rb",
    ) as f:
        expected = f.read()

    assert (
        rd.commit_file_bytes(tc.TEST_COMMIT_HASH, "docx") == expected
    )


def test_repository_data_commit_identifier_to_full_path_returns_correct_path(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    expected = (
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_COMMIT_HASH + tc.DOCX_EXTENSION)
    )

    assert (
        rd.commit_identifier_to_full_path(tc.TEST_COMMIT_HASH, "docx") == expected
    )


def test_repository_data_commit_file_bytes_raises_if_commit_identifier_length_invalid(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException) as e:
        rd.commit_file_bytes(tc.TEST_STRING, "docx")

    assert str(e.value) == c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE


def test_repository_data_commit_file_bytes_raises_if_no_matching_commit_file_found(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException) as e:
        rd.commit_file_bytes(tc.SECOND_COMMIT_HASH, "docx")

    assert str(e.value) == c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
        file_path=tc.SECOND_COMMIT_HASH
    )


def test_repository_data_commit_file_bytes_raises_if_multiple_matching_commit_files_found(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    (
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_COMMIT_HASH + "2" + tc.DOCX_EXTENSION)
    ).write_text(
        tc.TEST_STRING,
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    )

    with pytest.raises(SCCSException) as e:
        rd.commit_file_bytes(tc.TEST_COMMIT_HASH, "docx")

    assert str(e.value) == c.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(
        commit_identifier=tc.TEST_COMMIT_HASH
    )


def test_repository_data_commit_file_bytes_raises_for_display_length_multiple_matches(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    (
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_COMMIT_HASH + "2" + tc.DOCX_EXTENSION)
    ).write_text(
        tc.TEST_STRING,
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    )

    with pytest.raises(SCCSException) as e:
        rd.commit_file_bytes(tc.TEST_COMMIT_HASH[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH], "docx")

    assert str(e.value) == c.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(
        commit_identifier=tc.TEST_COMMIT_HASH[: c.COMMIT_IDENTIFIER_DISPLAY_LENGTH]
    )


def test_repository_data_commit_identifier_to_full_path_raises_if_commit_identifier_length_invalid(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException) as e:
        rd.commit_identifier_to_full_path(tc.TEST_STRING, "docx")

    assert str(e.value) == c.INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE


def test_repository_data_commit_identifier_to_full_path_raises_if_no_matching_commit_file_found(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException) as e:
        rd.commit_identifier_to_full_path(tc.SECOND_COMMIT_HASH, "docx")

    assert str(e.value) == c.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE.format(
        file_path=tc.SECOND_COMMIT_HASH
    )


def test_repository_data_commit_identifier_to_full_path_raises_if_multiple_matching_commit_files_found(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    (
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_COMMIT_HASH + "2" + tc.DOCX_EXTENSION)
    ).write_text(
        tc.TEST_STRING,
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    )

    with pytest.raises(SCCSException) as e:
        rd.commit_identifier_to_full_path(tc.TEST_COMMIT_HASH, "docx")

    assert str(e.value) == c.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE.format(
        commit_identifier=tc.TEST_COMMIT_HASH
    )


def test_repository_data_config_data_returns_correct_config_data(initialized_repository: Path) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert rd.config_data(tc.NAME_KEY) == tc.TEST_STRING


def test_repository_data_config_data_raises_if_invalid_key(initialized_repository: Path) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        rd.config_data(tc.TEST_STRING)


def test_repository_data_current_branch_returns_correct_branch(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert rd.current_branch() == tc.MAIN_BRANCH_NAME


def test_repository_data_latest_commit_identifier_returns_correct_commit_identifier(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    target.set(tc.MAIN_BRANCH_NAME)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert rd.latest_commit_identifier() == tc.TEST_COMMIT_HASH


def test_repository_data_latest_commit_identifier_raises_if_latest_commit_identifier_is_missing(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    target.set(tc.MAIN_BRANCH_NAME)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME, "r+", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        metadata = json.load(f)
        metadata[
            tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][tc.HISTORY_KEY][tc.LATEST_COMMIT_KEY
        ] = ""

        f.seek(0)
        json.dump(metadata, f, indent=tc.JSON_INDENT)
        f.truncate()

    with pytest.raises(SCCSException):
        rd.latest_commit_identifier()


def test_repository_data_raise_for_commit_identifier_length_raises_if_invalid_length(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        rd.raise_for_commit_identifier_length(tc.TEST_STRING)
    with pytest.raises(SCCSException):
        rd.raise_for_commit_identifier_length("")


def test_repository_data_raise_for_commit_identifier_length_does_not_raise_on_valid_lengths(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    rd.raise_for_commit_identifier_length(tc.TEST_COMMIT_HASH)
    rd.raise_for_commit_identifier_length(tc.TEST_COMMIT_HASH[:10])
    

def test_repository_data_short_commit_identifier_to_full_returns_full_commit_identifier(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert (
        rd.short_commit_identifier_to_full(tc.TEST_COMMIT_HASH[:10]) == tc.TEST_COMMIT_HASH
    )


def test_repository_data_repository_objects_returns_correct_objects(
    initialized_repository: Path
) -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    expected = {tc.TEST_COMMIT_HASH}

    assert rd.repository_objects() == expected


def test_target_branch_set_sets_target_branch() -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)

    test_branch_name = tc.TEST_STRING

    target.set(test_branch_name)

    assert target._branch == test_branch_name


def test_target_branch_get_returns_target_branch() -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)

    test_branch_name = tc.TEST_STRING

    target._branch = test_branch_name

    assert target.get() == test_branch_name


def test_target_branch_reset_sets_target_branch_to_none() -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)

    target._branch = tc.TEST_STRING

    target.reset()

    assert target._branch == None


def test_target_branch_require_raises_if_target_branch_is_none() -> None:
    c = SCCSConstants()
    target = TargetBranch(c)

    with pytest.raises(SCCSException):
        target.require()


def test_target_branch_require_returns_target_branch() -> None:
    tc = SCCSTestConstants()
    c = SCCSConstants()
    target = TargetBranch(c)

    target._branch = tc.TEST_STRING

    assert target.require() == tc.TEST_STRING


def test_repository_io_read_metadata_json_reads_correct_file(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    with open(initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        expected = json.load(f)

    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert expected == ri._read_metadata_json()


def test_repository_io_write_metadata_json_writes_correct_file(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri._write_metadata_json(tc.TEST_DICTIONARY)

    with open(initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        expected = json.load(f)

    assert expected == tc.TEST_DICTIONARY


def test_repository_io_create_document_commit_creates_document(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.create_document_commit(tc.TEST_STRING)

    new_commit_path = (
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_STRING + tc.DOCX_EXTENSION)
    )

    assert new_commit_path.exists()
    assert new_commit_path.suffix == tc.DOCX_EXTENSION


def test_repository_io_create_document_commit_copies_repository_document(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.create_document_commit(tc.TEST_STRING)

    new_commit_path = (
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.TEST_STRING + tc.DOCX_EXTENSION)
    )

    assert filecmp.cmp(
        new_commit_path,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME,
        shallow=False
    )


def test_repository_io_document_html_returns_correct_html(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert tc.TEST_DOCUMENT_HTML == ri.document_html()


def test_document_html_byte_hash_returns_correct_hash(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    assert ri.document_html_byte_hash() == tc.TEST_DOCUMENT_HTML_HASH


def test_repositoryIO_file_bytes_returns_correct_bytes(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    
    with open(initialized_repository / tc.TEST_DOCUMENT_FILENAME, "rb") as f:
        expected = f.read()

    assert expected == ri.file_bytes(initialized_repository / tc.TEST_DOCUMENT_FILENAME)


def test_repository_io_mutate_updated_branches_updated_branches_using_passed_callable(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    def add(updated: list[str]) -> bool:
        updated.append(tc.TEST_STRING)
        return True

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert tc.TEST_STRING not in json.load(f)[
            tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY] 

    ri.mutate_updated_branches(add)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert tc.TEST_STRING in json.load(f)[
            tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY] 


def test_repository_io_mutate_updated_branches_initializes_missing_updated_branches(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_current_branch_data(
        {tc.CURRENT_BRANCH_KEY: tc.MAIN_BRANCH_NAME, tc.BRANCHES_KEY: [tc.MAIN_BRANCH_NAME]}
    )

    def add(updated: list[str]) -> bool:
        updated.append(tc.TEST_STRING)
        return True

    ri.mutate_updated_branches(add)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.CURRENT_BRANCH_KEY][
            tc.UPDATED_BRANCHES_KEY
        ] == [tc.TEST_STRING]


def test_repository_io_mutate_updated_branches_does_not_write_if_mutation_returns_false(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    def do_nothing(updated: list[str]) -> bool:
        return False

    metadata_path = (
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    )

    with open(metadata_path) as f:
        metadata_before = json.load(f)

    ri.mutate_updated_branches(do_nothing)

    with open(metadata_path) as f:
        assert json.load(f) == metadata_before


def test_repository_io_read_branch_data_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_branch_data()


def test_repository_io_read_branch_data_returns_target_branch_metadata(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert (
        ri.read_branch_data()
        == tc.TEST_INITIALIZATION_METADATA[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME]
    )


def test_repository_io_read_branch_data_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_branch_data()


def test_repository_io_read_branches_data_returns_branches_metadata(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert ri.read_branches_data() == tc.TEST_INITIALIZATION_METADATA[tc.BRANCHES_KEY]


def test_repository_io_read_byte_hash_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_byte_hash()


def test_repository_io_read_byte_hash_returns_target_branch_byte_hash(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert ri.read_byte_hash() == {tc.TEST_COMMIT_HASH: tc.TEST_DOCUMENT_HTML_HASH}


def test_repository_io_read_byte_hash_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_byte_hash()


def test_repository_io_read_commit_messages_returns_commit_messages(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert ri.read_commit_messages() == {
        tc.TEST_COMMIT_HASH: tc.INITIAL_COMMIT_MESSAGE
    }


def test_repository_io_read_config_returns_config(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert ri.read_config() == {tc.NAME_KEY: tc.TEST_STRING, tc.EMAIL_KEY: tc.TEST_STRING}


def test_repository_io_read_current_branch_data_returns_current_branch_data(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert (
        ri.read_current_branch_data()
        == tc.TEST_INITIALIZATION_METADATA[tc.CURRENT_BRANCH_KEY]
    )


def test_repository_io_read_current_branch_data_key_returns_key_value(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert ri.read_current_branch_data_key(tc.CURRENT_BRANCH_KEY) == tc.MAIN_BRANCH_NAME


def test_repository_io_read_history_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_history()


def test_repository_io_read_history_returns_target_branch_history(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert (
        ri.read_history()
        == tc.TEST_INITIALIZATION_METADATA[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][
            tc.HISTORY_KEY
        ]
    )


def test_repository_io_read_history_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_history()


def test_repository_io_read_log_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_log()


def test_repository_io_read_log_returns_target_branch_log(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert (
        ri.read_log()
        == tc.TEST_INITIALIZATION_METADATA[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][
            tc.LOG_KEY
        ]
    )


def test_repository_io_read_log_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.read_log()


def test_repository_io_read_metadata_returns_repository_metadata(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    assert ri.read_metadata() == tc.TEST_INITIALIZATION_METADATA


def test_repository_io_write_branch_data_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_branch_data(tc.TEST_DICTIONARY)


def test_repository_io_write_branch_data_writes_to_target_branch(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_branch_data(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME] == tc.TEST_DICTIONARY


def test_repository_io_write_branch_data_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_branch_data(tc.TEST_DICTIONARY)


def test_repository_io_write_branches_data_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_branches_data(tc.TEST_DICTIONARY)


def test_repository_io_write_branches_data_writes_branches_data(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_branches_data(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.BRANCHES_KEY] == tc.TEST_DICTIONARY


def test_repository_io_write_branches_data_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_branches_data(tc.TEST_DICTIONARY)


def test_repository_io_write_byte_hash_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_byte_hash(tc.TEST_DICTIONARY)


def test_repository_io_write_byte_hash_writes_to_target_branch(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_byte_hash(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][
            tc.BYTE_HASH_KEY
        ] == tc.TEST_DICTIONARY


def test_repository_io_write_byte_hash_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_byte_hash(tc.TEST_DICTIONARY)


def test_repository_io_write_commit_messages_writes_commit_messages(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_commit_messages(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.COMMIT_MESSAGES_KEY] == tc.TEST_DICTIONARY


def test_repository_io_write_config_writes_config(initialized_repository: Path) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_config(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.CONFIG_KEY] == tc.TEST_DICTIONARY


def test_repository_io_write_current_branch_data_writes_current_branch_data(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_current_branch_data(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.CURRENT_BRANCH_KEY] == tc.TEST_DICTIONARY


def test_repository_io_write_diff_output_writes_diff_output_file(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_diff_output(tc.TEST_STRING)

    diff_output_path = initialized_repository / c.DIFF_OUTPUT_HTML_FILE

    assert diff_output_path.exists()

    with open(diff_output_path, "r", encoding=tc.UTF_8, newline=tc.NEWLINE) as f:
        assert f.read() == tc.TEST_STRING


def test_repository_io_write_history_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_history(tc.TEST_DICTIONARY)


def test_repository_io_write_history_writes_to_target_branch(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_history(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][
            tc.HISTORY_KEY
        ] == tc.TEST_DICTIONARY


def test_repository_io_write_history_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_history(tc.TEST_DICTIONARY)


def test_repository_io_write_html_commit_writes_html_and_view_html_objects(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_html_commit(tc.TEST_COMMIT_HASH, tc.TEST_DOCUMENT_HTML)

    name = tc.TEST_COMMIT_HASH + tc.HTML_EXTENSION

    with open(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.HTML_OBJECTS_PATH_SEGMENT
        / name,
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        assert f.read() == (tc.DEFAULT_HTML_STYLES + tc.TEST_DOCUMENT_HTML)

    with open(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.VIEW_HTML_OBJECTS_PATH_SEGMENT
        / name,
        "r",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        assert f.read() == tc.HTML_BOILERPLATE_TEMPLATE.format(
            styles=tc.DEFAULT_HTML_STYLES, html=tc.TEST_DOCUMENT_HTML
        )


def test_repository_io_write_log_raises_if_target_branch_not_set(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_log(tc.TEST_DICTIONARY)


def test_repository_io_write_log_writes_to_target_branch(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_log(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][
            tc.LOG_KEY
        ] == tc.TEST_DICTIONARY


def test_repository_io_write_log_raises_if_set_branch_does_not_exist(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.TEST_STRING)
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException):
        ri.write_log(tc.TEST_DICTIONARY)


def test_repository_io_write_metadata_writes_repository_metadata(
    initialized_repository: Path,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    ri = RepositoryIO(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    ri.write_metadata(tc.TEST_DICTIONARY)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f) == tc.TEST_DICTIONARY


def test_repository_path_document_objects_path_returns_correct_path() -> None:
    tc = SCCSTestConstants()
    root = Path(tc.TEST_STRING)
    c = SCCSConstants()
    target = TargetBranch(c)

    rp = RepositoryPaths(root, tc.TEST_STRING, c)

    expected = root / tc.SCCS_PATH_SEGMENT / tc.OBJECTS_PATH_SEGMENT / tc.DOCX_OBJECTS_PATH_SEGMENT

    assert rp.document_objects_path() == expected


def test_repository_path_document_path_returns_correct_path() -> None:
    tc = SCCSTestConstants()
    root = Path(tc.TEST_STRING)
    repository_name = tc.TEST_STRING
    c = SCCSConstants()
    target = TargetBranch(c)

    rp = RepositoryPaths(root, repository_name, c)

    expected = (root / (repository_name + tc.DOCX_EXTENSION) )

    assert rp.document_path() == expected


def test_repository_path_html_objects_path_returns_correct_path() -> None:
    tc = SCCSTestConstants()
    root = Path(tc.TEST_STRING)
    repository_name = tc.TEST_STRING
    c = SCCSConstants()
    target = TargetBranch(c)

    rp = RepositoryPaths(root, repository_name, c)

    expected = root / tc.SCCS_PATH_SEGMENT / tc.OBJECTS_PATH_SEGMENT / tc.HTML_OBJECTS_PATH_SEGMENT

    assert rp.html_objects_path() == expected


def test_repository_path_metadata_path_returns_correct_path() -> None:
    tc = SCCSTestConstants()
    root = Path(tc.TEST_STRING)
    repository_name = tc.TEST_STRING
    c = SCCSConstants()
    target = TargetBranch(c)

    rp = RepositoryPaths(root, repository_name, c)

    expected = root / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME

    assert rp.metadata_path() == expected


def test_repository_path_objects_path_returns_correct_path() -> None:
    tc = SCCSTestConstants()
    root = Path(tc.TEST_STRING)
    repository_name = tc.TEST_STRING
    c = SCCSConstants()
    target = TargetBranch(c)

    rp = RepositoryPaths(root, repository_name, c)

    expected = root / tc.SCCS_PATH_SEGMENT / tc.OBJECTS_PATH_SEGMENT

    assert rp.objects_path() == expected


def test_repository_path_sccs_path_returns_correct_path() -> None:
    tc = SCCSTestConstants()
    root = Path(tc.TEST_STRING)
    repository_name = tc.TEST_STRING
    c = SCCSConstants()
    target = TargetBranch(c)

    rp = RepositoryPaths(root, repository_name, c)

    expected = root / tc.SCCS_PATH_SEGMENT

    assert rp.sccs_path() == expected


def test_repository_path_view_html_objects_path_returns_correct_path() -> None:
    tc = SCCSTestConstants()
    root = Path(tc.TEST_STRING)
    repository_name = tc.TEST_STRING
    c = SCCSConstants()
    target = TargetBranch(c)

    rp = RepositoryPaths(root, repository_name, c)

    expected = root / tc.SCCS_PATH_SEGMENT / tc.OBJECTS_PATH_SEGMENT / tc.VIEW_HTML_OBJECTS_PATH_SEGMENT

    assert rp.view_html_objects_path() == expected


def test_repository_status_branch_exists_returns_correct_bool(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    assert rs.branch_exists(tc.MAIN_BRANCH_NAME) is True
    assert rs.branch_exists(tc.TEST_STRING) is False


def test_repository_status_is_current_branch_returns_correct_bool(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    assert rs.is_current_branch(tc.MAIN_BRANCH_NAME) is True
    assert rs.is_current_branch(tc.TEST_STRING) is False


def test_repository_status_raise_for_uncommitted_changes_raises_correctly(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    rs.raise_for_uncommitted_changes()  # Should not raise

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )

    with pytest.raises(SCCSException):
        rs.raise_for_uncommitted_changes()


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
def test_repository_status_validate_repository_layout_raises_for_each_missing_resource(
    initialized_repository: Path,
    missing_resource_path_name: str,
    expected_reported_resource_path_name: str,
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    missing_resource = getattr(rs.paths, missing_resource_path_name)()
    expected_reported_resource = getattr(rs.paths, expected_reported_resource_path_name)()

    assert missing_resource.exists()

    if missing_resource.is_dir():
        shutil.rmtree(missing_resource)
    else:
        missing_resource.unlink()

    with pytest.raises(SCCSException) as e:
        rs.validate_repository_layout()

    assert str(e.value) == c.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_repository_status_validate_uncommitted_changes_returns_correct_bool(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rs = RepositoryStatus(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    assert not rs.validate_uncommitted_changes()

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )

    assert rs.validate_uncommitted_changes()


def test_repository_write_add_branch_metadata_properly_updates_metadata(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        metadata = json.load(f)
        assert tc.TEST_STRING in metadata[tc.CURRENT_BRANCH_KEY][tc.BRANCHES_KEY]
        assert all(
            i in metadata[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY]
            for i in [tc.TEST_STRING, tc.MAIN_BRANCH_NAME]
        )
        assert tc.TEST_STRING == metadata[tc.CURRENT_BRANCH_KEY][tc.CURRENT_BRANCH_KEY]
        assert (
            metadata[tc.BRANCHES_KEY][tc.TEST_STRING] == (
                metadata[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME]
            )
        )


def test_repository_write_add_to_branches_list_adds_branch_to_branches_list(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    new_branch_name = tc.TEST_STRING

    rw.add_to_branches_list(new_branch_name)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert new_branch_name in json.load(f)[tc.CURRENT_BRANCH_KEY][tc.BRANCHES_KEY]


def test_repository_write_add_to_updated_branches_adds_branch_to_updated_branches(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    new_branch_name = tc.TEST_STRING

    rw.add_to_updated_branches(new_branch_name)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert new_branch_name in json.load(f)[
            tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY
        ]


def test_repository_write_add_to_updated_branches_does_not_duplicate(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME,
        "r+",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        metadata = json.load(f)
        metadata[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY].append(
            tc.MAIN_BRANCH_NAME
        )
        f.seek(0)
        json.dump(metadata, f, indent=tc.JSON_INDENT)
        f.truncate()

    rw.add_to_updated_branches(tc.MAIN_BRANCH_NAME)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        updated_branches = json.load(f)[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY]

    assert updated_branches == [tc.MAIN_BRANCH_NAME]


def test_repository_write_commit_changes_commits_changes_and_updates_metadata(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )

    rw.commit_changes(tc.TEST_STRING)

    with open(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.HTML_OBJECTS_PATH_SEGMENT
        / (tc.SECOND_COMMIT_HASH + tc.HTML_EXTENSION), "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == (
            tc.DEFAULT_HTML_STYLES + tc.SECOND_COMMIT_TEST_DOCUMENT_HTML
        )

    with open(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.VIEW_HTML_OBJECTS_PATH_SEGMENT
        / (tc.SECOND_COMMIT_HASH + tc.HTML_EXTENSION), "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == (
            tc.HTML_BOILERPLATE_TEMPLATE.format(
                styles=tc.DEFAULT_HTML_STYLES, html=tc.SECOND_COMMIT_TEST_DOCUMENT_HTML
            )
        )

    assert filecmp.cmp(
        initialized_repository
        / tc.SCCS_PATH_SEGMENT
        / tc.OBJECTS_PATH_SEGMENT
        / tc.DOCX_OBJECTS_PATH_SEGMENT
        / (tc.SECOND_COMMIT_HASH + tc.DOCX_EXTENSION),
        initialized_repository / tc.TEST_DOCUMENT_FILENAME,
        shallow=False
    )

    with open(initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME) as f:
        assert json.load(f) == tc.SECOND_COMMIT_TEST_METADATA


def test_repository_write_commit_changes_raises_if_no_changes(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException):
        target.set(tc.MAIN_BRANCH_NAME)
        rw.commit_changes(tc.TEST_STRING)


def test_repository_write_commit_changes_raises_if_target_branch_not_set(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )

    with pytest.raises(SCCSException):
        rw.commit_changes(tc.TEST_STRING)


def test_repository_write_commit_changes_raises_if_target_branch_does_not_exist(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME,
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )

    target.set(tc.TEST_STRING)

    with pytest.raises(SCCSException):
        rw.commit_changes(tc.TEST_STRING)


def test_repository_write_commit_changes_commits_when_allow_empty_commit_is_true(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    identifier = rw.commit_changes(tc.TEST_STRING, allow_empty_commit=True)

    assert len(identifier) == 64
    assert all(i in tc.ALLOWED_HASH_CHARACTERS for i in identifier)
    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        metadata = json.load(f)
        assert metadata[
            tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][tc.HISTORY_KEY][tc.LATEST_COMMIT_KEY
        ] == identifier

        assert metadata[tc.BRANCHES_KEY][tc.MAIN_BRANCH_NAME][tc.HISTORY_KEY][tc.LATEST_COMMIT_NUMBER_KEY] == 2


def test_repository_write_commit_changes_when_updated_branches_is_missing(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME,
        "r+",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE,
    ) as f:
        metadata = json.load(f)
        del metadata[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY]
        f.seek(0)
        json.dump(metadata, f, indent=tc.JSON_INDENT)
        f.truncate()

    shutil.copy(
        Path(__file__).parent / tc.SECOND_COMMIT_TEST_DOCUMENT_FILENAME, 
        initialized_repository / tc.TEST_DOCUMENT_FILENAME
    )

    rw.commit_changes(tc.TEST_STRING)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        metadata = json.load(f)
        assert (
            tc.MAIN_BRANCH_NAME
            in metadata[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY]
        )


def test_repository_write_remove_branch_metadata_removes_branch_metadata(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    branch_to_remove = tc.MAIN_BRANCH_NAME

    rw.remove_branch_metadata(branch_to_remove, tc.MAIN_BRANCH_NAME)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        metadata = json.load(f)
        assert branch_to_remove not in metadata[tc.BRANCHES_KEY]
        assert branch_to_remove not in metadata[tc.CURRENT_BRANCH_KEY][tc.BRANCHES_KEY]
        assert branch_to_remove not in metadata[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY]
        assert metadata[tc.CURRENT_BRANCH_KEY][tc.CURRENT_BRANCH_KEY] == tc.MAIN_BRANCH_NAME


def test_repository_write_remove_branch_metadata_keeps_current_branch_when_removing_another(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    rw.add_branch_metadata(tc.TEST_STRING, tc.MAIN_BRANCH_NAME)
    rw.add_branch_metadata(tc.TEST_STRING + "2", tc.MAIN_BRANCH_NAME)

    target.set(tc.TEST_STRING + "2")

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        metadata_before = json.load(f)

    rw.remove_branch_metadata(tc.TEST_STRING, tc.TEST_STRING + "2")

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        metadata = json.load(f)
        assert tc.TEST_STRING not in metadata[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY]
        assert tc.TEST_STRING not in metadata[tc.BRANCHES_KEY]
        assert tc.TEST_STRING not in metadata[tc.CURRENT_BRANCH_KEY][tc.BRANCHES_KEY]
        assert (
            metadata[tc.CURRENT_BRANCH_KEY][tc.CURRENT_BRANCH_KEY]
            == tc.TEST_STRING + "2"
        )
        assert (
            metadata[tc.BRANCHES_KEY][tc.TEST_STRING + "2"]
            == metadata_before[tc.BRANCHES_KEY][tc.TEST_STRING + "2"]
        )
        assert metadata[tc.CURRENT_BRANCH_KEY][tc.CURRENT_BRANCH_KEY] == tc.TEST_STRING + "2"


def test_repository_write_remove_from_branches_list_removes_branch_from_branches_list(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    branch_to_remove = tc.MAIN_BRANCH_NAME

    rw.remove_from_branches_list(branch_to_remove)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert branch_to_remove not in json.load(f)[tc.CURRENT_BRANCH_KEY][tc.BRANCHES_KEY]


def test_repository_write_remove_from_branches_list_raises_if_branch_not_in_list(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    metadata_json_path = initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    metadata_before_removal = metadata_json_path.read_bytes()

    with pytest.raises(SCCSException) as e:
        rw.remove_from_branches_list(tc.TEST_STRING)

    assert str(e.value) == c.INVALID_BRANCH_DATA_ERROR_MESSAGE
    assert metadata_json_path.read_bytes() == metadata_before_removal


def test_repository_write_remove_from_updated_branch_removes_branch_from_updated_branches(
    initialized_repository: Path    
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    branch_to_remove = tc.MAIN_BRANCH_NAME

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        json_data = json.load(f)
        json_data[tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY].append(branch_to_remove)

    json.dump(json_data, open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME,
        "w",
        encoding=tc.UTF_8,
        newline=tc.NEWLINE
    ))

    rw.remove_from_updated_branch(branch_to_remove)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert branch_to_remove not in json.load(f)[
            tc.CURRENT_BRANCH_KEY][tc.UPDATED_BRANCHES_KEY
        ]


def test_repository_write_set_current_branch_sets_current_branch(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    new_current_branch = tc.TEST_STRING

    rw.set_current_branch(new_current_branch)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.CURRENT_BRANCH_KEY][tc.CURRENT_BRANCH_KEY] == new_current_branch


def test_repository_write_write_key_to_config_writes_key_value_to_config(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    rw.write_key_to_config(tc.NAME_KEY, tc.TEST_STRING)

    with open(
        initialized_repository / tc.SCCS_PATH_SEGMENT / tc.METADATA_JSON_FILENAME
    ) as f:
        assert json.load(f)[tc.CONFIG_KEY][tc.NAME_KEY] == tc.TEST_STRING


def test_repository_write_write_key_to_config_raises_if_value_is_a_space(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException):
        rw.write_key_to_config(tc.NAME_KEY, " ")


def test_repository_write_write_key_to_config_raises_if_key_is_not_valid(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException):
        rw.write_key_to_config(tc.TEST_STRING, tc.TEST_STRING)


def test_repository_write_write_key_to_config_raises_if_name_or_email_contains_invalid_characters(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants()
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException):
        rw.write_key_to_config(tc.NAME_KEY, "?")

    with pytest.raises(SCCSException):
        rw.write_key_to_config(tc.EMAIL_KEY, "?")


def test_repository_write_write_key_to_config_raises_if_remote_contains_invalid_characters(
    initialized_repository: Path
) -> None:
    c = SCCSConstants()
    target = TargetBranch(c)
    tc = SCCSTestConstants() 
    rw = RepositoryWrite(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target,
    )

    with pytest.raises(SCCSException):
        rw.write_key_to_config(tc.REMOTE_KEY, "\\")