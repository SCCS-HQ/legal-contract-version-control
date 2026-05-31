import copy
import difflib
import sys
from pathlib import Path

import utils
from bs4 import BeautifulSoup


def get_entered_commit_to_diff():
    """Retrieve the commit file path entered by the user."""

    return sys.argv[2] if len(sys.argv) > 2 else None


def validate_commit(commit_to_diff, docx_current_version):
    """Validate the commit file and current docx file paths."""

    if not commit_to_diff:
        print("No commit file specified.")
        sys.exit(1)

    if not Path(commit_to_diff).is_file():
        print("Commit file not found. Please provide a valid commit file path.")
        sys.exit(1)

    if Path(commit_to_diff).suffix.lower() != ".html":
        print(
            "Commit file is not a .html file. Please provide a valid .html commit file"
        )
        sys.exit(1)

    if not Path(docx_current_version).is_file():
        print(
            "Docx file not found. Re-initialize SCCS for this file with 'sccs init"
            "<file_path>'"
        )
        sys.exit(1)


def get_commit_html(commit_path):
    """Read and return the HTML content of a commit file."""

    try:
        with open(commit_path, "r", encoding="utf-8", newline="\n") as f:
            commit_html = f.read()
    except Exception as e:
        print(f"Error reading commit file: {e}")
        sys.exit(1)
    return commit_html


def number_tags(html):
    """Add sequential data-number attributes to all tags in the HTML."""

    soup = html
    for i, tag in enumerate(soup.find_all()):
        if tag.name == "style":
            continue
        tag["data-number"] = str(i)
    return soup


def strip_number_attribute(html):
    """Remove data-number attributes from all tags in the HTML."""

    soup = html
    for tag in soup.find_all():
        if "data-number" in tag.attrs:
            del tag["data-number"]
    return soup


def tags_to_list(html):
    """Convert all tags in the HTML to a list of strings."""

    soup = html
    return [str(tag) for tag in soup.find_all()]


def get_data_number(tag_list):
    """Retrieve the set of data-number values from a list of tag strings."""

    data_number = set()
    for tag in tag_list:
        parsed_tag = (
            tag if hasattr(tag, "attrs") else BeautifulSoup(tag, "html.parser").find()
        )
        if parsed_tag is not None:
            if parsed_tag.get("data-number") is not None:
                data_number.add(parsed_tag.get("data-number"))
    return data_number


def delete_tag(html, old_changed_strings):
    """Mark tags matching old_changed_strings as deleted in the HTML."""

    old_data_numbers = get_data_number(old_changed_strings)
    soup = html
    for tag in soup.find_all():
        if tag.name == "style":
            tag.decompose()
            continue

        if tag.get("data-number") in old_data_numbers:
            if "class" in tag.attrs:
                tag["class"].append("deleted")
            else:
                tag["class"] = ["deleted"]
    return soup


def replace_tag(html, old_changed_strings, new_changed_strings):
    """Replace tags matching old_changed_strings with new_changed_strings in the
    entered HTML.
    """

    old_data_numbers = get_data_number(old_changed_strings)
    frag = BeautifulSoup("".join(new_changed_strings), "html.parser")
    soup = html
    match = []
    for tag in soup.find_all():
        if tag.name == "style":
            tag.decompose()
            continue
        if tag.get("data-number") in old_data_numbers:
            match.append(tag)

    for i in frag.find_all():
        if i.name:
            if "class" in i.attrs:
                i["class"].append("inserted")
            else:
                i["class"] = ["inserted"]
    if match:
        match[-1].insert_after(frag)
        for tag in match:
            if "class" in tag.attrs:
                tag["class"].append("deleted")
            else:
                tag["class"] = ["deleted"]
    return soup


def insert_tag(html, new_changed_strings, i1):
    """Insert new_changed_strings before the tag at index i1 in the HTML."""

    soup = html
    for tag in soup.find_all():
        if tag.name == "style":
            tag.decompose()
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


def remove_inline_semantics(html):
    """Remove inline semantic tags (b, i, u, strong, em) and style tags from the entered
    HTML."""

    soup = html
    for tag in soup.find_all(["b", "i", "u", "strong", "em", "style"]):
        if tag.name == "style":
            tag.decompose()
        else:
            tag.unwrap()
    return soup


def convert_html_to_soup(html):
    """Convert an HTML string to a BeautifulSoup object."""

    return BeautifulSoup(html, "html.parser")


def format_bs4_html_list(bs4_obj):
    """Format a BeautifulSoup object into a numbered list of tag strings."""

    return tags_to_list(number_tags(remove_inline_semantics(copy.copy(bs4_obj))))


def get_opcodes(commit_soup, current_soup):
    """Get the sequence of opcodes comparing commit HTML to current HTML."""

    commit_tags = tags_to_list(remove_inline_semantics(copy.copy(commit_soup)))
    current_tags = tags_to_list(remove_inline_semantics(copy.copy(current_soup)))
    return difflib.SequenceMatcher(None, commit_tags, current_tags).get_opcodes()


def get_redline_html(commit_soup):
    """Return a numbered, inline-semantics-stripped copy of the commit HTML."""

    return number_tags(remove_inline_semantics(copy.copy(commit_soup)))


def format_redline_html(redline, opcodes, commit_list, docx_current_version_list):
    """Apply opcodes to the redline HTML to produce a tracked-changes document."""

    for opcode in reversed(opcodes):
        tag, i1, i2, j1, j2 = opcode
        old_changed_strings = commit_list[i1:i2]
        new_changed_strings = docx_current_version_list[j1:j2]
        if tag == "replace":
            redline = replace_tag(redline, old_changed_strings, new_changed_strings)
        if tag == "insert":
            redline = insert_tag(redline, new_changed_strings, i1)
        if tag == "delete":
            redline = delete_tag(redline, old_changed_strings)
    return redline


def write_redline_html_file(redline, filename="redline.html"):
    """Write the redline HTML to a file."""

    with open(filename, "w", encoding="utf-8", newline="\n") as f:
        f.write(utils.wrap_html(str(strip_number_attribute(redline))))


if __name__ == "__main__":

    utils.check_sccs_layout()

    validate_commit(get_entered_commit_to_diff(), utils.current_file_docx_path)

    docx_current_version_html = utils.convert_docx_to_html()

    commit_html = get_commit_html(get_entered_commit_to_diff())

    bs4_docx_current_version_soup = convert_html_to_soup(docx_current_version_html)

    docx_current_version_list = format_bs4_html_list(bs4_docx_current_version_soup)

    bs4_commit_soup = convert_html_to_soup(commit_html)
    commit_list = format_bs4_html_list(bs4_commit_soup)

    opcodes = get_opcodes(bs4_commit_soup, bs4_docx_current_version_soup)

    base_redline_html = get_redline_html(bs4_commit_soup)

    redline = format_redline_html(
        base_redline_html, opcodes, commit_list, docx_current_version_list
    )

    write_redline_html_file(redline)
