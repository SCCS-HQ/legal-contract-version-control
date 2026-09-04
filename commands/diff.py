#!/usr/bin/env python3

import copy
import difflib
import filecmp
from pathlib import Path
import shutil

import exceptions
import utils
from bs4 import BeautifulSoup
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
    RepositoryData,
    RepositoryIO,
    RepositoryStatus,
)


def convert_html_to_soup(c: SCCSConstants, html: str | bytes) -> BeautifulSoup:

    return BeautifulSoup(html, c.HTML_PARSER)


def remove_inline_semantics(c: SCCSConstants, html: BeautifulSoup) -> BeautifulSoup:

    soup = copy.copy(html)
    for i in soup.find_all(c.TAGS_TO_UNWRAP):
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
        else:
            i.unwrap()
    return soup


def tags_to_list(soup: BeautifulSoup) -> list[str]:

    return [str(i) for i in soup.find_all()]


def number_tags(c: SCCSConstants, soup: BeautifulSoup) -> BeautifulSoup:

    for i, tag in enumerate(soup.find_all()):
        if tag.name == c.STYLE_TAG_NAME:
            continue
        tag[c.DATA_NUMBER_HTML_ATTRIBUTE] = str(i)
    return soup


def get_data_number(c: SCCSConstants, tag_list: list[str]) -> set[str]:

    data_number = set()
    for i in tag_list:
        parsed_tag = BeautifulSoup(i, c.HTML_PARSER).find()
        if parsed_tag is not None:
            if parsed_tag[c.DATA_NUMBER_HTML_ATTRIBUTE] is not None:
                data_number.add(parsed_tag[c.DATA_NUMBER_HTML_ATTRIBUTE])
    return data_number


def delete_tag(
    c: SCCSConstants, old_changed_strings: list[str], soup: BeautifulSoup
) -> BeautifulSoup:

    for i in soup.find_all():
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
            continue

        if i[c.DATA_NUMBER_HTML_ATTRIBUTE] in get_data_number(c, old_changed_strings):
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[
                    c.CLASS_HTML_ATTRIBUTE
                ].append(  # pyright: ignore [reportAttributeAccessIssue]
                    c.DELETED_HTML_ATTRIBUTE_VALUE
                )
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [  # pyright: ignore [reportArgumentType]
                    c.DELETED_HTML_ATTRIBUTE_VALUE
                ]
    return soup


def replace_tag(
    c: SCCSConstants,
    old_changed_strings: list[str],
    new_changed_strings: list[str],
    soup: BeautifulSoup,
) -> BeautifulSoup:

    html_fragment = BeautifulSoup(
        c.EMPTY_STRING.join(new_changed_strings), c.HTML_PARSER
    )
    match = []
    for i in soup.find_all():
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
            continue
        if i[c.DATA_NUMBER_HTML_ATTRIBUTE] in get_data_number(c, old_changed_strings):
            match.append(i)

    for i in html_fragment.find_all():
        if i.name:
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[
                    c.CLASS_HTML_ATTRIBUTE
                ].append(  # pyright: ignore [reportAttributeAccessIssue]
                    c.INSERTED_HTML_ATTRIBUTE_VALUE
                )
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [  # pyright: ignore [reportArgumentType]
                    c.INSERTED_HTML_ATTRIBUTE_VALUE
                ]
    if match:
        match[-1].insert_after(html_fragment)
        for i in match:
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[c.CLASS_HTML_ATTRIBUTE].append(c.DELETED_HTML_ATTRIBUTE_VALUE)
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [c.DELETED_HTML_ATTRIBUTE_VALUE]
    return soup


def insert_tag(
    c: SCCSConstants,
    new_changed_strings: list[str],
    insert_index: int,
    soup: BeautifulSoup,
) -> BeautifulSoup:

    for i in soup.find_all():
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
            continue
    tags = soup.find_all()
    html_fragment = BeautifulSoup(
        c.EMPTY_STRING.join(new_changed_strings), c.HTML_PARSER
    )
    for i in html_fragment.find_all():
        if i.name:
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[
                    c.CLASS_HTML_ATTRIBUTE
                ].append(  # pyright: ignore [reportAttributeAccessIssue]
                    c.INSERTED_HTML_ATTRIBUTE_VALUE
                )
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [  # pyright: ignore [reportArgumentType]
                    c.INSERTED_HTML_ATTRIBUTE_VALUE
                ]

    (
        tags[insert_index].insert_before(html_fragment)
        if insert_index < len(tags)
        else soup.append(html_fragment)
    )

    return soup


