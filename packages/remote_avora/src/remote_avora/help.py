from remote_avora.constants_classes import RemoteAvoraConstants


def print_help(rc: RemoteAvoraConstants) -> None:
    """
    Print the help messages listing the available Remote-Avora commands and their descriptions.
    """

    for i in rc.HELP_MESSAGES:
        print(i)


def main(rc: RemoteAvoraConstants) -> None:
    """
    Run the help command by printing the help messages.
    """

    print_help(rc)