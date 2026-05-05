from sccs_layout_check import check_sccs, directory_path, sanitize_dirname, path
import hashlib
import sys
import os
import json
import shutil
check_sccs()

branch_to_switch = sys.argv[2] if len(sys.argv) > 2 else None

def update_current_branch(branch):
    try:
        with open(os.path.join(directory_path, ".sccs", "current_branch", "current_branch.json"), "r", encoding="utf-8", newline="\n") as f:
            try:
                current_branch = json.load(f)
                current_branch["current_branch"] = branch
            except Exception as e:
                print(f"Error reading or updating current branch information: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error accessing current branch information: {e}")
        sys.exit(1)

    try: 
        with open(os.path.join("tmp"), "w", encoding="utf-8", newline="\n") as f:
            try:
                json.dump(current_branch, f, indent=4)
            except Exception as e:
                print(f"Error updating current branch information: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error accessing current branch information: {e}")
        sys.exit(1)
    
    try: 
        os.replace("tmp", os.path.join(directory_path, ".sccs", "current_branch", "current_branch.json"))
    except Exception as e:
        print(f"Error replacing current branch information: {e}")
        sys.exit(1)

def get_branch_data():
    try:
        with open(os.path.join(directory_path, ".sccs", "current_branch", "current_branch.json"), "r", encoding="utf-8", newline="\n") as f:
            try:
                data = json.load(f)
                return data.get("current_branch"), data.get("branches")
            except Exception as e:
                print(f"Error reading current branch information: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error accessing current branch information: {e}")
        sys.exit(1)

def check_branch_to_switch(branch_to_switch, branches):
    if not branch_to_switch or len(branch_to_switch) == 0:
        print("No branch specified. Please provide a branch name to switch to.")
        sys.exit(1)

    if branch_to_switch not in branches:
        print(f"Error: Branch '{branch_to_switch}' does not exist.")
        sys.exit(1)

def get_latest_commit_binary_hash(branch, latest_commit):
    try:
        with open(os.path.join(directory_path, ".sccs", "branches", branch, "commit_file_hash", "commit_file_hash.json"), "r", encoding="utf-8", newline="\n") as f:
            try:
                return json.load(f).get(latest_commit)
            except Exception as e:
                print(f"Error reading commit file hash for branch '{branch}': {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error accessing commit file hash for branch '{branch}': {e}")
        sys.exit(1)

def hash_current_document():
    try:
        with open(path, "rb") as f:
            hasher = hashlib.sha256()
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
            return hasher.hexdigest()
    except Exception as e:
        print(f"Error processing .docx file: {e}")
        sys.exit(1)

def check_for_changes(branch, latest_commit_binary_hash, current_document_hash):
    if not current_document_hash == latest_commit_binary_hash:
        print(f"Error: The current file has uncommitted changes on the current branch '{branch}'. Please commit your changes before switching branches." )
        sys.exit(1)

def sanitize_branch(branch_name):
    return sanitize_dirname(branch_name)

def get_latest_commit(branch):
    try:
        with open(os.path.join(directory_path, ".sccs",  "branches", branch, "history", "commit_history.json"), "r", encoding="utf-8", newline="\n") as f:
            try:
                history = json.load(f)
                try:
                    return history["history"]["latest_commit"]
                except KeyError as e:
                    print(f"Error: Missing key {e} in commit history for branch '{branch}'.")
                    sys.exit(1)
            except Exception as e:
                print(f"Error parsing commit history for branch '{branch}': {e}")
                sys.exit(1)
    except Exception as e: 
        print(f"Error reading commit history for branch '{branch}': {e}")
        sys.exit(1)

def check_commit(commit):
    if not os.path.isfile(os.path.join(directory_path, ".sccs", "objects", "docx", f"{commit}.docx")):
        print(f"Error: Commit object '{commit}' not found.")
        sys.exit(1)

def copy_commit_to_main(commit):
    try:
        shutil.copy2(os.path.join(directory_path, ".sccs", "objects", "docx", f"{commit}.docx"), os.path.join(directory_path, f"{os.path.basename(directory_path)}.docx"))
    except Exception as e:
        print(f"Error copying commit '{commit}' to main: {e}")
        sys.exit(1)

def print_confirmation(branch_to_switch):
    print(f"Successfully switched to branch '{branch_to_switch}'.")

if __name__ == "__main__":
    branch, branches = get_branch_data()

    latest_commit = get_latest_commit(branch)

    latest_commit_binary_hash = get_latest_commit_binary_hash(branch, latest_commit)

    current_document_hash = hash_current_document()

    check_for_changes(branch, latest_commit_binary_hash, current_document_hash)

    check_branch_to_switch(branch_to_switch, branches)

    branch_to_switch = sanitize_branch(branch_to_switch)

    latest_commit_on_branch_to_switch = get_latest_commit(branch_to_switch)

    check_commit(latest_commit_on_branch_to_switch)

    copy_commit_to_main(latest_commit_on_branch_to_switch)

    update_current_branch(branch_to_switch)

    print_confirmation(branch_to_switch)