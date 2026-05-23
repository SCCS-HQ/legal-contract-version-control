import json
import os
from pathlib import Path
import re
import sys

working_directory_path = os.getcwd()

current_file_docx_path = os.path.join(working_directory_path, f"{os.path.basename(working_directory_path)}.docx")

sccs_versions_directory_path = os.path.join(working_directory_path, ".sccs")

def clean_directory_name(name):
    return re.sub(r'[\\/:*?"<>|]', '-', name).strip('. ')

def check_sccs_layout():

    if not Path(sccs_versions_directory_path).is_dir():
        print("This file has not been initialized with SCCS.")
        print("Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "current_branch")).is_dir():
        print("Current branch directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "current_branch", "current_branch.json")).is_file():
        print("Current branch file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    try: 
        with open(os.path.join(sccs_versions_directory_path, "current_branch", "current_branch.json"), "r", encoding="utf-8", newline="\n") as current_branch_file:
            current_branch = json.load(current_branch_file).get("current_branch")
            if not current_branch:
                print("Current branch not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
                sys.exit(1)

    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        print("Current branch file is missing or corrupted. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        print("Error: ", e)
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "branches", current_branch)).is_dir():
        print("Branch directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "branches", current_branch, "commit_file_hash")).is_dir():
        print("Commit file hash directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)
    if not Path(os.path.join(sccs_versions_directory_path, "branches", current_branch, "commit_file_hash", "commit_file_hash.json")).is_file():
        print("Commit file hash JSON not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "commit_messages")).is_dir():
        print("Commit messages directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "commit_messages", "commit_messages.json")).is_file():
        print("Commit messages JSON not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "objects")).is_dir():
        print("Objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "objects", "docx")).is_dir():
        print("Docx objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "objects", "html")).is_dir():
        print("HTML objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "objects", "view_html")).is_dir():
        print("View HTML objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "config")).is_dir():
        print("Config directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "config", "config.json")).is_file():
        print("Config file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "branches", current_branch, "history")).is_dir():
        print("History directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_versions_directory_path, "branches", current_branch, "history", "commit_history.json")).is_file():
        print("History file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(current_file_docx_path).is_file():
        print("Docx file not found. Re-initialize SCCS for this file with 'sccs init <file_path>'")
        sys.exit(1)

def wrap_html(html):
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{default_html_styles}</head><body><div class='center'><div id='target'>{html}</div></div></body></html>"

default_html_styles = """<style>
* {
font-family: Arial, Helvetica, sans-serif;
}

.inserted {
background-color: #d4fcbc;
display: block;
width: fit-content;
}

.deleted {
background-color: #fbb6c2;
display: block;
width: fit-content;
}

.center {
display: flex;
justify-content: center;
}
</style>"""