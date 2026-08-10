#!/usr/bin/env python3

import utils
from constants_classes import SCCSConstants
from repository_layout import (
    TargetBranch,
)


def print_help(c: SCCSConstants) -> None:

    for i in c.HELP_MESSAGES:
        print(i)


def main(c: SCCSConstants) -> None:
    print_help(c)


if __name__ == "__main__":
    utils.run_command(
        main,
    )
