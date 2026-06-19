#!/usr/bin/env python3
"""Command to configure a SCCS repository's settings"""

import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout
from urllib.parse import urlsplit, urljoin

REPOS = "repos"
REMOTE = "remote"
NAME = "name"
EMAIL = "email"
ACCEPTED_KEYS = (REMOTE, NAME, EMAIL)
ACCEPTED_SCHEMES = ("http", "https")
EMPTY_CONFIG_VALUE_ERROR_MESSAGE = (
    "Configuration value for the given key cannot be empty. Please provide a valid value."
)
INVALID_URL_ERROR_MESSAGE = (
    "Invalid remote URL provided. The URL must start with 'http://' or 'https://', and "
    "use the format 'http(s)://<host>/<base-path>'. Base path is optional."
)
INVALID_KEY_ERROR_MESSAGE = (
    "Invalid configuration key provided. Accepted keys are: {keys}."
)
INVALID_REPO_NAME_ERROR_MESSAGE = (
    "Invalid repository name. Repository names cannot be empty or contain only whitespace. "
)
SUCCESS_MESSAGE_TEMPLATE = "Configuration '{key}' set to '{value}' successfully.\n"


def strip_trailing_slash(value: str) -> str:
    """Remove any trailing slashes from the value."""

    return value.rstrip('/')


def validate_entered_value(repo_name: str, key: str, value: str, REPOS: str = REPOS, REMOTE: str = REMOTE, ACCEPTED_KEYS: tuple = ACCEPTED_KEYS, ACCEPTED_SCHEMES: tuple = ACCEPTED_SCHEMES, EMPTY_CONFIG_VALUE_ERROR_MESSAGE: str = EMPTY_CONFIG_VALUE_ERROR_MESSAGE, INVALID_URL_ERROR_MESSAGE: str = INVALID_URL_ERROR_MESSAGE, INVALID_KEY_ERROR_MESSAGE: str = INVALID_KEY_ERROR_MESSAGE) -> str:
    """
    Resolve the entered remote URL to the correct format for storing in the config file
    by ensuring it starts with 'http://' or 'https://', does not end with a '/', and
    ends with '/repos/<repo-name>'.

    Return the resolved 'remote'.
    """

    key = key.strip().lower()

    if key not in ACCEPTED_KEYS:
            raise exceptions.InvalidArgumentError(INVALID_KEY_ERROR_MESSAGE.format(keys=", ".join(ACCEPTED_KEYS)))
    
    if not value.strip():
        raise exceptions.InvalidArgumentError(EMPTY_CONFIG_VALUE_ERROR_MESSAGE)
    
    if not repo_name.strip():
        raise exceptions.InvalidArgumentError(
            "Repository name cannot be empty. Please ensure the repository is properly initialized with a valid name."
        )

    if (repo_name := utils.clean_directory_name(repo_name)) is None:
        raise exceptions.InvalidArgumentError(
            INVALID_REPO_NAME_ERROR_MESSAGE
        )

    if key == REMOTE:
        url = strip_trailing_slash(value)
        url_parsed = urlsplit(url)

        if (
            url_parsed.scheme.lower() not in ACCEPTED_SCHEMES
            or not url_parsed.netloc
            or url_parsed.query
            or url_parsed.fragment
        ):
            raise exceptions.InvalidArgumentError(
                INVALID_URL_ERROR_MESSAGE
            )
        
        return urljoin(url, f"{REPOS}/{repo_name}")
    
    return value


def print_confirmation_message(key: str, value: str, SUCCESS_MESSAGE_TEMPLATE: str = SUCCESS_MESSAGE_TEMPLATE) -> None:
    """Print a confirmation message after successfully setting the configuration."""

    print(SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value))


def main(Repo: RepositoryLayout, key: str | None = None, value: str | None = None) -> None:
    """Run functions for the <sccs config> command."""
    Repo.check_repository_layout()

    if key is None:
        key = utils.entered_arguement(2)
    if value is None:
        value = utils.entered_arguement(3)

    repo_name = Repo.repo_name

    value = validate_entered_value(repo_name, key, value)

    Repo.write_key_to_config(key, value)

    print_confirmation_message(key, value)


if __name__ == "__main__":
    try:
        Repository = RepositoryLayout(Path.cwd())
        main(Repository)

    except exceptions.SCCSException as e:
        print(f"An error occurred:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred:\n{type(e).__name__}: {e}\n")
        sys.exit(2)