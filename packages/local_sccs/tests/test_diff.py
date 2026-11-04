from local_sccs.repository_layout import TargetBranch
from test_constants import SCCSTestConstants
from local_sccs import diff
from local_sccs.constants_classes import SCCSConstants
import pytest
from pathlib import Path
from local_sccs.repository_layout import RepositoryData, RepositoryIO, RepositoryStatus, RepositoryWrite
from local_sccs.exceptions import SCCSException
import shutil
from typing import NoReturn
import os
import tempfile
from types import FunctionType

from bs4 import BeautifulSoup


@pytest.mark.parametrize(
    "html, expected_value",
    [
         (
            SCCSTestConstants.TEST_DIFF_HTML_1,
            [
                "<html><body><p>Hello <strong>bold</strong>, <em>italic</em>, and <u>underlined</u> text.</p></body></html>",
                "<body><p>Hello <strong>bold</strong>, <em>italic</em>, and <u>underlined</u> text.</p></body>",
                "<p>Hello <strong>bold</strong>, <em>italic</em>, and <u>underlined</u> text.</p>",
                "<strong>bold</strong>",
                "<em>italic</em>",
                 "<u>underlined</u>"
             ],
         ),
         (
             SCCSTestConstants.TEST_DIFF_HTML_2,
             [
                 "<html><body><h2>Testing <b>bold</b> and <i>italic</i> with <u>underline</u>.</h2></body></html>",
                 "<body><h2>Testing <b>bold</b> and <i>italic</i> with <u>underline</u>.</h2></body>",
                 "<h2>Testing <b>bold</b> and <i>italic</i> with <u>underline</u>.</h2>",
                 "<b>bold</b>",
                 "<i>italic</i>",
                 "<u>underline</u>"
             ],
         ),
     ]
)
def test_tags_to_list_converts_bs4_object_to_list_of_tags(
    tc: SCCSTestConstants, html: str, expected_value: list
) -> None:
    assert (
        diff.tags_to_list(BeautifulSoup(html, tc.HTML_PARSER))
        == expected_value
    )


@pytest.mark.parametrize(
    "html, expected_value",
    [
         (
             SCCSTestConstants.TEST_DIFF_HTML_1,
             "<html><body><p>Hello bold, italic, and underlined text.</p></body></html>",
         ),
         (
             SCCSTestConstants.TEST_DIFF_HTML_2,
             "<html><body><h2>Testing bold and italic with underline.</h2></body></html>",
         )
     ],
)
def test_remove_inline_semantics_removes_or_decomposes_tags(
    c: SCCSConstants, tc: SCCSTestConstants, html: str, expected_value: str
) -> None:
    assert (
        diff.remove_inline_semantics(c, BeautifulSoup(html, tc.HTML_PARSER))
        == BeautifulSoup(expected_value, tc.HTML_PARSER)
    )


@pytest.mark.parametrize(
    "html, expected_value",
    [
         (
             SCCSTestConstants.TEST_DIFF_HTML_1,
             SCCSTestConstants.TEST_DIFF_HTML_1_WITH_DATA_NUMBER
         ),
         (
             SCCSTestConstants.TEST_DIFF_HTML_2,
             SCCSTestConstants.TEST_DIFF_HTML_2_WITH_DATA_NUMBER
         )
     ],
)
def test_number_tags_numbers_tags_correctly(
    c: SCCSConstants, tc: SCCSTestConstants, html: str, expected_value: str
) -> None:
    assert (
       diff.number_tags(c, BeautifulSoup(html, tc.HTML_PARSER))
        == BeautifulSoup(expected_value, tc.HTML_PARSER)
    )


