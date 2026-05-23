import os
from pathlib import Path
import shutil
import sys
import hashlib
from datetime import datetime
import json
import mammoth
from default_css_styles import styles
from utils import check_sccs, path, directory_path, wrap_html

check_sccs()

def hash_current_docx_binary():
    try:
        with open(path, "rb") as f:
                hasher = hashlib.sha256()
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
                hashed_file = hasher.hexdigest()
    except Exception as e:
        print(f"Error processing .docx file: {e}")
        sys.exit(1)
    return hashed_file

def convert_docx_to_html():
    try: 
        with open(path, "rb") as f:
            result = mammoth.convert_to_html(f)
            return result.value
    except Exception as e:
        print(f"Error converting .docx to HTML: {e}")
        sys.exit(1)

def get_obj_from_config(object):
    # Get name and email entered on init
    config_path = os.path.join(directory_path, ".sccs", "config", "config.json")
    if not Path(config_path).is_file():
        print("Configuration file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8", newline="\n") as config_file:
        config = json.load(config_file)
        object = config.get(object)
    
    return object

def get_commit_message():
    # Get commit message
    commit_message = input("Enter commit message: ").strip()

    if commit_message == "":
        print("Commit message cannot be empty.")
        sys.exit(1)
    
    return commit_message

def get_timestamp():
    return datetime.now().isoformat()

def get_current_branch():
   #Get current branch
    current_branch_path = os.path.join(directory_path, ".sccs", "current_branch", "current_branch.json")
    if not Path(current_branch_path).is_file():
        print("Current branch file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    with open(current_branch_path, "r", encoding="utf-8", newline="\n") as current_branch_file:
        current_branch = json.load(current_branch_file).get("current_branch") 

    return current_branch

def get_history_path():
    return os.path.join(directory_path, ".sccs", "branches", get_current_branch(), "history", "commit_history.json")

def get_commit_history():
    history_path = get_history_path()
    if not Path(history_path).is_file():
        print("History file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    try:
        with open(history_path, "r", encoding="utf-8", newline="\n") as history_file:
        
            history = json.load(history_file)

    except Exception as e:
        print(f"Error retrieving JSON from history file: {e}")
        sys.exit(1)

    return history

def get_parent_hash(history):
    parent_hash = history["history"].get("latest_commit")
    return parent_hash

def generate_commit_hash(timestamp, commit_message, name, email, parent_hash):
    return hashlib.sha256(f'{timestamp}/{commit_message}/{name}/{email}/{parent_hash}'.encode()).hexdigest()

def copy_docx_to_objects(sha_hash):
    shutil.copy2(os.path.join(directory_path, Path(path).name) , os.path.join(directory_path, ".sccs", "objects", "docx", f"{sha_hash}.docx"))

def write_diff_html(sha_hash, docx_html):
    with open(os.path.join(directory_path, ".sccs", "objects", "html", f"{sha_hash}.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(styles + docx_html)

def write_view_html(sha_hash, docx_html):
    with open(os.path.join(directory_path, ".sccs", "objects", "view_html", f"{sha_hash}.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(wrap_html(docx_html))

def update_commit_log_history(history, sha_hash, timestamp, name, email, commit_message):
    commit_history_file = get_history_path()
    if not os.path.isfile(commit_history_file):
        print("History file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    # Update history
    history["history"]["latest_commit"] = f"{sha_hash}"
    history["history"]["latest_commit_number"] = history["history"].get("latest_commit_number", 0) + 1
    history["history"]["commit_order"][str(history["history"]["latest_commit_number"])] = f"{sha_hash}"

    history["log"][f"{sha_hash}"] = {
        "timestamp": timestamp,
        "author": f"{name} <{email}>",
        "message": commit_message
    }
    return {history: commit_history_file}

def update_commit_messages(sha_hash, commit_message):
    # Update commit messages
    commit_messages_path = os.path.join(directory_path, ".sccs", "commit_messages", "commit_messages.json")
    if not Path(commit_messages_path).is_file():
        print("Commit messages file not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    with open(commit_messages_path, "r", encoding="utf-8", newline="\n") as commit_messages_file:
        try:
            messages = json.load(commit_messages_file)
        except Exception as e:
            print(f"Error reading commit messages: {e}")
            sys.exit(1)

    messages[f"{sha_hash}"] = f"{commit_message}"

    return {messages: commit_messages_path}

def update_commit_binary_hash_history(sha_hash, hash_docx_binary):
    # Update commit file hash
    commit_file_hash_path = os.path.join(directory_path, ".sccs", "branches", get_current_branch(), "commit_file_hash", "commit_file_hash.json")
    if not Path(commit_file_hash_path).is_file():
        print("Commit file hash not found. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    try: 
        with open(commit_file_hash_path, "r", encoding="utf-8", newline="\n") as f:
            try:
                commit_file_hash = json.load(f)
            except Exception as e:
                print(f"Error reading commit file hash: {e}")
                sys.exit(1)
    except (json.JSONDecodeError, KeyError, TypeError, OSError) as e:
        print("Commit file hash is missing or corrupted. Please run 'sccs init <file_path>' to initialize SCCS for this file.")
        sys.exit(1)

    commit_file_hash[f"{sha_hash}"] = hash_docx_binary

    return {commit_file_hash, commit_file_hash_path}

def combine_update_dicts(*dicts):
    update_dict = {}
    for d in dicts:
        update_dict.update(d)
    return update_dict

def atomically_update_history(dict):
    for key, value in dict.items():
        try: 
            with open(Path(value).with_suffix("tmp"), "w", encoding="utf-8", newline="\n") as f:
                try:
                    json.dump(key, f)
                except Exception as e:
                    print(f"Error writing to temporary file: {e}")
                    sys.exit(1)
        except Exception as e:
            print(f"Error opening temporary file: {e}")
            sys.exit(1)
    for key, value in dict.items():
        try:
            os.replace(Path(value).with_suffix("tmp"), value)
        except Exception as e:
            print(f"Error replacing temporary file: {e}")
            sys.exit(1)

def print_confirmation_message(sha_hash):
    print(f"Commit {sha_hash} created successfully.")

if __name__ == "__main__":

    hash_docx_binary = hash_current_docx_binary()

    name = get_obj_from_config("name")

    email = get_obj_from_config("email")

    docx_html = convert_docx_to_html()

    commit_message = get_commit_message()

    timestamp = get_timestamp()

    current_branch = get_current_branch()

    history = get_commit_history()

    parent_hash = get_parent_hash(history)

    sha_hash = generate_commit_hash(timestamp, commit_message, name, email, parent_hash)

    copy_docx_to_objects(sha_hash)

    write_diff_html(sha_hash, docx_html)

    write_view_html(sha_hash, docx_html)

    atomically_update_history(combine_update_dicts(update_commit_log_history(history, sha_hash, timestamp, name, email, commit_message), update_commit_binary_hash_history(sha_hash, hash_docx_binary), update_commit_messages(sha_hash, commit_message)))

    print_confirmation_message(sha_hash)