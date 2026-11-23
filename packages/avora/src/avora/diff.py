import copy
import difflib
import filecmp

from avora import utils
from avora.constants_classes import AvoraConstants
from avora.exceptions import AvoraException
from avora.repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryStatus,
)
from bs4 import BeautifulSoup


def delete_tag(
    c: AvoraConstants, old_changed_strings: list[str], soup: BeautifulSoup
) -> BeautifulSoup:
    """
    Add a deleted class to the tags in the provided BeautifulSoup object that match the
    data-number attributes of the tags in the old_changed_strings list. This function
    modifies the soup in place and returns it.
    """

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


def format_redline_html(
    c: AvoraConstants,
    past_version: list[str],
    current_version: list[str],
    commit_identifier_list: list[str],
    document_current_version_list: list[str],
    soup: BeautifulSoup,
) -> BeautifulSoup:
    """
    Format the provided BeautifulSoup object to highlight differences between the past
    and current versions of the document. This function uses the difflib library to
    identify changes and applies appropriate HTML classes to indicate insertions,
    deletions, and replacements. The function modifies the soup in place and returns it.
    """

    redline = soup
    for tag, i1, i2, j1, j2 in reversed(
        difflib.SequenceMatcher(None, past_version, current_version).get_opcodes()
    ):
        old_changed_strings = commit_identifier_list[i1:i2]
        new_changed_strings = document_current_version_list[j1:j2]
        if tag == c.REPLACE_OPCODE:

            redline = replace_tag(c, old_changed_strings, new_changed_strings, soup)
        if tag == c.INSERT_OPCODE:

            redline = insert_tag(c, new_changed_strings, i1, soup)
        if tag == c.DELETE_OPCODE:

            redline = delete_tag(c, old_changed_strings, soup)
    return redline


def generate_diff_output(
    c: AvoraConstants, commit_identifier: str, rd: RepositoryData, ri: RepositoryIO
) -> BeautifulSoup:
    """
    Generate a BeautifulSoup object representing the differences between the past and
    current versions of the document based on the specified commit identifier. This
    function retrieves the past version of the document from the commit and compares it
    to the current version, applying appropriate formatting to highlight changes.
    """

    commit_soup = BeautifulSoup(
        rd.commit_file_bytes(commit_identifier, c.HTML_DIRECTORY), c.HTML_PARSER
    )

    current_version_soup = BeautifulSoup(ri.document_html(), c.HTML_PARSER)

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


def get_data_number(c: AvoraConstants, tag_list: list[str]) -> list[str]:
    """
    Retrieve the data-number attributes from the provided list of tags in the order
    they are encountered. This function parses each tag in the list and extracts the
    data-number attribute, if present, adding it to a list. The function returns the
    list of data-number attributes found in the tags.
    """

    data_number = []
    for i in tag_list:
        parsed_tag = BeautifulSoup(i, c.HTML_PARSER).find()
        if (
            parsed_tag is not None
            and parsed_tag.get(c.DATA_NUMBER_HTML_ATTRIBUTE) is not None
        ):
            data_number.append(parsed_tag[c.DATA_NUMBER_HTML_ATTRIBUTE])
    return data_number


def insert_tag(
    c: AvoraConstants,
    new_changed_strings: list[str],
    insert_index: int,
    soup: BeautifulSoup,
) -> BeautifulSoup:
    """
    Insert new tags created from the new_changed_strings list into the provided
    BeautifulSoup object at the specified index. This function modifies the soup in
    place and returns it.
    """

    tags = soup.find_all()

    for i in tags:
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
            continue
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


def number_tags(c: AvoraConstants, soup: BeautifulSoup) -> BeautifulSoup:
    """
    Add a data-number attribute to each tag in the provided BeautifulSoup object,
    excluding style tags. The data-number attribute is set to the index of the tag in
    the list of all tags. This function modifies the soup in place and returns it.
    """

    for i, tag in enumerate(soup.find_all()):
        if tag.name == c.STYLE_TAG_NAME:
            continue
        tag[c.DATA_NUMBER_HTML_ATTRIBUTE] = str(i)
    return soup


