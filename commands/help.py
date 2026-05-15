#!/usr/bin/env python3
"""Print a list of all available commands."""

import sys

import exceptions

MESSAGES_TO_PRINT = [
    "SCCS Help",
    "Available commands:",
    "  init    - Initialize a new SCCS repository",
    "  commit  - Commit changes to a repository",
    "  open    - Restore a previous commit and overwrite the current changes",
    "  log     - Show commit history",
    "  diff    - Compare the current .docx converted to HTML with a specified commit "
    "HTML file",
    "  status  - Show the status of a repository",
    "  branch  - List, create, and delete branches",
    "  switch  - Switch to a different branch",
    "  help    - Show this help message",
]


def print_help(messages: list[str]) -> None:
    """Print help messages."""

    for item in messages:
        print(item)


def main() -> None:
    """Run functions for the <sccs help> command."""

    print_help(MESSAGES_TO_PRINT)


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
