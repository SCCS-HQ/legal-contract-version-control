#!/usr/bin/env python3
"""Create and display HTML diffs between commits."""

import copy
import difflib
import sys
from pathlib import Path

import exceptions
import utils
from bs4 import BeautifulSoup
from repository_layout import RepositoryLayout

Repository = RepositoryLayout(Path.cwd())


def get_commit_html() -> str:
    """
    Open the commit HTML file at the specified path and return its contents as a string.

    Return the commit HTML as a string if the file is successfully opened, otherwise
    raise as exception.
    """

    try:
        with open(
            Repository.commit_path("html", Path.cwd(), utils.entered_arguement(2)
        ), "r", encoding="utf-8", newline="\n") as f:
            commit_html = f.read()

    except Exception as e:
        raise exceptions.FileOpenError from e
    return commit_html


def number_tags(html: BeautifulSoup) -> BeautifulSoup:
    """
    Add a data-number attribute to all tags in the HTML, excluding style tags, with a
    unique index value by enumerating through the tags and giving each a data-number
    attribute corresponding to its index in the enumeration.

    Return the modified BeautifulSoup object with numbered tags.
    """

    soup = remove_inline_semantics(html)
    
    for i in enumerate(soup.find_all()):
        if i[1].name == "style":
            continue
        i[1]["data-number"] = str(i[0])
    return soup


def strip_number_attribute(html: BeautifulSoup) -> BeautifulSoup:
    """
    Use BeautifulSoup.findall() to return a list of all tags in the HTML, and remove the
    data-number attribute from each tag if it exists.

    Return the modified BeautifulSoup object with data-number attributes removed from
    all tags.
    """

    soup = html
    for i in soup.find_all():
        if "data-number" in i.attrs:
            del i["data-number"]
    return soup


def tags_to_list(html: BeautifulSoup) -> list[str]:
    """
    Use BeautifulSoup.findall() to return a list of all tags in the HTML, and convert
    each tag to a string.

    Return a list of strings representing each tag in the HTML.
    """

    soup = remove_inline_semantics(html)
    return [str(i) for i in soup.find_all()]


def get_data_number(tag_list: list[str]) -> set[str]:
    """
    Convert a list of tag strings to a set of data-number attribute values by parsing
    each tag to search for the 'data-number' attribute.

    Return a set of data-number attribute values found in the list of tag strings.
    """

    data_number = set()
    for i in tag_list:
        parsed_tag = (
            i if hasattr(i, "attrs") else BeautifulSoup(i, "html.parser").find()
        )
        if parsed_tag is not None:
            if parsed_tag.get("data-number") is not None:
                data_number.add(parsed_tag.get("data-number"))
    return data_number


def delete_tag(old_changed_strings: list[str]) -> BeautifulSoup:
    """
    Add a "deleted" class to all tags in the list of modified strings that have a
    data-number attribute.

    Decompose all 'style' tags in the HTML

    Return the modified BeautifulSoup object with "deleted" class added to tags.
    """

    soup = get_redline_html()
    for i in soup.find_all():
        if i.name == "style":
            i.decompose()
            continue

        if i.get("data-number") in get_data_number(old_changed_strings):
            if "class" in i.attrs:
                i["class"].append("deleted")
            else:
                i["class"] = ["deleted"]
    return soup


def replace_tag(
    old_changed_strings: list[str], new_changed_strings: list[str]
) -> BeautifulSoup:
    """
    Replace tags matching old_changed_strings with new_changed_strings in the entered
    HTML.

    Decompose all 'style' tags in the HTML

    Return the modified BeautifulSoup object with 'deleted' class added to old tags and
    'inserted' class added to new tags.
    """

    frag = BeautifulSoup("".join(new_changed_strings), "html.parser")
    soup = get_redline_html()
    match = []
    for i in soup.find_all():
        if i.name == "style":
            i.decompose()
            continue
        if i.get("data-number") in get_data_number(old_changed_strings):
            match.append(i)

    for i in frag.find_all():
        if i.name:
            if "class" in i.attrs:
                i["class"].append("inserted")
            else:
                i["class"] = ["inserted"]
    if match:
        match[-1].insert_after(frag)
        for i in match:
            if "class" in i.attrs:
                i["class"].append("deleted")
            else:
                i["class"] = ["deleted"]
    return soup


