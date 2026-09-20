
from remote_sccs.main import app
from remote_sccs import serve 
from remote_sccs.constants_classes import RemoteSCCSConstants, RemoteErrorWrappers
import sys

import argparse

rc = RemoteSCCSConstants
COMMANDS = {
    rc.SERVE_COMMAND_NAME: serve.main
}

def create_argument_parser(rc: RemoteSCCSConstants) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=rc.REMOTE_SCCS,
        description=rc.REMOTE_SCCS_DESCRIPTION
    )

    parser.add_argument(dest=rc.COMMAND_FIELD_NAME, required=True)

    return parser


def run_command(arguments: argparse.Namespace) -> None:
    rc = RemoteSCCSConstants
    error_wrappers = RemoteErrorWrappers()
    COMMAND_ARGUMENTS = {
        rc.SERVE_COMMAND_NAME: lambda: [rc]
    }
    try:
        COMMANDS[arguments.command](*COMMAND_ARGUMENTS[arguments.command]())
    except Exception as e:
        error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(
            type_name=type(e).__name__, e=e
        )
        sys.exit(rc.UNEXPECTED_ERROR_EXIT_CODE)

def main(rc: RemoteSCCSConstants) -> None:
    if len(sys.argv) < 2:
        return

    arguments = create_argument_parser(rc).parse_args()

    run_command(arguments)

if __name__ == "__main__":
    rc = RemoteSCCSConstants()
    main(rc)