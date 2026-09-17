#!/usr/bin/env python3

from pathlib import Path
from urllib.parse import urljoin, urlsplit

import src.local_sccs.exceptions as exceptions
import src.local_sccs.utils as utils
from src.local_sccs.constants_classes import SCCSConstants
from src.local_sccs.repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def print_config_success_message(c: SCCSConstants, key: str, value: str) -> None:
    """
    Print a success message after a successful configuration operation, including the
    key and value that were set."""

    print(c.CONFIG_SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value))


def resolve_key_value(
    c: SCCSConstants, repository_name: str, key: str, value: str
) -> str:
    """
    Resolve the value for the given key. If the key is 'remote', it ensures that the
    value is a valid URL and appends the required path ending for the repository. For
    other keys, it simply returns the value.

    If the key is 'remote' and validation fails, it raises an SCCSException with an
    appropriate error message.
    """

    if key == c.REMOTE_KEY:
        url = (
            value + c.PATH_SEPARATOR if not value.endswith(c.PATH_SEPARATOR) else value
        )
        parsed_url = urlsplit(url)

        if (
            parsed_url.scheme.lower() not in c.ACCEPTED_SCHEMES
            or not parsed_url.netloc
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise exceptions.SCCSException(c.INVALID_URL_ERROR_MESSAGE)

        required_path_ending = (
            c.REPOSITORIES_PATH_SEGMENT
            + c.PATH_SEPARATOR
            + repository_name
            + c.PATH_SEPARATOR
        )

        return (
            urljoin(url, required_path_ending)
            if not url.endswith(required_path_ending)
            else url
        )

    return value


def validate_entered_value(c: SCCSConstants, key: str, value: str) -> str:
    """
    Validates the entered key-value pair by checking if the key is accepted and if the
    value is not empty.

    Raises an SCCSException if the key or value is invalid.
    """

    if key not in c.ACCEPTED_CONFIG_KEYS:
        raise exceptions.SCCSException(c.INVALID_KEY_ERROR_MESSAGE)

    utils.raise_if_empty(c, value.strip(), key)

    return value.strip()


def main(
    c: SCCSConstants,
    key: str,
    value: str,
    rd: RepositoryData,
    ri: RepositoryIO,
    rp: RepositoryPaths,
    rs: RepositoryStatus,
    rw: RepositoryWrite,
) -> None:
    """
    Run the config command by setting the current branch as the target, validating the
    repository layout, and writing the entered key-value pair to the configuration of a
    copy of the repository in a staging directory.

    Promote the staging directory to the repository root, print a success message, and
    reset the target branch when the operation completes.
    """

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    resolved_value = resolve_key_value(
        c, rp.repository_name, key, validate_entered_value(c, key, value)
    )

    with utils.staged_repository(c, rp.root, rp.root, rd.root) as staging_root:
        staging_ri = RepositoryIO(staging_root, ri.repository_name, c, ri.target)
        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)

        staging_rw.write_key_to_config(key, resolved_value, staging_ri.read_config())

    print_config_success_message(c, key, value)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, c.FIRST_ARGUMENT_INDEX),
        utils.entered_argument(c, c.SECOND_ARGUMENT_INDEX),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryIO(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )
