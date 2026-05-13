import json
import os
import sys
from pathlib import Path

import exceptions
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
        raise FileNotFoundError(
            "History file not found. Please run 'sccs init <file_path>' to initialize "
            "SCCS for this file."
        )

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


def main():
    utils.check_sccs_layout()

    print_log()


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
else:
    raise exceptions.FileImportedAsModuleError(
        "This file cannot be run as a module. Please run it as a script."
    )