def format_redline_html(
    c: SCCSConstants,
    past_version: list[str],
    current_version: list[str],
    commit_identifier_list: list[str],
    document_current_version_list: list[str],
    soup: BeautifulSoup,
) -> BeautifulSoup:

    opcodes = difflib.SequenceMatcher(None, past_version, current_version).get_opcodes()

    redline = soup
    for i in reversed(opcodes):
        tag, i1, i2, j1, j2 = i
        old_changed_strings = commit_identifier_list[i1:i2]
        new_changed_strings = document_current_version_list[j1:j2]
        if tag == c.REPLACE_OPCODE:

            redline = replace_tag(c, old_changed_strings, new_changed_strings, soup)
        if tag == c.INSERT_OPCODE:

            redline = insert_tag(c, new_changed_strings, i1, soup)
        if tag == c.DELETE_OPCODE:

            redline = delete_tag(c, old_changed_strings, soup)
    return redline


def strip_number_attribute(c: SCCSConstants, soup: BeautifulSoup) -> BeautifulSoup:

    for i in soup.find_all():
        if c.DATA_NUMBER_HTML_ATTRIBUTE in i.attrs:
            del i[c.DATA_NUMBER_HTML_ATTRIBUTE]
    return soup


def generate_diff_output(
    c: SCCSConstants, commit_identifier: str, rd: RepositoryData, ri: RepositoryIO
) -> BeautifulSoup:

    commit_soup = convert_html_to_soup(
        c, rd.commit_file_bytes(commit_identifier, c.HTML_DIRECTORY)
    )

    current_version_soup = convert_html_to_soup(c, ri.document_html())

    past_version = tags_to_list(remove_inline_semantics(c, commit_soup))

    current_version = tags_to_list(remove_inline_semantics(c, current_version_soup))

    commit_identifier_list = tags_to_list(
        remove_inline_semantics(c, number_tags(c, commit_soup))
    )

    document_current_version_list = tags_to_list(
        remove_inline_semantics(c, number_tags(c, current_version_soup))
    )

    commit_soup = remove_inline_semantics(c, number_tags(c, commit_soup))

    return format_redline_html(
        c,
        past_version,
        current_version,
        commit_identifier_list,
        document_current_version_list,
        commit_soup,
    )


def validate_diff(c: SCCSConstants, rd: RepositoryData, commit_identifier: str) -> None:

    commit_path = rd.commit_identifier_to_full_path(
        commit_identifier, c.DOCUMENT_DIRECTORY
    )

    if filecmp.cmp(commit_path, rd.paths.document_path()):
        raise exceptions.SCCSException(c.DIFF_ERROR_MESSAGE)


def print_diff_success_message(c: SCCSConstants) -> None:

    print(c.DIFF_SUCCESS_MESSAGE)


def main(
    c: SCCSConstants,
    commit_identifier: str,
    rd: RepositoryData,
    ri: RepositoryIO,
    rs: RepositoryStatus,

) -> None:
    rs.target.set(rd.current_branch())
    rs.validate_repository_layout()
    rs.raise_for_uncommitted_changes()

    validate_diff(c, rd, commit_identifier)

    full_commit_identifier = rd.short_commit_identifier_to_full(commit_identifier)

    staging_root = utils.create_staging_directory(c, ri.root)

    try:
        
        staging_ri = RepositoryIO(staging_root, c, ri.target)

        staging_ri.write_diff_output(
            utils.wrap_html(
                c,
                str(
                    strip_number_attribute(
                        c, generate_diff_output(c, full_commit_identifier, rd, ri)
                    )
                ),
                c.DEFAULT_HTML_STYLES,
            )
        )
        utils.promote_staging(c, staging_root, ri.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_diff_success_message(c)
    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryIO(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
    )
