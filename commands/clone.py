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
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.URL_FIELD_NAME)
        )

    if not any(url.startswith(i) for i in c.ACCEPTED_SCHEMES):
        raise exceptions.InvalidArgumentError(c.INVALID_URL_ERROR_MESSAGE)

    if not url.endswith(c.CLONE_ENDPOINT):
        raise exceptions.InvalidArgumentError(c.INVALID_ENDING_ERROR_MESSAGE)

    return url


def request_repository(c: SCCSConstants, url: str, timeout: int) -> requests.Response:

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise exceptions.HTTPGetRequestError(c.HTTP_REQUEST_ERROR_MESSAGE) from e

    return response


def unzip_repository_file(c: SCCSConstants, zip_buffer: io.BytesIO, url: str) -> None:

    path_parts = [i for i in urlsplit(url).path.split(c.PATH_SEPARATOR) if i]

    if not path_parts or not urlsplit(url).path.endswith(c.CLONE_ENDPOINT):
        raise exceptions.InvalidArgumentError(c.INVALID_ENDING_ERROR_MESSAGE)

    if len(path_parts) < c.MINIMUM_PATH_PARTS:
        raise exceptions.InvalidArgumentError(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=c.REPOSITORY_NAME_FIELD_NAME
            )
        )

    destination = Path(os.path.abspath(path_parts[-2]))

    if not re.fullmatch(r"^[A-Za-z0-9._-]+$", destination.name) or destination.name in (
        ".",
        "..",
    ):
        raise exceptions.InvalidArgumentError(c.INVALID_REPOSITORY_NAME_ERROR_MESSAGE)

    try:
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            for i in zf.namelist():
                utils.safe_extract_zip(zf, i, destination)
    except exceptions.ZippingFileError:
        raise
    except Exception as e:
        raise exceptions.ZippingFileError(c.UNZIP_FAILED_ERROR_MESSAGE) from e


def print_clone_success_message(c: SCCSConstants, response: requests.Response) -> None:

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.CLONE_SUCCESS_MESSAGE)


def main(c: SCCSConstants, url: str | None) -> None:

    url = resolve_entered_url(c, url)

    response = request_repository(c, url, c.HTTP_TIMEOUT_SECONDS)

    zip_buffer = io.BytesIO(response.content)

    unzip_repository_file(c, zip_buffer, url)

    print_clone_success_message(c, response)


if __name__ == "__main__":
    utils.run_command(main, utils.entered_argument(2))
