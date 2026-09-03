#!/usr/bin/env python3

import io
import os
import re
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import exceptions
import requests
import utils
from constants_classes import SCCSConstants


def resolve_entered_url(c: SCCSConstants, url: str | None) -> str:

    if not url:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.URL_FIELD_NAME)
        )

    if not any(url.startswith(i) for i in c.ACCEPTED_SCHEMES):
        raise exceptions.SCCSException(c.INVALID_URL_ERROR_MESSAGE)

    if not url.endswith(c.CLONE_ENDPOINT):
        raise exceptions.SCCSException(c.INVALID_ENDING_ERROR_MESSAGE)

    return url


def request_repository(c: SCCSConstants, url: str, timeout: int) -> requests.Response:

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise exceptions.SCCSException(c.HTTP_REQUEST_ERROR_MESSAGE) from e

    return response


def unzip_repository_file(
        c: SCCSConstants, zip_buffer: io.BytesIO, url: str, destination: Path
    ) -> None:

    path_parts = [i for i in urlsplit(url).path.split(c.PATH_SEPARATOR) if i]

    if not path_parts or not urlsplit(url).path.endswith(c.CLONE_ENDPOINT):
        raise exceptions.SCCSException(c.INVALID_ENDING_ERROR_MESSAGE)

    if len(path_parts) < c.MINIMUM_PATH_PARTS:
        raise exceptions.SCCSException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=c.REPOSITORY_NAME_FIELD_NAME
            )
        )

    destination = Path(os.path.abspath(path_parts[-2]))

    if not re.fullmatch(r"^[A-Za-z0-9._-]+$", destination.name) or destination.name in (
        c.SINGLE_PERIOD, c.DOUBLE_PERIOD,
    ):
        raise exceptions.SCCSException(c.INVALID_REPOSITORY_NAME_ERROR_MESSAGE)

    with zipfile.ZipFile(zip_buffer, "r") as zf:
        for i in zf.namelist():
            utils.safe_extract_zip(c, zf, i, destination)



def print_clone_success_message(c: SCCSConstants, response: requests.Response) -> None:

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.CLONE_SUCCESS_MESSAGE)


def main(c: SCCSConstants, url: str | None) -> None:

    url = resolve_entered_url(c, url)

    response = request_repository(c, url, c.HTTP_TIMEOUT_SECONDS)

    zip_buffer = io.BytesIO(response.content)

    staging_root = utils.create_staging_directory(c, Path.cwd())

    try:
        unzip_repository_file(c, zip_buffer, url, staging_root)
        utils.promote_staging(staging_root, Path.cwd())
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_clone_success_message(c, response)


if __name__ == "__main__":
    c = SCCSConstants()
    utils.run_command(main, utils.entered_argument(c, 2))
