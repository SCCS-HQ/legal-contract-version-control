#!/usr/bin/env python3
"""Command to configure a SCCS repository's settings"""

import sys

import exceptions
import utils


def resolve_entered_remote(remote: str) -> str:
    """
    Resolve the entered remote URL to the correct format for storing in the config file
    by ensuring it starts with 'http://' or 'https://', does not end with a '/', and
    ends with '/repos/<repo-name>'.

    Return the resolved 'remote'.
    """

    if not remote.startswith("http://") and not remote.startswith("https://"):
        raise exceptions.InvalidArgumentError(
            "Invalid remote URL provided. Please provide a valid URL starting with "
            "'http://' or 'https://'."
        )

    if remote.endswith("/"):
        remote = remote[:-1]

    for i in ["publish", "clone"]:
        if remote.endswith(i):
            raise exceptions.InvalidArgumentError(
                "Invalid remote URL provided. Please provide a valid URL. It cannot end"
                f" with '/{i}'."
            )

    if not remote.endswith("/repos"):
        remote += "/repos"

    remote += "/" + utils.working_directory_path.name

    return remote


def main() -> None:
    """Run functions for the <sccs config> command."""
    utils.check_sccs_layout()

    key = utils.entered_arguement(2)
    value = utils.entered_arguement(3)

    if key == "remote":
        value = resolve_entered_remote(value)

    utils.write_key_to_config(key, value)

    print(f"Configuration '{key}' set to '{value}' successfully.\n")


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)
