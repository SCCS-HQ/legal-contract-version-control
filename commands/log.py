import json
from pathlib import Path
import os
import sys
import utils

CURRENT_BRANCH_PATH = os.path.join(utils.working_directory_path, ".sccs", "current_branch", "current_branch.json")



def get_current_branch():
    with open(CURRENT_BRANCH_PATH, "r", encoding="utf-8", newline="\n") as current_branch_file:
        current_branch = json.load(current_branch_file).get("current_branch")
    return current_branch

def get_log_data():
    # Get JSON log data
    log_path = os.path.join(utils.working_directory_path, ".sccs", "branches", get_current_branch(), "history", "commit_history.json")
    if not Path(log_path).is_file():
        print("Log file not found. Please make sure the file has been initialized with SCCS.")
        sys.exit(1)

    with open(log_path, "r", encoding="utf-8", newline="\n") as log_file:
        log_data = json.load(log_file)
    return log_data

def print_log():
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