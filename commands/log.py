import json
import os
import sys
from pathlib import Path

import utils


def get_log_data(cwd=None, current_branch=None):
    """Retrieve the commit log data from the history JSON file."""

    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch is None:
        current_branch = utils.get_current_branch()

    # Get JSON log data
    log_path = os.path.join(
        cwd, ".sccs", "branches", current_branch, "history", "commit_history.json"
    )

    if not Path(log_path).is_file():
        print(
            "Log file not found. Please make sure the file has been initialized with "
            "'sccs init <file_path>'"
        )
        sys.exit(1)

    with open(log_path, "r", encoding="utf-8", newline="\n") as log_file:
        log_data = json.load(log_file)
    return log_data


def print_log():
    """Print the commit log to the console."""

    log_data = get_log_data()
    for entry in log_data["log"]:
        print(
            "------------------------------\n"
            f"Commit File: {entry}\n"
            f"Author: {log_data['log'][entry]['author']}\n"
            f"Date: {log_data['log'][entry]['timestamp']}\n"
            f"Message: {log_data['log'][entry]['message']}\n"
            "------------------------------"
        )


if __name__ == "__main__":

    utils.check_sccs_layout()

    print_log()
