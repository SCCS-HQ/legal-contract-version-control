from remote_sccs.main import app
from remote_sccs import serve
import sys

import uvicorn
import argparse

COMMANDS = {
    "serve": serve.main
}

def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="remote_sccs",
        description="Remote API for Self-Hosting of SCCS"
    )

    parser.add_argument(dest="command", required=True)

    return parser


def run_command(arguments: argparse.Namespace) -> None:
    try:
        COMMANDS[arguments.command]()
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__}: {e}")
        sys.exit(2)

def main() -> None:


      
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()