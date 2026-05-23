import os
from pathlib import Path
import sys
import hashlib
import json
import utils

CURRENT_BRANCH_PATH = os.path.join(utils.working_directory_path, ".sccs", "current_branch", "current_branch.json")

def get_current_branch():
    try:
        with open(CURRENT_BRANCH_PATH, "r", encoding="utf-8", newline="\n") as current_branch_file:
            try:
                current_branch = json.load(current_branch_file).get("current_branch")
                if not current_branch:
                    print("Current branch is missing from JSON. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
                    sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from current branch file: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error reading current branch: {e}")
        sys.exit(1)
    return current_branch

def hash_current_docx_binary(file_path):
    try:
        with open(file_path, "rb") as f:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
            hashed_file = hasher.hexdigest()
    except Exception as e:
        print(f"Error processing .docx file: {e}")
        sys.exit(1)

    return hashed_file

def get_latest_commit_hash_file(current_branch):
    # get the latest commit filename hash from commit history
    history_path = os.path.join(utils.working_directory_path, ".sccs", "branches", current_branch, "history", "commit_history.json")
    if not Path(history_path).is_file():
        print("History file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    try:
        with open(history_path, "r", encoding="utf-8", newline="\n") as history_file:
            try:
                history = json.load(history_file)
                latest_commit_hash = history["history"]["latest_commit"]
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error reading history file: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error opening history file: {e}")
        sys.exit(1)

    if not latest_commit_hash:
        print("History file is missing the latest commit information. Please reinitialize SCCS for this file.") 
        sys.exit(1)
    
    return latest_commit_hash

def get_latest_commit_file_binary_hash(current_branch):
    # get the hash of the latest committed file
    latest_commit_hash = get_latest_commit_hash_file(current_branch)
    latest_commit_file_hash_path = os.path.join(utils.working_directory_path, ".sccs", "branches", current_branch, "commit_file_hash", "commit_file_hash.json")
    if not Path(latest_commit_file_hash_path).is_file():
        print("Latest commit file hash not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    try:
        with open(latest_commit_file_hash_path, "r", encoding="utf-8", newline="\n") as f:
            try:
                commit_file_hash_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from latest commit file hash: {e}")
                sys.exit(1)
            try:
                latest_commit_file_hash = commit_file_hash_data.get(latest_commit_hash)
            except Exception as e:
                print(f"Error retrieving latest commit file hash: {e}")
                sys.exit(1)
                
            if not latest_commit_file_hash:
                print("Latest commit file hash is missing from JSON. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
                sys.exit(1)
    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        print(f"Error reading latest commit file hash: {e}")
        sys.exit(1)

    if not latest_commit_file_hash:
        print("Latest commit file hash is missing. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    return latest_commit_file_hash

def compare_hashes(old_hash, new_hash):
    return old_hash == new_hash

def print_changes_message_and_exit(old_hash, new_hash):
    if compare_hashes(old_hash, new_hash):
        print("No changes detected since the latest commit. Nothing to commit.")
        sys.exit(0)
    else:
        print("Changes detected since the latest commit. You can proceed with committing these changes.")
        sys.exit(1)

if __name__ == "__main__":
    utils.check_sccs_layout()
    current_branch = get_current_branch()
    print_changes_message_and_exit(get_latest_commit_file_binary_hash(current_branch), hash_current_docx_binary(utils.current_file_docx_path))