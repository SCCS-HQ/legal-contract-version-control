import json
import os
import shutil
import sys

import utils


def get_entered_subcommand():
    """Retrieve the subcommand entered by the user."""

    return sys.argv[2] if len(sys.argv) > 2 else None


def get_entered_branch_name():
    """Retrieve the branch name entered by the user."""

    return sys.argv[3] if len(sys.argv) > 3 else None


def validate_subcommand(subcommand, branch_name):
    """Validate the subcommand entered by the user."""

    if not subcommand:
        print(
            "No subcommand provided. Please use 'create', 'delete', or 'list' along "
            "with required arguments."
        )
        sys.exit(1)

    if subcommand not in ["create", "delete", "list"]:
        print(f"Unknown subcommand: {subcommand}")
        print(
            "Invalid subcommand. Please use 'create', 'delete', or 'list' along with "
            "required arguments."
        )
        sys.exit(1)

    if subcommand in ["create", "delete"]:
        if not branch_name:
            print("No branch name provided. Please specify a branch name.")
            sys.exit(1)


def branch_create_subcommand(
    current_branch, branch_data, cwd=None, current_branch_path=None
):
    """Create a new branch from the current branch."""

    if cwd is None:
        cwd = utils.working_directory_path

    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    sanitized_branch_name = utils.clean_directory_name(get_entered_branch_name())

    if not sanitized_branch_name:
        print("Invalid branch name. Please provide a valid branch name.")
        sys.exit(1)

    if sanitized_branch_name in branch_data["branches"]:
        print(f"Branch '{sanitized_branch_name}' already exists.")
        sys.exit(1)

    if os.path.isdir(os.path.join(cwd, ".sccs", "branches", sanitized_branch_name)):
        print(
            f"Branch '{sanitized_branch_name}' already exists, or a directory with the "
            f"same name exists."
        )
        sys.exit(1)

    shutil.copytree(
        os.path.join(cwd, ".sccs", "branches", current_branch),
        os.path.join(cwd, ".sccs", "branches", sanitized_branch_name),
    )

    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as current_branch_file:
            branch_data["branches"].append(sanitized_branch_name)
            branch_data["current_branch"] = sanitized_branch_name
            json.dump(branch_data, current_branch_file, indent=4)

    except Exception as e:
        print(f"Error creating branch '{sanitized_branch_name}': {e}")
        sys.exit(1)

    print(
        f"Branch '{sanitized_branch_name}' was created from branch '{current_branch}', "
        f"and is now the current branch."
    )


def branch_delete_subcommand(
    current_branch, branch_data, cwd=None, current_branch_path=None
):
    """Delete an existing branch."""

    if cwd is None:
        cwd = utils.working_directory_path
    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    sanitized_branch_name = utils.clean_directory_name(get_entered_branch_name())

    branch_path = os.path.join(cwd, ".sccs", "branches", sanitized_branch_name)

    if sanitized_branch_name == current_branch:
        print("Cannot delete the current branch.")
        sys.exit(1)

    if not os.path.exists(branch_path):
        print(f"Branch '{sanitized_branch_name}' does not exist.")
        sys.exit(1)

    if not sanitized_branch_name in branch_data["branches"]:
        print(f"Branch '{sanitized_branch_name}' does not exist in branch data.")
        sys.exit(1)

    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as current_branch_file:
            branch_data["branches"].remove(sanitized_branch_name)
            json.dump(branch_data, current_branch_file, indent=4)

    except Exception as e:
        print(f"Error updating branch data: {e}")
        sys.exit(1)

    try:
        shutil.rmtree(branch_path)

    except Exception as e:
        print(f"Error deleting branch '{sanitized_branch_name}': {e}")
        rollback_changes_after_failure(current_branch_path, branch_data=branch_data)

    print(f"Branch '{sanitized_branch_name}' was deleted.")


def rollback_changes_after_failure(current_branch_path, branch_data=None):
    """Rollback changes after a failed branch deletion."""

    if current_branch_path is None:
        current_branch_path = utils.current_branch_path

    if branch_data is None:
        branch_data = utils.get_branch_data()

    sanitized_branch_name = utils.clean_directory_name(get_entered_branch_name())
    try:
        with open(
            current_branch_path, "w", encoding="utf-8", newline="\n"
        ) as current_branch_file:
            branch_data["branches"].append(sanitized_branch_name)
            json.dump(branch_data, current_branch_file, indent=4)

    except Exception as e:
        print(
            f"Error updating branch data after failed deletion: {e}\nThe branch '"
            f"{sanitized_branch_name}' may be in an inconsistent state."
        )
        sys.exit(1)


def branch_list_subcommand(current_branch, branch_data):
    """List all branches."""

    print("Branches:")
    for branch in branch_data.get("branches", []):
        if branch == current_branch:
            print(f"* {branch} (current)")
        else:
            print(f"  {branch}")


def run_specified_subcommand(subcommand, current_branch, branch_data):
    """Run the specified subcommand."""

    if subcommand == "create":
        branch_create_subcommand(current_branch, branch_data)
    elif subcommand == "delete":
        branch_delete_subcommand(current_branch, branch_data)
    elif subcommand == "list":
        branch_list_subcommand(current_branch, branch_data)


if __name__ == "__main__":

    utils.check_sccs_layout()

    validate_subcommand(get_entered_subcommand(), get_entered_branch_name())

    run_specified_subcommand(
        get_entered_subcommand(), utils.get_current_branch(), utils.get_branch_data()
    )
