#!/usr/bin/env python3
"""Command to configure a SCCS repository's settings"""


from pathlib import Path

import exceptions
import utils
from repository_layout import (
    RepositoryPaths,
    RepositoryData,
    RepositoryWrite,
    RepositoryStatus,
    TargetBranch,
)
from constants_classes import SCCSConstants
from urllib.parse import urlsplit, urljoin


def validate_entered_value(c: SCCSConstants, repo_name: str, key: str, value: str) -> None:
    """
    Resolve the entered remote URL to the correct format for storing in the config file
    by ensuring it starts with 'http://' or 'https://', does not end with a '/', and
    ends with '/repos/<repo-name>'.

    Return the resolved 'remote'.
    """

    if key not in c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.InvalidArgumentError(c.INVALID_KEY_ERROR_MESSAGE)

    if not value:
        raise exceptions.InvalidArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key))

    if not repo_name:
        raise exceptions.EmptyArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.REPOSITORY_NAME_FIELD_NAME))

    repo_name = utils.clean_directory_name(repo_name)

    if repo_name is None:
        raise exceptions.InvalidArgumentError(
            c.INVALID_REPO_NAME_ERROR_MESSAGE
        )


def resolve_key_value(c: SCCSConstants, repo_name: str, key: str, value: str) -> str:
    """Resolve the entered remote URL to the correct format for storing in the config file."""

    if not value:
        raise exceptions.InvalidArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key))

    if key == c.REMOTE_KEY:
        url = value.rstrip(c.PATH_SEPARATOR)
        url_parsed = urlsplit(url)

        if (
            url_parsed.scheme.lower() not in c.ACCEPTED_SCHEMES
            or not url_parsed.netloc
            or url_parsed.query
            or url_parsed.fragment
        ):
            raise exceptions.InvalidArgumentError(
                c.INVALID_URL_ERROR_MESSAGE
            )

        return urljoin(url, c.REPOS_PATH_SEGMENT + c.PATH_SEPARATOR + repo_name)

    return value


def print_config_confirmation_message(c: SCCSConstants, key: str, value: str) -> None:
    """Print a confirmation message after successfully setting the configuration."""

    print(c.CONFIG_SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value))


def main(c: SCCSConstants, key: str, value: str, rp: RepositoryPaths, rd: RepositoryData, rs: RepositoryStatus, rw: RepositoryWrite) -> None:
    """Run functions for the <sccs config> command."""
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    repo_name = rp.repo_name

    validate_entered_value(c, repo_name, key, value)

    value = resolve_key_value(c, repo_name, key, value)

    rw.write_key_to_config(key, value)

    print_config_confirmation_message(c, key, value)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    utils.run_command(
        main,
        utils.entered_argument(2),
        utils.entered_argument(3),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target),
    )
