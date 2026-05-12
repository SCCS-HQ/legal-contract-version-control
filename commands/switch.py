import hashlib
import json
import os
import shutil
import sys

import utils


def get_branch_to_switch():
    return sys.argv[2] if len(sys.argv) > 2 else None


def update_current_branch(branch, current_branch_path=None, cwd=None):
    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch_path is None:
        current_branch_path = utils.current_branch_path
    try:
        with open(current_branch_path, "r", encoding="utf-8", newline="\n") as f:
            current_branch = json.load(f)
            current_branch["current_branch"] = branch

        tmp_path = os.path.join(cwd, ".sccs", "current_branch", "tmp")

        with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(current_branch, f, indent=4)

        os.replace(
            tmp_path,
            os.path.join(cwd, ".sccs", "current_branch", "current_branch.json"),
        )

    except Exception as e:
        print(f"Error updating current branch information: {e}")
        sys.exit(1)


def check_branch_to_switch(branch_to_switch, branches):
    if not branch_to_switch or len(branch_to_switch) == 0:
        print("No branch specified. Please provide a branch name to switch to.")
        sys.exit(1)

    if branch_to_switch not in branches:
        print(f"Error: Branch '{branch_to_switch}' does not exist.")
        sys.exit(1)


def get_latest_commit_binary_hash(branch, latest_commit, cwd=None):
    if cwd is None:
        cwd = utils.working_directory_path
    try:
        with open(
            os.path.join(
                cwd,
                ".sccs",
                "branches",
                branch,
                "commit_file_hash",
                "commit_file_hash.json",
            ),
            "r",
            encoding="utf-8",
            newline="\n",
        ) as f:
            return json.load(f).get(latest_commit)
    except Exception as e:
        print(f"Error accessing commit file hash for branch '{branch}': {e}")
        sys.exit(1)


def check_for_changes(branch, latest_commit_binary_hash, current_document_hash):
    if not current_document_hash == latest_commit_binary_hash:
        print(
            f"Error: The current file has uncommitted changes on the current branch '{branch}'. Please commit your changes before switching branches."
        )
        sys.exit(1)


def sanitize_branch(branch_name):
    return utils.clean_directory_name(branch_name)


def get_latest_commit(branch, cwd=None):
    if cwd is None:
        cwd = utils.working_directory_path
    try:
        with open(
            os.path.join(
                cwd, ".sccs", "branches", branch, "history", "commit_history.json"
            ),
            "r",
            encoding="utf-8",
            newline="\n",
        ) as f:
            history = json.load(f)
            return history["history"]["latest_commit"]
    except Exception as e:
        print(f"Error reading commit history for branch '{branch}': {e}")
        sys.exit(1)


def check_commit(commit, cwd=None):
    if cwd is None:
        cwd = utils.working_directory_path
    if not os.path.isfile(
        os.path.join(cwd, ".sccs", "objects", "docx", f"{commit}.docx")
    ):
        print(f"Error: Commit object '{commit}' not found.")
        sys.exit(1)


def copy_commit_to_main(commit, cwd=None):
    if cwd is None:
        cwd = utils.working_directory_path
    try:
        shutil.copy2(
            os.path.join(cwd, ".sccs", "objects", "docx", f"{commit}.docx"),
            os.path.join(cwd, f"{os.path.basename(cwd)}.docx"),
        )
    except Exception as e:
        print(f"Error copying commit '{commit}' to main: {e}")
        sys.exit(1)


def print_confirmation(branch_to_switch):
    print(f"Successfully switched to branch '{branch_to_switch}'.")


if __name__ == "__main__":
    utils.check_sccs_layout()

    branches = utils.get_branch_data(key="branches")

    current_branch = utils.get_current_branch()

    latest_commit = get_latest_commit(current_branch)

    latest_commit_binary_hash = get_latest_commit_binary_hash(
        current_branch, latest_commit
    )

    current_document_hash = utils.hash_current_docx_binary()

    check_for_changes(current_branch, latest_commit_binary_hash, current_document_hash)

    branch_to_switch = get_branch_to_switch()

    check_branch_to_switch(branch_to_switch, branches)

    branch_to_switch = sanitize_branch(branch_to_switch)

    latest_commit_on_branch_to_switch = get_latest_commit(branch_to_switch)

    check_commit(latest_commit_on_branch_to_switch)

    copy_commit_to_main(latest_commit_on_branch_to_switch)

    update_current_branch(branch_to_switch)

    print_confirmation(branch_to_switch)
