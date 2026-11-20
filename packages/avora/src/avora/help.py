from avora.constants_classes import AvoraConstants


def print_help(c: AvoraConstants) -> None:
    """
    Print the help messages listing the available Avora commands and their descriptions.
    """

    for i in c.HELP_MESSAGES:
        print(i)


def main(c: AvoraConstants) -> None:
    """
    Run the help command by printing the help messages.
    """

    print_help(c)