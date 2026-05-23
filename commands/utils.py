import json
import os
from pathlib import Path
import re
import sys

directory_path = os.getcwd()

path = os.path.join(directory_path, f"{os.path.basename(directory_path)}.docx")

sccs_dir = os.path.join(directory_path, ".sccs")

def sanitize_dirname(name):
    return re.sub(r'[\\/:*?"<>|]', '-', name).strip('. ')

def check_sccs():

    if not Path(sccs_dir).is_dir():
        print("This file has not been initialized with SCCS.")
        print("Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "current_branch")).is_dir():
        print("Current branch directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "current_branch", "current_branch.json")).is_file():
        print("Current branch file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    try: 
        with open(os.path.join(sccs_dir, "current_branch", "current_branch.json"), "r", encoding="utf-8", newline="\n") as current_branch_file:
            current_branch = json.load(current_branch_file).get("current_branch")
            if not current_branch:
                print("Current branch not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
                sys.exit(1)

    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        print("Current branch file is missing or corrupted. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        print("Error: ", e)
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "branches", current_branch)).is_dir():
        print("Branch directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "branches", current_branch, "commit_file_hash")).is_dir():
        print("Commit file hash directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)
    if not Path(os.path.join(sccs_dir, "branches", current_branch, "commit_file_hash", "commit_file_hash.json")).is_file():
        print("Commit file hash JSON not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "commit_messages")).is_dir():
        print("Commit messages directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "commit_messages", "commit_messages.json")).is_file():
        print("Commit messages JSON not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects")).is_dir():
        print("Objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects", "docx")).is_dir():
        print("Docx objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects", "html")).is_dir():
        print("HTML objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "objects", "view_html")).is_dir():
        print("View HTML objects directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "config")).is_dir():
        print("Config directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "config", "config.json")).is_file():
        print("Config file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "branches", current_branch, "history")).is_dir():
        print("History directory not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(os.path.join(sccs_dir, "branches", current_branch, "history", "commit_history.json")).is_file():
        print("History file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    if not Path(path).is_file():
        print("Docx file not found. Re-initialize SCCS for this file with 'sccs init <file_path>'")
        sys.exit(1)

def wrap_html(html):
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{default_styles}</head><body><div class='center'><div id='target'>{html}</div></div></body></html>"

default_styles = """<style>
* {
font-family: Arial, Helvetica, sans-serif;}

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