
import remote_sccs.serve as serve
import remote_sccs.help as help
from remote_sccs.constants_classes import RemoteSCCSConstants, RemoteErrorWrappers
import sys

import argparse

rc = RemoteSCCSConstants()
COMMANDS = {
    rc.SERVE_COMMAND_NAME: serve.main,
    rc.HELP_COMMAND_NAME: help.main
}

def create_argument_parser(rc: RemoteSCCSConstants) -> argparse.ArgumentParser:
    """
    Creates and returns a ArgumentParser object to parse Remote-SCCS commands and arguments.
    """

    parser = argparse.ArgumentParser(
        prog=rc.REMOTE_SCCS,
        description=rc.REMOTE_SCCS_DESCRIPTION
    )

    parser.add_argument(dest=rc.COMMAND_FIELD_NAME)

    return parser


def run_command(arguments: argparse.Namespace) -> None:
    """
    Run the specified Remote-SCCS command by using an ArgumentParser object and reading what 
    command was called.

    If and invalid command is provided, inform the user and run Remote-SCCS help.
    """

    if arguments.command not in COMMANDS:
        rc = RemoteSCCSConstants()
        print(
            rc.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=arguments.command)
        )
        help.main(rc)
        return

    rc = RemoteSCCSConstants()
    error_wrappers = RemoteErrorWrappers()
    COMMAND_ARGUMENTS = {
        rc.SERVE_COMMAND_NAME: lambda: [rc],
        rc.HELP_COMMAND_NAME: lambda: [rc]
    }
    try:
        COMMANDS[arguments.command](*COMMAND_ARGUMENTS[arguments.command]())
    
    except Exception as e:
        print(
            error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(
                type_name=type(e).__name__, e=e
            )
        )
        sys.exit(rc.UNEXPECTED_ERROR_EXIT_CODE)


def main() -> None:
    """
    Run the specified Remote-SCCS command by reading and parsing the entered arguments.
    
    If no arguments are provided, run Remote-SCCS help.
    """

    rc = RemoteSCCSConstants()

    if len(sys.argv) < rc.MINIMUM_ARGUMENTS:
        help.main(rc)
        return

    arguments = create_argument_parser(rc).parse_args()

    run_command(arguments)

