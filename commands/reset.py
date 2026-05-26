#!/usr/bin/env python3
"""Delete all uncommitted changes."""

import shutil
import sys
from pathlib import Path
import exceptions
import utils
import json


def reset(cwd: Path | None = None) -> None:
    """Delete all uncommitted changes."""
    
    if cwd is None:
        cwd = utils.working_directory_path

    if not utils.check_for_uncommitted_changes("reset", False):
        raise exceptions.NoUncommittedChangesError()
        
    with open(cwd / ".sccs" / "branches" / utils.get_current_branch() / "history" / "commit_history.json") as f:
        data = json.load(f)
        latest_commit = data["history"]["latest_commit"]
        
    shutil.copy2(utils.validate_commit(folder="docx", commit=latest_commit), cwd / utils.current_file_docx_path)


def main() -> None:
    """Main function to handle the <reset> command."""
    utils.check_sccs_layout()
    reset()
    

if __name__ == "__main__":
    try:
        main()
    except exceptions.SCCSException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred:\n{e}\n")
        sys.exit(1)