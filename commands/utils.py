import hashlib
import json
import os
import re
import sys
from pathlib import Path

import mammoth

working_directory_path = os.getcwd()

current_file_docx_path = os.path.join(
    working_directory_path, f"{os.path.basename(working_directory_path)}.docx"
)

sccs_versions_directory_path = os.path.join(working_directory_path, ".sccs")

default_html_styles = """<style>\n* {\nfont-family: Arial, Helvetica, sans-serif;\n}\n\n.inserted {\nbackground-color: #d4fcbc;\ndisplay: block;\nwidth: fit-content;\n}\n\n.deleted {\nbackground-color: #fbb6c2;\ndisplay: block;\nwidth: fit-content;\n}\n\n.center {\ndisplay: flex;\njustify-content: center;\n}\n</style>"""

current_branch_path = os.path.join(
    working_directory_path, ".sccs", "current_branch", "current_branch.json"
)


def clean_directory_name(name):
    return re.sub(r'[\\/:*?"<>|]', "-", name).strip(". ")


def check_sccs_layout(
    sccs_dir=sccs_versions_directory_path, docx_path=current_file_docx_path
):

    if not Path(sccs_dir).is_dir():
        print("This file has not been initialized with SCCS.")
        print("Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "current_branch")).is_dir():
        print(
            "Current branch directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(
        os.path.join(sccs_dir, "current_branch", "current_branch.json")
    ).is_file():
        print(
            "Current branch file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    try:
        with open(
            os.path.join(sccs_dir, "current_branch", "current_branch.json"),
            "r",
            encoding="utf-8",
            newline="\n",
        ) as current_branch_file:
            current_branch = json.load(current_branch_file).get("current_branch")
            if not current_branch:
                print(
                    "Current branch not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
                )
                sys.exit(1)

    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        print(
            "Current branch file is missing or corrupted. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        print("Error: ", e)
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "branches", current_branch)).is_dir():
        print(
            "Branch directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(
        os.path.join(sccs_dir, "branches", current_branch, "commit_file_hash")
    ).is_dir():
        print(
            "Commit file hash directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)
    if not Path(
        os.path.join(
            sccs_dir,
            "branches",
            current_branch,
            "commit_file_hash",
            "commit_file_hash.json",
        )
    ).is_file():
        print(
            "Commit file hash JSON not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "commit_messages")).is_dir():
        print(
            "Commit messages directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(
        os.path.join(sccs_dir, "commit_messages", "commit_messages.json")
    ).is_file():
        print(
            "Commit messages JSON not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects")).is_dir():
        print(
            "Objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects", "docx")).is_dir():
        print(
            "Docx objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects", "html")).is_dir():
        print(
            "HTML objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects", "view_html")).is_dir():
        print(
            "View HTML objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "config")).is_dir():
        print(
            "Config directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "config", "config.json")).is_file():
        print(
            "Config file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "branches", current_branch, "history")).is_dir():
        print(
            "History directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(
        os.path.join(
            sccs_dir, "branches", current_branch, "history", "commit_history.json"
        )
    ).is_file():
        print(
            "History file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file."
        )
        sys.exit(1)

    if not Path(docx_path).is_file():
        print(
            "Docx file not found. Re-initialize SCCS for this file with 'sccs init <file_path>'"
        )
        sys.exit(1)


def wrap_html(html, styles=default_html_styles):
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head><body><div class='center'><div id='target'>{html}</div></div></body></html>"


def hash_current_docx_binary(docx_path=current_file_docx_path):
    try:
        with open(docx_path, "rb") as f:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        print(f"Error processing .docx file: {e}")
        sys.exit(1)

    return hashed_file


def get_current_branch(file_path=current_branch_path):
    try:
        with open(
            file_path, "r", encoding="utf-8", newline="\n"
        ) as current_branch_file:
            current_branch = json.load(current_branch_file).get("current_branch")
            if not current_branch:
                print(
                    "Current branch is missing from JSON. Please run 'sccs init <file_path>' to initialize SCCS for this file."
                )
                sys.exit(1)
    except Exception as e:
        print(f"Error reading current branch: {e}")
        sys.exit(1)
    return current_branch


def get_branch_data(file_path=current_branch_path, key=None):
    try:
        with open(file_path, "r", encoding="utf-8", newline="\n") as f:
            data = json.load(f)
            if key:
                return data.get(key)
            return data

    except Exception as e:
        print(f"Error reading current branch data: {e}")
        sys.exit(1)


def convert_docx_to_html(docx_path=None):
    if docx_path is None:
        docx_path = current_file_docx_path
    try:
        with open(docx_path, "rb") as f:
            result = mammoth.convert_to_html(f)
            return result.value
    except Exception as e:
        print(f"Error converting .docx to HTML: {e}")
        sys.exit(1)
