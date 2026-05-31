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


def print_help(messages):
    """Print help messages."""

    for item in messages:
        print(item)


if __name__ == "__main__":
    print_help(MESSAGES_TO_PRINT)
