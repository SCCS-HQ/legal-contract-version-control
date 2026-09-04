#!/usr/bin/env python3


import shutil
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import exceptions
import utils
from constants_classes import SCCSConstants
from repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)


def validate_entered_value(c: SCCSConstants, key: str, value: str) -> str:

    if key not in c.ACCEPTED_CONFIG_KEYS:
        raise exceptions.SCCSException(c.INVALID_KEY_ERROR_MESSAGE)

    if not value.strip():
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=key)
        )

    return value.strip()


def resolve_key_value(
    c: SCCSConstants, repository_name: str, key: str, value: str
) -> str:

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


def print_config_success_message(c: SCCSConstants, key: str, value: str) -> None:

    print(c.CONFIG_SUCCESS_MESSAGE_TEMPLATE.format(key=key, value=value))


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

    rs.target.set(rd.current_branch())

    rs.validate_repository_layout()

    resolved_value = resolve_key_value(
        c, rp.repository_name, key, validate_entered_value(c, key, value)
    )

    staging_root = utils.create_staging_directory(c, rp.root)

    try:
        shutil.copytree(rd.root, staging_root, dirs_exist_ok=True)

        staging_ri = RepositoryIO(staging_root, ri.repository_name, c, ri.target)
        staging_rw = RepositoryWrite(staging_root, rw.repository_name, c, rw.target)

        staging_rw.write_key_to_config(key, resolved_value, staging_ri.read_config())
        utils.promote_staging(staging_root, rp.root)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_config_success_message(c, key, value)

    rs.target.reset()


if __name__ == "__main__":
    c = SCCSConstants()
    target = TargetBranch(c)
    repository_name = Path.cwd().name
    utils.run_command(
        main,
        utils.entered_argument(c, 2),
        utils.entered_argument(c, 3),
        RepositoryData(Path.cwd(), repository_name, c, target),
        RepositoryIO(Path.cwd(), repository_name, c, target),
        RepositoryPaths(Path.cwd(), repository_name, c, target),
        RepositoryStatus(Path.cwd(), repository_name, c, target),
        RepositoryWrite(Path.cwd(), repository_name, c, target),
    )