def print_diff_success_message(c: AvoraConstants) -> None:
    """
    Print a success message after a successful diff operation.
    """

    print(c.DIFF_SUCCESS_MESSAGE)


def remove_inline_semantics(c: AvoraConstants, html: BeautifulSoup) -> BeautifulSoup:
    """
    Remove inline semantics from the provided HTML by unwrapping certain tags and
    removing style tags. This function creates a copy of the original HTML to avoid
    modifying it directly.
    """

    soup = copy.deepcopy(html)
    for i in soup.find_all(c.TAGS_TO_UNWRAP):
        if i.name == c.STYLE_TAG_NAME:
            i.decompose()
        else:
            i.unwrap()
    soup.smooth()
    return soup


def replace_tag(
    c: AvoraConstants,
    old_changed_strings: list[str],
    new_changed_strings: list[str],
    soup: BeautifulSoup,
) -> BeautifulSoup:
    """
    Replace tags in the provided BeautifulSoup object that match the data-number
    attributes of the tags in the old_changed_strings list with new tags created from
    the new_changed_strings list. This function modifies the soup in place and returns
    it.
    """

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
        match[c.LAST_TAG_INDEX].insert_after(html_fragment)
        for i in match:
            if c.CLASS_HTML_ATTRIBUTE in i.attrs:
                i[c.CLASS_HTML_ATTRIBUTE].append(c.DELETED_HTML_ATTRIBUTE_VALUE)
            else:
                i[c.CLASS_HTML_ATTRIBUTE] = [c.DELETED_HTML_ATTRIBUTE_VALUE]
    return soup


def strip_number_attribute(c: AvoraConstants, soup: BeautifulSoup) -> BeautifulSoup:
    """
    Strip the data-number attribute from all tags in the provided BeautifulSoup object.
    This function modifies the soup in place and returns it.
    """

    for i in soup.find_all():
        if c.DATA_NUMBER_HTML_ATTRIBUTE in i.attrs:
            del i[c.DATA_NUMBER_HTML_ATTRIBUTE]
    return soup


def tags_to_list(soup: BeautifulSoup) -> list[str]:
    """
    Convert the provided BeautifulSoup object into a list of strings, where each string
    represents a tag in the HTML. This function extracts all tags from the soup and
    returns them as a list of strings."""

    return [str(i) for i in soup.find_all()]


def validate_diff(
    c: AvoraConstants, rd: RepositoryData, commit_identifier: str
) -> None:
    """
    Validate the specified commit identifier by checking if it exists in the repository
    and if the document at that commit is different from the current version.

    Raises an AvoraException if the commit identifier is invalid or if there are no
    differences between the past and current versions of the document.
    """

    commit_path = rd.commit_identifier_to_full_path(
        commit_identifier, c.DOCUMENT_DIRECTORY
    )

    if filecmp.cmp(commit_path, rd.paths.document_path()):
        raise AvoraException(c.DIFF_NO_CHANGES_ERROR_MESSAGE)


def main(
    c: AvoraConstants,
    commit_identifier: str,
    rd: RepositoryData,
    ri: RepositoryIO,
    rs: RepositoryStatus,
) -> None:
    """
    Run the diff command by setting the current branch as the target, validating the
    repository layout and entered commit identifier, and generating the diff output
    between the entered commit and the current document.

    Write the diff output to the repository, print a success message, and reset the
    target branch when the operation completes.
    """

    try:
        rs.validate_repository_layout()
        rs.target.set(rd.current_branch())
        rs.raise_for_uncommitted_changes()

        validate_diff(c, rd, commit_identifier)

        ri.write_diff_output(
            utils.wrap_html(
                c,
                str(
                    strip_number_attribute(
                        c,
                        generate_diff_output(
                            c,
                            rd.short_commit_identifier_to_full(commit_identifier),
                            rd,
                            ri,
                        ),
                    )
                ),
                c.DEFAULT_HTML_STYLES,
            )
        )

        print_diff_success_message(c)
    except AvoraException:
        raise
    except Exception as e:
        raise AvoraException(c.STAGED_REPOSITORY_ERROR_MESSAGE) from e
    finally:
        rs.target.reset()
