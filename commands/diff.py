#!/usr/bin/env python3
"""Create and display HTML diffs between commits."""

import copy
import difflib
from pathlib import Path

import utils
from bs4 import BeautifulSoup
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryIO,
    RepositoryData,
    RepositoryStatus,
    TargetBranch,
)


def number_tags(c: SCCSConstants, soup: BeautifulSoup) -> BeautifulSoup:
    """
    Add a data-number attribute to all tags in the  HTML, excluding style tags, with a
    unique index value by enumerating through the tags and giving each a data-number
    attribute corresponding to its index in the enumeration.

    Return the modified BeautifulSoup object with numbered tags.
    """
    
    for index, tag in enumerate(soup.find_all()):
        if tag.name == c.STYLE_TAG_NAME:
            continue
        tag[c.DATA_NUMBER_HTML_ATTRIBUTE] = str(index)
    return soup


def strip_number_attribute(
        c: SCCSConstants,
        soup: BeautifulSoup
    ) -> BeautifulSoup:
    """
    Use BeautifulSoup.findall() to return a list of all tags in the HTML, and remove the
    data-number attribute from each tag if it exists.

    Return the modified BeautifulSoup object with data-number attributes removed from
    all tags.
    """

    for i in soup.find_all():
        if c.DATA_NUMBER_HTML_ATTRIBUTE in i.attrs:
            del i[c.DATA_NUMBER_HTML_ATTRIBUTE]
    return soup


def tags_to_list(soup: BeautifulSoup) -> list[str]:
    """
    Use BeautifulSoup.findall() to return a list of all tags in the HTML, and convert
    each tag to a string.

    Return a list of strings representing each tag in the HTML.
    """

    return [str(i) for i in soup.find_all()]


def get_data_number(c: SCCSConstants, tag_list: list[str]) -> set[str]:
    """
    Convert a list of tag strings to a set of data-number attribute values by parsing
    each tag to search for the 'data-number' attribute.

    Return a set of data-number attribute values found in the list of tag strings.
    """

    data_number = set()
    for i in tag_list:
        parsed_tag = (BeautifulSoup(i, c.HTML_PARSER).find())
        if parsed_tag is not None:
            if parsed_tag[c.DATA_NUMBER_HTML_ATTRIBUTE] is not None:
                data_number.add(parsed_tag[c.DATA_NUMBER_HTML_ATTRIBUTE])
    return data_number


def delete_tag(c: SCCSConstants, old_changed_strings: list[str], soup: BeautifulSoup) -> BeautifulSoup:
    """
    Add a "deleted" class to all tags in the list of modified strings that have a
    data-number attribute.

    Decompose all 'style' tags in the HTML

    Return the modified BeautifulSoup object with "deleted" class added to tags.
    """

    for i in soup.find_all():
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
            continue

        if i[c.DATA_NUMBER_HTML_ATTRIBUTE] in get_data_number(c, old_changed_strings):
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[c.CLASS_HTML_ATTRIBUTE].append(c.DELETED_HTML_ATTRIBUTE_VALUE)
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [c.DELETED_HTML_ATTRIBUTE_VALUE]
    return soup


def replace_tag(
    c: SCCSConstants, old_changed_strings: list[str], new_changed_strings: list[str], soup: BeautifulSoup
) -> BeautifulSoup:
    """
    Replace tags matching old_changed_strings with new_changed_strings in the entered
    HTML.

    Decompose all 'style' tags in the HTML

    Return the modified BeautifulSoup object with 'deleted' class added to old tags and
    'inserted' class added to new tags.
    """

    frag = BeautifulSoup(c.EMPTY_STRING.join(new_changed_strings), c.HTML_PARSER)
    match = []
    for i in soup.find_all():
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
            continue
        if i[c.DATA_NUMBER_HTML_ATTRIBUTE] in get_data_number(c, old_changed_strings):
            match.append(i)

    for i in frag.find_all():
        if i.name:
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[c.CLASS_HTML_ATTRIBUTE].append(c.INSERTED_HTML_ATTRIBUTE_VALUE)
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [c.INSERTED_HTML_ATTRIBUTE_VALUE]
    if match:
        match[-1].insert_after(frag)
        for i in match:
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[c.CLASS_HTML_ATTRIBUTE].append(c.DELETED_HTML_ATTRIBUTE_VALUE)
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [c.DELETED_HTML_ATTRIBUTE_VALUE]
    return soup


