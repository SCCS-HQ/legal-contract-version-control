#!/usr/bin/env python3

from remote_sccs.constants_classes import RemoteSCCSConstants


def print_help(rc: RemoteSCCSConstants) -> None:
    """
    Print the help messages listing the available SCCS commands and their descriptions.
    """

    for i in rc.HELP_MESSAGES:
        print(i)


def main(rc: RemoteSCCSConstants) -> None:
    """
    Run the help command by printing the help messages.
    """

    print_help(rc)