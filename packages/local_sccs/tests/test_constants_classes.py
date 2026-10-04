from local_sccs.constants_classes import SCCSConstants


def test_sccs_constants_help_messages_returns_correct_help_message(
    c: SCCSConstants
) -> None:

    assert c.HELP_MESSAGES == (
        "SCCS Help",
        "Available commands:",
        "  sccs branch - Create a new branch, delete, or list branches.",
        "  sccs clone - Clone a hosted SCCS repository with a URL.",
        "  sccs commit - Commit changes to the repository.",
        "  sccs config - Configure a repository's data value (remote, name, email)",
        "  sccs diff - Show differences between the current document and a past commit.",
        "  sccs help - Prints a help message listing the available commands and their descriptions.",
        "  sccs init - Initialize a new SCCS repository.",
        "  sccs log - Print a list of past commits for the current branch.",
        "  sccs merge - Merge the entered branch into the current branch.",
        "  sccs open - Open a commit file and update the current document.",
        "  sccs publish - Publish a local repository to a hosting service.",
        "  sccs pull - Pull changes from a remote repository and merge them into the local repository.",
        "  sccs push - Push changes from the local repository to a remote repository.",
        "  sccs reset - Delete all uncommitted changes.",
        "  sccs revert - Revert the current document to the specified commit.",
        "  sccs status - Check the status of the current document for uncommitted changes.",
        "  sccs switch - Switch between document branches.",
        "Available flags:",
        "  --debug, -d - Does not except Exception or SCCSException.",
    )