def insert_tag(new_changed_strings: list[str], i1: int) -> BeautifulSoup:
    """
    Insert new tags matching new_changed_strings into the entered HTML at the position
    corresponding to i1.

    Decompose all 'style' tags in the HTML.

    Return the modified BeautifulSoup object with 'inserted' class added to new tags.
    """

    soup = get_redline_html()
    for i in soup.find_all():
        if i.name == "style":
            i.decompose()
            continue
    tags = soup.find_all()
    frag = BeautifulSoup("".join(new_changed_strings), "html.parser")
    for i in frag.find_all():
        if i.name:
            if "class" in i.attrs:
                i["class"].append("inserted")
            else:
                i["class"] = ["inserted"]
    if i1 < len(tags):
        tags[i1].insert_before(frag)
    else:
        soup.append(frag)
    return soup


def remove_inline_semantics(html: BeautifulSoup) -> BeautifulSoup:
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
        ["b", "i", "u", "strong", "em", "style", "table", "tr", "td", "ol", "ul"]
    ):
        if i.name == "style":
            i.decompose()
        else:
            i.unwrap()
    return soup


def convert_html_to_soup(html: str) -> BeautifulSoup:
    """
    Parse the entered HTML string into a BeautifulSoup object.

    Return the BeautifulSoup object representing the parsed HTML.
    """

    return BeautifulSoup(html, "html.parser")


def format_bs4_html_list(bs4_obj: BeautifulSoup) -> list[str]:
    """
    Perform a number of functions used to format the HTML before diffing.

    Functions performed (in order): 'remove_inline_semantics', 'number_tags', and
    'tags_to_list'.

    Return a list of strings which could be concatenated to produce the formatted HTML.
    """

    return tags_to_list(number_tags(convert_html_to_soup(bs4_obj)))


def get_opcodes() -> list[tuple[str, int, int, int, int]]:
    """
    Remove the inline semantics tags and convert the tags into lists using copies of
    both the commit and current version BeautifulSoup objects.

    Use difflib.SequenceMatcher to compare the two lists of tags and return a list of
    opcodes representing the differences between the 2 lists.

    Return a list of opcodes representing the differences between the commit and current
    version HTML.
    """

    return difflib.SequenceMatcher(
        None,
        tags_to_list(convert_html_to_soup(get_commit_html())),
        tags_to_list(convert_html_to_soup(Repository.convert_docx_to_html()))
    ).get_opcodes()


def get_redline_html() -> BeautifulSoup:
    """
    Remove the inline semantics tags and convert the tags into lists using a copy of the
    commit BeautifulSoup object.

    Return the BeautifulSoup object to be used as the base HTML for the redline
    document.
    """

    return number_tags(convert_html_to_soup(get_commit_html()))


def format_redline_html() -> BeautifulSoup:
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

    opcodes = get_opcodes()
    commit_list = format_bs4_html_list(get_commit_html())
    docx_current_version_list = format_bs4_html_list(Repository.convert_docx_to_html())

    for i in reversed(opcodes):
        tag, i1, i2, j1, j2 = i
        old_changed_strings = commit_list[i1:i2]
        new_changed_strings = docx_current_version_list[j1:j2]
        if tag == "replace":

            redline = replace_tag(old_changed_strings, new_changed_strings)
        if tag == "insert":

            redline = insert_tag(new_changed_strings, i1)
        if tag == "delete":

            redline = delete_tag(old_changed_strings)
    return redline


def write_redline_html_file() -> None:
    """
    Print the redline HTML to a file named 'redline.html' in the current working
    directory.
    """

    with open("redline.html", "w", encoding="utf-8", newline="\n") as f:
        f.write(utils.wrap_html(str(strip_number_attribute(format_redline_html()))))


def main() -> None:
    """Run functions for the <sccs diff> command."""
    Repository.check_repository_layout()

    write_redline_html_file()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