@pytest.mark.parametrize(
    "html, expected_value",
    [
         (
             SCCSTestConstants.TEST_DIFF_HTML_1_WITH_DATA_NUMBER,
             SCCSTestConstants.TEST_DIFF_HTML_1
         ),
         (
             SCCSTestConstants.TEST_DIFF_HTML_2_WITH_DATA_NUMBER,
             SCCSTestConstants.TEST_DIFF_HTML_2
         )
     ],
)
def test_strip_number_attribute_removes_all_data_number_attributes(
    c: SCCSConstants, tc: SCCSTestConstants, html: str, expected_value: str
) -> None:
    assert (
        diff.strip_number_attribute(c, BeautifulSoup(html, tc.HTML_PARSER))
        == BeautifulSoup(expected_value, tc.HTML_PARSER)
    )


def test_print_diff_success_message(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    diff.print_diff_success_message(c)

    assert capsys.readouterr().out == tc.DIFF_SUCCESS_MESSAGE


def test_validate_diff_raises_if_commit_is_latest(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants
) -> None:
    rd = RepositoryData(
        initialized_repository, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        diff.validate_diff(c, rd, tc.TEST_COMMIT_HASH)
    assert str(e.value) == tc.FAILED_TO_GENERATE_DIFF_OUTPUT_MESSAGE


@pytest.mark.parametrize(
    "html, old_changed_strings, expected_value",
    [
        (
            SCCSTestConstants.TEST_DIFF_HTML_1_WITH_DATA_NUMBER,
            [
                '<strong data-number="3">bold</strong>',
                '<em data-number="4">'
            ],
             '<html data-number="0"><body data-number="1"><p data-number="2">Hello <strong class="deleted" data-number="3">bold</strong>, <em class="deleted" data-number="4">italic</em>, and <u data-number="5">underlined</u> text.</p></body></html>'
        ),
        (
            SCCSTestConstants.TEST_DIFF_HTML_2_WITH_DATA_NUMBER,
            [
                '<b data-number="3">bold</b>',
                '<i data-number="4">'
            ],
            '<html data-number="0"><body data-number="1"><h2 data-number="2">Testing <b class="deleted" data-number="3">bold</b> and <i class="deleted" data-number="4">italic</i> with <u data-number="5">underline</u>.</h2></body></html>'
        ),
        (
            "<html data-number='0'><body data-number='1'><style data-number='2'>x</style><p class='foo' data-number='3'>Hello</p></body></html>",
            ["<p data-number='3'>Hello</p>"],
            "<html data-number='0'><body data-number='1'><p class='foo deleted' data-number='3'>Hello</p></body></html>"
        )
     ],
)
def test_delete_tag_adds_deleted_class_and_deletes_style_tags(
    c: SCCSConstants, tc: SCCSTestConstants, html: str, old_changed_strings: list[str], expected_value: str
) -> None:

    assert (
        diff.delete_tag(c, old_changed_strings, BeautifulSoup(html, tc.HTML_PARSER))
        == BeautifulSoup(expected_value, tc.HTML_PARSER)
    )


@pytest.mark.parametrize(
    "html, new_changed_strings, insert_index, expected_value",
    [
        (
            SCCSTestConstants.TEST_DIFF_HTML_1_WITH_DATA_NUMBER,
            [
                "<div>this is a div</div>",
                "<p>this is a p</p>"
            ],
            2,
             '<html data-number="0"><body data-number="1"><div class="inserted">this is a div</div><p class="inserted">this is a p</p><p data-number="2">Hello <strong data-number="3">bold</strong>, <em data-number="4">italic</em>, and <u data-number="5">underlined</u> text.</p></body></html>'
        ),
        (
            SCCSTestConstants.TEST_DIFF_HTML_2_WITH_DATA_NUMBER,
            [
                "<div>this is a div</div>",
                "<p>this is a p</p>"
            ],
            2,
            '<html data-number="0"><body data-number="1"><div class="inserted">this is a div</div><p class="inserted">this is a p</p><h2 data-number="2">Testing <b data-number="3">bold</b> and <i data-number="4">italic</i> with <u data-number="5">underline</u>.</h2></body></html>'
        ),
        (
            "<html data-number='0'><body data-number='1'><style data-number='2'>x</style><p data-number='3'>Hello</p></body></html>",
            ["<p class='bar'>new</p>"],
            2,
            "<html data-number='0'><body data-number='1'><p class='bar inserted'>new</p><p data-number='3'>Hello</p></body></html>",
        )
    ]
)
def test_insert_tag_inserts_tags_correctly(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    html: str,
    new_changed_strings: list[str],
    insert_index: int,
    expected_value: str
) -> None:

    assert (
        diff.insert_tag(
            c,
            new_changed_strings,
            insert_index,
            BeautifulSoup(html, tc.HTML_PARSER)
        )
        == BeautifulSoup(expected_value, tc.HTML_PARSER)
    )


@pytest.mark.parametrize(
    "html, old_changed_strings, new_changed_strings, expected_value",
    [
        (
            SCCSTestConstants.TEST_DIFF_HTML_1_WITH_DATA_NUMBER,
            [
                '<strong data-number="3">bold</strong>',
                '<em data-number="4">'
            ],
            [
                "<div>this is a div</div>",
                "<p>this is a p</p>"
            ],
             '<html data-number="0"><body data-number="1"><p data-number="2">Hello <strong data-number="3" class="deleted">bold</strong>, <em data-number="4" class="deleted">italic</em><div class="inserted">this is a div</div><p class="inserted">this is a p</p>, and <u data-number="5">underlined</u> text.</p></body></html>'
        ),
        (
            SCCSTestConstants.TEST_DIFF_HTML_2_WITH_DATA_NUMBER,
            [
                '<b data-number="3">bold</b>',
                '<i data-number="4">'
            ],
            [
                "<div>this is a div</div>",
                "<p>this is a p</p>"
            ],
            '<html data-number="0"><body data-number="1"><h2 data-number="2">Testing <b class="deleted" data-number="3">bold</b> and <i class="deleted" data-number="4">italic</i><div class="inserted">this is a div</div><p class="inserted">this is a p</p> with <u data-number="5">underline</u>.</h2></body></html>'
        ),
        (
            "<html data-number='0'><body data-number='1'><style data-number='2'>x</style><p class='foo' data-number='3'>Hello</p></body></html>",
            ["<p data-number='3'>Hello</p>"],
            ["<p class='bar'>new</p>"],
            "<html data-number='0'><body data-number='1'><p class='foo deleted' data-number='3'>Hello</p><p class='bar inserted'>new</p></body></html>",
        )
    ]
)
def test_replace_tag_adds_correct_tags_and_classes(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    html: str,
    old_changed_strings: list[str],
    new_changed_strings: list[str],
    expected_value: str
) -> None:

    assert (
        diff.replace_tag(
            c,
            old_changed_strings,
            new_changed_strings,
            BeautifulSoup(html, tc.HTML_PARSER)
        )
        == BeautifulSoup(expected_value, tc.HTML_PARSER)
    )


@pytest.mark.parametrize(
    "tag_list, expected_value",
    [
        (
            ['<html data-number="0"><body data-number="1"><p data-number="2">Hello <strong data-number="3">bold</strong>, <em data-number="4">italic</em>, and <u data-number="5">underlined</u> text.</p></body></html>', '<body data-number="1"><p data-number="2">Hello <strong data-number="3">bold</strong>, <em data-number="4">italic</em>, and <u data-number="5">underlined</u> text.</p></body>', '<p data-number="2">Hello <strong data-number="3">bold</strong>, <em data-number="4">italic</em>, and <u data-number="5">underlined</u> text.</p>', '<strong data-number="3">bold</strong>', '<em data-number="4">italic</em>', '<u data-number="5">underlined</u>'],
            {'0', '1', '2', '3', '5', '4'}
        ),
        (
            ['<html data-number="0"><body data-number="1"><h2 data-number="2">Testing <b data-number="3">bold</b> and <i data-number="4">italic</i> with <u data-number="5">underline</u>.</h2></body></html>', '<body data-number="1"><h2 data-number="2">Testing <b data-number="3">bold</b> and <i data-number="4">italic</i> with <u data-number="5">underline</u>.</h2></body>', '<h2 data-number="2">Testing <b data-number="3">bold</b> and <i data-number="4">italic</i> with <u data-number="5">underline</u>.</h2>', '<b data-number="3">bold</b>', '<i data-number="4">italic</i>', '<u data-number="5">underline</u>'],
            {'4', '2', '3', '0', '5', '1'}
        )
    ]
)
def test_get_data_number_returns_set_of_data_numbers(
    c: SCCSConstants, tag_list: list[str], expected_value: set[str]
) -> None:
    assert diff.get_data_number(c, tag_list) == expected_value


@pytest.mark.parametrize(
    "past_version, current_version, commit_identifier_list, document_current_version_list, html, expected_value",
    [
        (
            ['<p>First bold paragraph.</p>', '<h2>Second italic heading.</h2>', '<li>Third underlined item.</li>'],
            ['<h2>Second italic heading. Updated</h2>', '<li>Third underlined item.</li>', '<p>Fourth</p>'],
            ['<p data-number="0">First bold paragraph.</p>', '<h2 data-number="2">Second italic heading.</h2>', '<li data-number="5">Third underlined item.</li>'],
            ['<h2 data-number="0">Second italic heading. Updated</h2>', '<li data-number="3">Third underlined item.</li>', '<p data-number="5">Fourth</p>'],
            '<p data-number="0">First bold paragraph.</p><h2 data-number="2">Second italic heading.</h2><li data-number="5">Third underlined item.</li>',
            '<p class="deleted" data-number="0">First bold paragraph.</p><h2 class="deleted" data-number="2">Second italic heading.</h2><h2 class="inserted" data-number="0">Second italic heading. Updated</h2><li data-number="5">Third underlined item.</li><p class="inserted" data-number="5">Fourth</p>'
        ),
        (
            ['<h1>Project Overview</h1>', '<p>Review the first draft before adding new details.</p>', '<li>Check the formatting.</li>'],
            ['<h1>Project Overview</h1>', '<li>Check the formatting. Edited</li>', '<p>4th</p>'],
            ['<h1 data-number="0">Project Overview</h1>', '<p data-number="1">Review the first draft before adding new details.</p>', '<li data-number="5">Check the formatting.</li>'],
            ['<h1 data-number="0">Project Overview</h1>', '<li data-number="2">Check the formatting. Edited</li>', '<p data-number="4">4th</p>'],
            '<h1 data-number="0">Project Overview</h1><p data-number="1">Review the first draft before adding new details.</p><li data-number="5">Check the formatting.</li>',
            '<h1 data-number="0">Project Overview</h1><p class="deleted" data-number="1">Review the first draft before adding new details.</p><li class="deleted" data-number="5">Check the formatting.</li><li class="inserted" data-number="2">Check the formatting. Edited</li><p class="inserted" data-number="4">4th</p>'
        ),
        (
            ["<p>a</p>", "<p>b</p>"],
            ["<p>a</p>"],
            ["<p data-number='0'>a</p>", "<p data-number='1'>b</p>"],
            ["<p data-number='0'>a</p>"],
            '<p data-number="0">a</p><p data-number="1">b</p>',
            '<p data-number="0">a</p><p class="deleted" data-number="1">b</p>',
        )
    ]
)
def test_format_redline_html_formats_correctly(
    c: SCCSConstants,
    tc: SCCSTestConstants,
    past_version: list[str],
    current_version: list[str],
    commit_identifier_list: list[str],
    document_current_version_list: list[str],
    html: str,
    expected_value: str
) -> None:
    assert (
        diff.format_redline_html(
            c,
            past_version,
            current_version,
            commit_identifier_list,
            document_current_version_list,
            BeautifulSoup(html, tc.HTML_PARSER)
        )
        == BeautifulSoup(expected_value, tc.HTML_PARSER)
    )


def test_generate_diff_output_generates_correct_diff(
    repository_with_multiple_commits: Path, c: SCCSConstants, target: TargetBranch, tc: SCCSTestConstants
) -> None:

    rd = RepositoryData(repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    ri = RepositoryIO(repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target)
    
    assert BeautifulSoup(
        str(diff.generate_diff_output(c, tc.TEST_COMMIT_HASH, rd, ri)).strip(),
        tc.HTML_PARSER,
    ) == BeautifulSoup(
        tc.TEST_REPOSITORY_DIFF_HTML.strip(),
        tc.HTML_PARSER,
    )


@pytest.mark.parametrize(
    ("missing_resource_path_name", "expected_reported_resource_path_name"),
    [
        ("view_html_objects_path", "view_html_objects_path"),
        ("html_objects_path", "html_objects_path"),
        ("sccs_path", "sccs_path"),
        ("document_objects_path", "document_objects_path"),
        ("document_path", "document_path"),
        ("metadata_path", "metadata_path"),
        ("objects_path", "objects_path")
    ],
)
def test_diff_main_raises_for_each_missing_resource(
    initialized_repository: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
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
        diff.main(c, tc.TEST_STRING, rd, ri ,rs)

    assert str(e.value) == tc.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE.format(
        resource_name=expected_reported_resource
    )


def test_diff_main_raises_if_uncommitted_changes_exist(    
    repository_with_modified_document: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
) -> None:
    rd = RepositoryData(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_modified_document, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    with pytest.raises(SCCSException) as e:
        diff.main(c, tc.TEST_COMMIT_HASH, rd, ri, rs)
    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE


def test_diff_main_prints_success_message(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    capsys: pytest.CaptureFixture[str]
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw.commit_changes(tc.TEST_STRING)

    diff.main(c, tc.TEST_COMMIT_HASH, rd, ri, rs)

    assert capsys.readouterr().out == tc.DIFF_SUCCESS_MESSAGE

@pytest.mark.parametrize(
    "module, function",
    [(tempfile, "mkdtemp"), (shutil, "copytree"), (os, "rename")]
)
def test_diff_main_staged_repository_creation_fails(
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
    ri = RepositoryIO(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    monkeypatch.setattr(module, function, raise_exception)

    with pytest.raises(SCCSException) as e:
        diff.main(c, tc.TEST_STRING, rd, ri, rs)
    assert str(e.value) == tc.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE

    staging_dirs = list(
        repository_with_multiple_commits.parent.glob(
            tc.TEMPORARY_DIRECTORY_PREFIX + tc.RGLOB_ALL_FILES_PATTERN
        )
    )
    
    assert not staging_dirs


def test_diff_main_generic_exception_resets_target(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw.commit_changes(tc.TEST_STRING)

    monkeypatch.setattr(diff, "generate_diff_output", raise_exception)

    with pytest.raises(SCCSException) as e:
        diff.main(c, tc.TEST_COMMIT_HASH, rd, ri, rs)
    assert str(e.value) == tc.STAGED_REPOSITORY_ERROR_MESSAGE

    assert target.get() == tc.MAIN_BRANCH_NAME or True


def test_diff_main_create_proper_diff_output(
    repository_with_multiple_commits: Path,
    c: SCCSConstants,
    target: TargetBranch,
    tc: SCCSTestConstants
) -> None:
    rd = RepositoryData(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    ri = RepositoryIO(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rs = RepositoryStatus(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )

    target.set(tc.MAIN_BRANCH_NAME)
    rw = RepositoryWrite(
        repository_with_multiple_commits, tc.TEST_DOCUMENT_REPOSITORY_NAME, c, target
    )
    rw.commit_changes(tc.TEST_STRING)

    diff.main(c, tc.TEST_COMMIT_HASH, rd, ri, rs)

    with open(
        repository_with_multiple_commits / tc.DIFF_HTML_FILE, "r", encoding=tc.UTF_8, newline=tc.NEWLINE
    ) as f:
        assert f.read() == tc.TEST_DIFF_OUTPUT


def test_diff_main_resets_target_on_error(
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

    with pytest.raises(SCCSException):
        diff.main(c, tc.TEST_COMMIT_HASH, rd, ri, rs)

    assert target.get() is None