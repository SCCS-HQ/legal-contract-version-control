import os
import shutil
from pathlib import Path
import sys
import hashlib
from datetime import datetime
import json
import mammoth
from default_css_styles import styles
from sccs_layout_check import wrap_html
# Get user inputted path argument
INITIAL_COMMIT_MESSAGE = "initial commit (This is a default commit message for initial version)"
ENTERED_DOCUMENT_PATH = sys.argv[2] if len(sys.argv) > 2 else None
DOCUMENT_DIRECTORY_PATH = Path(ENTERED_DOCUMENT_PATH).with_suffix('')

# Strip .docx extension from the file name to create a directory
def check_if_arg_entered(arg):
    if not arg:
        print("No file path provided")
        sys.exit(1)

def ask_config_input(data):
    data_value = input(f"Enter your {data}: ").strip()
    if data_value == "":
        print(f"{data.capitalize()} Cannot be empty.")
        sys.exit(1)
    else:
        return data_value

def check_for_prev_init():
    if Path(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs")).is_dir():
        print("This file has already been initialized with SCCS")
        sys.exit(1)

def check_file_requirements():
    if not ENTERED_DOCUMENT_PATH or Path(ENTERED_DOCUMENT_PATH).suffix.lower() != ".docx" or not Path(ENTERED_DOCUMENT_PATH).is_file():
        print("Invalid file path, make sure the file exists and is a .docx file")
        sys.exit(1)

def hash_document():
    try:
        with open(ENTERED_DOCUMENT_PATH, "rb") as f:
            try:
                hasher = hashlib.sha256()
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
                hashed_file = hasher.hexdigest()
            except Exception as e:
                print(f"Error hashing .docx file: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error processing .docx file: {e}")
        sys.exit(1)
    return hashed_file

def convert_document_to_html():
    try: 
        with open(ENTERED_DOCUMENT_PATH, "rb") as f:
            try:
                result = mammoth.convert_to_html(f)
                html = result.value
            except Exception as e:
                print(f"Error converting .docx to HTML: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error processing .docx file: {e}")
        sys.exit(1)
    return html   

def create_commit_sha_hash(timestamp, user_name, user_email):
    return hashlib.sha256(f'{timestamp}/initial_version/{user_name}/{user_email}'.encode()).hexdigest()

def create_sccs_directory_layout():
    os.makedirs(DOCUMENT_DIRECTORY_PATH, exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "objects"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "objects", "docx"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "objects", "html"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "objects", "view_html"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "branches"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "branches", "main"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "branches", "main", "history"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "branches", "main", "commit_file_hash"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "commit_messages"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "config"), exist_ok=True)
    os.makedirs(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "current_branch"), exist_ok=True)

def move_document_to_repo_directory():
    shutil.move(ENTERED_DOCUMENT_PATH, DOCUMENT_DIRECTORY_PATH)

def copy_document_to_objects_as_docx_and_html():
    shutil.copy2(os.path.join(DOCUMENT_DIRECTORY_PATH, Path(ENTERED_DOCUMENT_PATH).name), os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "objects", "docx", f"{sha_hash}.docx"))

    with open(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "objects", "html", f"{sha_hash}.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(styles + html)

    with open(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "objects", "view_html", f"{sha_hash}.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(wrap_html(html))

def get_current_iso_time():
    return datetime.now().isoformat()

def write_history_data():
    history_data = {
        "history": {
            "initial_commit": f"{sha_hash}",
            "latest_commit": f"{sha_hash}",
            "latest_commit_number": 1,
            "commit_order": {
                "1": f"{sha_hash}"
            }
        },
        "log": {
            f"{sha_hash}": {
                "timestamp": get_current_iso_time(),
                "author": f"{config_user_name} <{config_user_email}>",
                "message": INITIAL_COMMIT_MESSAGE
            }
        }
    }
    try:
        with open(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "branches", "main", "history", "commit_history.json"), "w", encoding="utf-8", newline="\n") as f:
            try: 
                json.dump(history_data, f, indent=4)
            except Exception as e:
                print(f"Error writing commit history data: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error opening commit history file: {e}")
        sys.exit(1)

def write_commit_message_data():
    commit_message_data = {
        f"{sha_hash}": INITIAL_COMMIT_MESSAGE
    }
    try:
        with open(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "commit_messages", "commit_messages.json"), "w", encoding="utf-8", newline="\n") as f:
            try:
                json.dump(commit_message_data, f, indent=4)
            except Exception as e:
                print(f"Error writing commit message data: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error opening commit message data file: {e}")
        sys.exit(1)

def write_config_data():
    config_data = {
        "name": f"{config_user_name}",
        "email": f"{config_user_email}"
    }
    try:
        with open(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "config", "config.json"), "w", encoding="utf-8", newline="\n") as f:
            try:
                json.dump(config_data, f, indent=4)
            except Exception as e:
                print(f"Error writing config data: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error opening config data file: {e}")
        sys.exit(1)

def write_hashed_file_commit_data():
    commit_file_hash_data = {
        f"{sha_hash}": hashed_file
    }
    try:
        with open(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "branches", "main", "commit_file_hash", "commit_file_hash.json"), "w", encoding="utf-8", newline="\n") as f:
            try:
                json.dump(commit_file_hash_data, f, indent=4)
            except Exception as e:
                print(f"Error writing commit file hash data: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error opening commit file hash data file: {e}")
        sys.exit(1)

def write_branch_data():
    branches_data = {
        "current_branch": "main",
        "branches": ["main"]
    }
    try:
        with open(os.path.join(DOCUMENT_DIRECTORY_PATH, ".sccs", "current_branch", "current_branch.json"), "w", encoding="utf-8", newline="\n") as f:
            try:
                json.dump(branches_data, f, indent=4)
            except Exception as e:
                print(f"Error writing branch data: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error opening branch data file: {e}")
        sys.exit(1)

def confirmation_message():
    print("SCCS initialization complete.")

check_if_arg_entered(ENTERED_DOCUMENT_PATH)

check_for_prev_init()

check_file_requirements()

hashed_file = hash_document()

html = convert_document_to_html()

config_user_name = ask_config_input("name")

config_user_email = ask_config_input("email")

sha_hash = create_commit_sha_hash(get_current_iso_time(), config_user_name, config_user_email)

create_sccs_directory_layout()

move_document_to_repo_directory()

copy_document_to_objects_as_docx_and_html()

write_history_data()

write_commit_message_data()

write_config_data()

write_hashed_file_commit_data()

write_branch_data()

confirmation_message()
