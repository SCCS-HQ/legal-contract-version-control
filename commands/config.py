#!/usr/bin/env python3


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


def validate_entered_value(
    c: SCCSConstants, repo_name: str | None, key: str | None, value: str | None
) -> None:

    if key not in c.ACCEPTED_CONFIG_KEYS:
            raise exceptions.InvalidArgumentError(c.INVALID_KEY_ERROR_MESSAGE)

    if not value:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
        )

    if not repo_name:
        raise exceptions.EmptyArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=c.REPOSITORY_NAME_FIELD_NAME
            )
        )

    repo_name = utils.clean_directory_name(repo_name)


def resolve_key_value(
    c: SCCSConstants, repo_name: str, key: str | None, value: str | None
) -> str:

    if not value:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
        )

    if key == c.REMOTE_KEY:
        url = value + c.PATH_SEPARATOR if not value.endswith(c.PATH_SEPARATOR) else value
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

        required_path_ending = (
            c.REPOS_PATH_SEGMENT + c.PATH_SEPARATOR + repo_name + c.PATH_SEPARATOR
        )

        return urljoin(url, required_path_ending) if not url.endswith(required_path_ending) else url

    return value


def print_config_confirmation_message(c: SCCSConstants, key: str, value: str) -> None:

    print(c.CONFIG_SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value))


def main(
    c: SCCSConstants,
    key: str | None,
    value: str | None,
    rd: RepositoryData,
    rs: RepositoryStatus,
    rp: RepositoryPaths,
    rw: RepositoryWrite,
) -> None:
    rs.target.set(rd.current_branch())

    rs.check_repository_layout()

    repo_name = rp.repo_name

    assert key is not None
    assert value is not None

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
        RepositoryData(Path.cwd(), c, target),
        RepositoryStatus(Path.cwd(), c, target),
        RepositoryPaths(Path.cwd(), c, target),
        RepositoryWrite(Path.cwd(), c, target)
    )
