#!/usr/bin/env python3
"""Command to configure a SCCS repository's settings"""

import sys

import exceptions
import utils


def get_entered_config_key() -> str | None:
    """Retrieve the key entered by the user."""
    key = sys.argv[2] if len(sys.argv) > 2 else None
    if key is None:
        raise exceptions.InvalidArgumentError(
            "No key provided. Please provide a key to configure: 'remote', 'name', or "
            "'email'."
        )

    if key not in ["remote", "name", "email"]:
        raise exceptions.InvalidArgumentError(
            "Invalid key provided. Please provide a valid key to configure: 'remote', "
            "'name', or 'email'."
        )
    return key


def get_entered_config_value() -> str | None:
    """Retrieve the value entered by the user."""
    value = sys.argv[3] if len(sys.argv) > 3 else None
    if value is None:
        raise exceptions.InvalidArgumentError(
            "No value provided. Please provide a value to configure."
        )
    return value


def resolve_entered_remote(remote: str) -> str:
    """
    Resolve the entered remote URL to the correct format for storing in the config file
    by ensuring it starts with 'http://' or 'https://', does not end with a '/', and
    ends with '/repos/<repo-name>'."""

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
    key = get_entered_config_key()
    value = get_entered_config_value()

    if key == "remote":
        value = resolve_entered_remote(value)

    utils.write_key_to_config(key, value)

    print(f"Configuration '{key}' set to '{value}' successfully.")


if __name__ == "__main__":
    try:
        main()

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n\n{type(e).__name__}: {e}\n")
        sys.exit(2)
