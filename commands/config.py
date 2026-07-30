#!/usr/bin/env python3
"""Command to configure a SCCS repository's settings"""

import sys
from pathlib import Path

import exceptions
import utils
from repository_layout import RepositoryLayout
from constants_classes import ErrorWrappers, SCCSConstants
from urllib.parse import urlsplit, urljoin
import os

def validate_entered_value(constants: SCCSConstants, repo_name: str, key: str, value: str) -> None:
    """
    Resolve the entered remote URL to the correct format for storing in the config file
    by ensuring it starts with 'http://' or 'https://', does not end with a '/', and
    ends with '/repos/<repo-name>'.

    Return the resolved 'remote'.
    """

    key = key.strip().lower()

    if key not in constants.ACCEPTED_KEYS:
            raise exceptions.InvalidArgumentError(constants.INVALID_KEY_ERROR_MESSAGE.format(keys=", ".join(constants.ACCEPTED_KEYS)))
    
    if not value.strip():
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key))
    
    if not repo_name.strip():
        raise exceptions.EmptyArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field="repository name"))

    repo_name = utils.clean_directory_name(repo_name)

    if repo_name is None:
        raise exceptions.InvalidArgumentError(
            constants.INVALID_REPO_NAME_ERROR_MESSAGE
        )


def resolve_key_value(constants: SCCSConstants, repo_name: str, key: str, value: str) -> str | None:
    """Resolve the entered remote URL to the correct format for storing in the config file."""

    value = value.strip()

    if not value:
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key))
    
    if key == constants.REMOTE:
        url = value.rstrip(os.sep)
        url_parsed = urlsplit(url)

        if (
            url_parsed.scheme.lower() not in constants.ACCEPTED_SCHEMES
            or not url_parsed.netloc
            or url_parsed.query
            or url_parsed.fragment
        ):
            raise exceptions.InvalidArgumentError(
                constants.INVALID_URL_ERROR_MESSAGE
            )
        
        return urljoin(url, f"{constants.REPOS}{os.sep}{repo_name}")
    
    return value


def print_config_confirmation_message(constants: SCCSConstants, key: str, value: str) -> None:
    """Print a confirmation message after successfully setting the configuration."""

    print(constants.CONFIG_DIR_SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value))


def main(constants: SCCSConstants, Repo: RepositoryLayout, key: str, value: str) -> None:
    """Run functions for the <sccs config> command."""
    Repo.check_repository_layout()

    repo_name = Repo.repo_name
    
    validate_entered_value(constants, repo_name, key, value)

    value = resolve_key_value(constants, repo_name, key, value)

    Repo.write_key_to_config(key, value)

    print_config_confirmation_message(constants, key, value)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        Repository = RepositoryLayout(Path.cwd(), constants)
        error_wrappers = ErrorWrappers()
        main(constants, Repository, utils.entered_argument(2), utils.entered_argument(3))

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)