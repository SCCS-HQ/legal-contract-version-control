import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import utils


def get_entered_document_path():
    """Retrieve the document path entered by the user."""

    return sys.argv[2] if len(sys.argv) > 2 else None


def get_document_repo_path():
    """Return the repo directory path derived from the entered document path."""

    path = get_entered_document_path()
    if not path:
        return None
    return Path(path).with_suffix("")


def check_if_arg_entered(arg):
    """Check that a file path argument was provided."""

    if not arg:
        print("No file path provided")
        sys.exit(1)


def ask_config_input(data):
    """Prompt the user for a config value and return it."""

    data_value = input(f"Enter your {data}: ").strip()
    if data_value == "":
        print(f"{data.capitalize()} Cannot be empty.")
        sys.exit(1)
    else:
        return data_value


def check_for_prev_init():
    """Exit if the document has already been initialized with SCCS."""

    if Path(os.path.join(get_document_repo_path(), ".sccs")).is_dir():
        print("This file has already been initialized with SCCS")
        sys.exit(1)


def check_file_requirements():
    """Validate that the entered path points to an existing .docx file."""

    entered_path = get_entered_document_path()
    if (
        not entered_path
        or Path(entered_path).suffix.lower() != ".docx"
        or not Path(entered_path).is_file()
    ):
        print("Invalid file path, make sure the file exists and is a .docx file")
        sys.exit(1)


def create_commit_sha_hash(timestamp, user_name, user_email):
    """Create a SHA-256 hash for the initial commit."""

    return hashlib.sha256(
        f"{timestamp}/initial_version/{user_name}/{user_email}".encode()
    ).hexdigest()


def create_sccs_directory_layout():
    """Create the full SCCS directory structure inside the repo path."""

    repo_path = get_document_repo_path()
    if not repo_path:
        print("Invalid file path")
        sys.exit(1)

    os.makedirs(repo_path, exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "objects"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "objects", "docx"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "objects", "html"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "objects", "view_html"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "branches"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "branches", "main"), exist_ok=True)
    os.makedirs(
        os.path.join(repo_path, ".sccs", "branches", "main", "history"), exist_ok=True
    )
    os.makedirs(
        os.path.join(repo_path, ".sccs", "branches", "main", "commit_file_hash"),
        exist_ok=True,
    )
    os.makedirs(os.path.join(repo_path, ".sccs", "commit_messages"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "config"), exist_ok=True)
    os.makedirs(os.path.join(repo_path, ".sccs", "current_branch"), exist_ok=True)


def move_document_to_repo_directory():
    """Move the source document into the repo directory."""

    shutil.move(get_entered_document_path(), get_document_repo_path())


def copy_document_to_objects_as_docx_and_html(sha_hash, html, styles=None):
    """Copy the document into objects as both .docx and .html."""

    if styles is None:
        styles = utils.default_html_styles

    repo_path = get_document_repo_path()
    doc_name = Path(get_entered_document_path()).name

    try:
        shutil.copy2(
            os.path.join(repo_path, doc_name),
            os.path.join(repo_path, ".sccs", "objects", "docx", f"{sha_hash}.docx"),
        )
    except Exception as e:
        print(f"Error copying document to objects: {e}")
        sys.exit(1)

    try:
        with open(
            os.path.join(repo_path, ".sccs", "objects", "html", f"{sha_hash}.html"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(styles + html)
    except Exception as e:
        print(f"Error writing HTML file: {e}")
        sys.exit(1)

    try:
        with open(
            os.path.join(
                repo_path, ".sccs", "objects", "view_html", f"{sha_hash}.html"
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write(utils.wrap_html(html))
    except Exception as e:
        print(f"Error writing view HTML file: {e}")
        sys.exit(1)


def get_current_iso_time():
    """Return the current time as an ISO 8601 string."""

    return datetime.now().isoformat()


def write_history_data(sha_hash, config_user_name, config_user_email):
    """Write the initial commit history JSON file."""

    history_data = {
        "history": {
            "initial_commit": f"{sha_hash}",
            "latest_commit": f"{sha_hash}",
            "latest_commit_number": 1,
            "commit_order": {"1": f"{sha_hash}"},
        },
        "log": {
            f"{sha_hash}": {
                "timestamp": get_current_iso_time(),
                "author": f"{config_user_name} <{config_user_email}>",
                "message": "initial commit (This is a default commit message for initial version)",
            }
        },
    }
    try:
        with open(
            os.path.join(
                get_document_repo_path(),
                ".sccs",
                "branches",
                "main",
                "history",
                "commit_history.json",
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(history_data, f, indent=4)
    except Exception as e:
        print(f"Error updating commit history file: {e}")
        sys.exit(1)


def write_commit_message_data(sha_hash):
    commit_message_data = {
        f"{sha_hash}": "initial commit (This is a default commit message for initial version)"
    }
    try:
        with open(
            os.path.join(
                get_document_repo_path(),
                ".sccs",
                "commit_messages",
                "commit_messages.json",
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_message_data, f, indent=4)
    except Exception as e:
        print(f"Error opening commit message data file: {e}")
        sys.exit(1)


def write_config_data(config_user_name, config_user_email):
    """Write the user config JSON file."""

    config_data = {"name": f"{config_user_name}", "email": f"{config_user_email}"}
    try:
        with open(
            os.path.join(get_document_repo_path(), ".sccs", "config", "config.json"),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error updating config data file: {e}")
        sys.exit(1)


def write_hashed_file_commit_data(sha_hash, hashed_file):
    """Write the initial commit file binary hash JSON file."""

    commit_file_hash_data = {f"{sha_hash}": hashed_file}
    try:
        with open(
            os.path.join(
                get_document_repo_path(),
                ".sccs",
                "branches",
                "main",
                "commit_file_hash",
                "commit_file_hash.json",
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(commit_file_hash_data, f, indent=4)
    except Exception as e:
        print(f"Error updating commit file hash data file: {e}")
        sys.exit(1)


def write_branch_data():
    """Write the initial branch tracking JSON file."""

    branches_data = {"current_branch": "main", "branches": ["main"]}
    try:
        with open(
            os.path.join(
                get_document_repo_path(),
                ".sccs",
                "current_branch",
                "current_branch.json",
            ),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(branches_data, f, indent=4)
    except Exception as e:
        print(f"Error opening branch data file: {e}")
        sys.exit(1)


def confirmation_message():
    """Print a confirmation message for successful SCCS initialization."""

    print("SCCS initialization complete.")


if __name__ == "__main__":
    check_if_arg_entered(get_entered_document_path())

    check_for_prev_init()

    check_file_requirements()

    config_user_name = ask_config_input("name")

    config_user_email = ask_config_input("email")

    current_iso_time = get_current_iso_time()

    sha_hash = create_commit_sha_hash(
        current_iso_time, config_user_name, config_user_email
    )

    create_sccs_directory_layout()

    document_as_html = utils.convert_docx_to_html(get_entered_document_path())

    move_document_to_repo_directory()

    copy_document_to_objects_as_docx_and_html(sha_hash, document_as_html)

    write_history_data(sha_hash, config_user_name, config_user_email)

    write_commit_message_data(sha_hash)

    write_config_data(config_user_name, config_user_email)

    current_branch_binary_hash = utils.hash_current_docx_binary(
        docx_path=os.path.join(
            get_document_repo_path(), Path(get_entered_document_path()).name
        )
    )

    write_hashed_file_commit_data(sha_hash, current_branch_binary_hash)

    write_branch_data()

    confirmation_message()