def insert_tag(c: SCCSConstants, new_changed_strings: list[str], i1: int, soup: BeautifulSoup) -> BeautifulSoup:
    """
    Insert new tags matching new_changed_strings into the entered HTML at the position
    corresponding to i1.

    Decompose all 'style' tags in the HTML.

    Return the modified BeautifulSoup object with 'inserted' class added to new tags.
    """

    for i in soup.find_all():
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
            continue
    tags = soup.find_all()
    frag = BeautifulSoup(c.EMPTY_STRING.join(new_changed_strings), c.HTML_PARSER)
    for i in frag.find_all():
        if i.name:
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[c.CLASS_HTML_ATTRIBUTE].append(c.INSERTED_HTML_ATTRIBUTE_VALUE)
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [c.INSERTED_HTML_ATTRIBUTE_VALUE]
    if i1 < len(tags):
        tags[i1].insert_before(frag)
    else:
        soup.append(frag)
    return soup


def remove_inline_semantics(c: SCCSConstants, html: BeautifulSoup) -> BeautifulSoup:
    """
    Remove inline semantics tags from the HTML by using BeautifulSoup.findall() to find
    all tags in the HTML, and unwrapping any tags that match the list of inline
    semantics tags, while decomposing any 'style' tags.

    Remove tags block level tags that cause nested tags. Not ignoring these types of
    tags creates duplicated content in the diff.

    Remove the following tags: b, i, u, strong, em, style, table, tr, td, ol, ul.

    Return the modified BeautifulSoup object with inline semantics tags removed.
    """

    soup = copy.copy(html)
    for i in soup.find_all(
        c.TAGS_TO_UNWRAP
    ):
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
        else:
            i.unwrap()
    return soup


def convert_html_to_soup(c: SCCSConstants, html: str | bytes) -> BeautifulSoup:
    """
    Parse the entered HTML string into a BeautifulSoup object.

    Return the BeautifulSoup object representing the parsed HTML.
    """

    return BeautifulSoup(html, c.HTML_PARSER)


def format_redline_html(
        c: SCCSConstants,
        past_version: list[str],
        current_version: list[str],
        commit_list: list[str],
        docx_current_version_list: list[str],
        soup: BeautifulSoup
    ) -> BeautifulSoup:
    """
    Use the list of opcodes provided to modify the base redline HTML. 'opcodes' is a
    list of 5-tuples.

    The first value in the 5-tuple is the type of difference. Depending on
    the type of difference, perform a different function:

    replace: replace_tag()

    insert: insert_tag()

    delete: delete_tag()

    Return a modified version of 'redline' using the opcodes to determine the type of
    difference and perform a subsequent function.
    """

    opcodes = difflib.SequenceMatcher(None, past_version, current_version).get_opcodes()

    redline = soup
    for i in reversed(opcodes):
        tag, i1, i2, j1, j2 = i
        old_changed_strings = commit_list[i1:i2]
        new_changed_strings = docx_current_version_list[j1:j2]
        if tag == c.REPLACE_OPCODE:

            redline = replace_tag(c, old_changed_strings, new_changed_strings, soup)
        if tag == c.INSERT_OPCODE:

            redline = insert_tag(c, new_changed_strings, i1, soup)
        if tag == c.DELETE_OPCODE:

            redline = delete_tag(c, old_changed_strings, soup)
    return redline


def print_diff_success_message(c: SCCSConstants):
    print(c.DIFF_SUCCESS_MESSAGE)


def generate_diff_output(c: SCCSConstants, commit_hash: str, ri: RepositoryIO, rd: RepositoryData):
    commit_soup = convert_html_to_soup(c, rd.commit_file_bytes(commit_hash, c.HTML_DIR))

    current_version_soup = convert_html_to_soup(c, ri.document_html())

    past_version = tags_to_list(remove_inline_semantics(c, commit_soup))

    current_version = tags_to_list(remove_inline_semantics(c, current_version_soup))

    commit_list = tags_to_list(remove_inline_semantics(c, number_tags(c, commit_soup)))

    docx_current_version_list = tags_to_list(remove_inline_semantics(c, number_tags(c, current_version_soup)))

    commit_soup = number_tags(c, remove_inline_semantics(c, commit_soup))

    return format_redline_html(c, past_version, current_version, commit_list, docx_current_version_list, commit_soup)


def main(
        c: SCCSConstants,
        commit_hash: str,
        rd: RepositoryData,
        rs: RepositoryStatus,
        ri: RepositoryIO
    ) -> None:
    """Run functions for the <sccs diff> command."""
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    rs.raise_for_uncommitted_changes()
    

    ri.write_diff_output(
        utils.wrap_html(
            c,
            str(strip_number_attribute(c, generate_diff_output(c, commit_hash, ri, rd))),
            c.DEFAULT_HTML_STYLES
        ),
    )

    print_diff_success_message(c)

    rs.target.reset()

if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryIO(Path.cwd(), c, target),
    )
