#!/usr/bin/env python3

import local_sccs.utils as utils
from local_sccs.constants_classes import SCCSConstants


def print_help(c: SCCSConstants) -> None:
    """
    Print the help messages listing the available SCCS commands and their descriptions.
    """

    for i in c.HELP_MESSAGES:
        print(i)


def main(c: SCCSConstants) -> None:
    """
    Run the help command by printing the help messages.
    """

    print_help(c)