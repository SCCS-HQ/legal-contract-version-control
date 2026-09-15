#!/usr/bin/env python3

import utils
from constants_classes import SCCSConstants


def main(c: SCCSConstants) -> None:
    """
    Run the help command by printing the help messages.
    """

    print_help(c)

def print_help(c: SCCSConstants) -> None:
    """
    Print the help messages listing the available SCCS commands and their descriptions.
    """

    for i in c.HELP_MESSAGES:
        print(i)


if __name__ == "__main__":
    utils.run_command(
        main,
    )
