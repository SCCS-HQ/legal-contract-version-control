#!/usr/bin/env python3
"""Clone a hosted SCCS repository with a URL"""

import io
import zipfile

import exceptions
import requests
import utils
from urllib.parse import urlsplit
from constants_classes import SCCSConstants

def resolve_entered_url(c: SCCSConstants, url: str) -> str:
    """
    Resolve the entered URL by adding 'https://' if missing and appending '/clone'
    if missing.

    Return 'url' so it begins with 'https://' and ends with '/clone/'.
    """

    if not url:
        raise exceptions.InvalidArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.URL_FIELD_NAME))

    if not any(url.startswith(i) for i in c.ACCEPTED_SCHEMES):
        raise exceptions.InvalidArgumentError(c.INVALID_URL_ERROR_MESSAGE)

    if not url.endswith(c.CLONE_ENDPOINT):
        raise exceptions.InvalidArgumentError(c.INVALID_ENDING_ERROR_MESSAGE)

    return url


def request_repo(c: SCCSConstants, url: str, timeout: int) -> requests.Response:
    """
    Make a GET request to url' and ensure that the request was successful.

    Return the server response after making a get request to 'url'.
    """

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise exceptions.HTTPGetRequestError(
            c.HTTP_REQUEST_ERROR_MESSAGE
        ) from e
    
    return response


def unzip_repo_file(c: SCCSConstants, buffer: io.BytesIO, url: str) -> None:
    """Unzip 'buffer'."""

    path_parts = [p for p in urlsplit(url).path.split(c.PATH_SEPARATOR) if p]

    if not path_parts or path_parts[-1] != c.CLONE_ENDPOINT:
        raise exceptions.InvalidArgumentError(c.INVALID_ENDING_ERROR_MESSAGE)
    
    if len(path_parts) < 2:
        raise exceptions.InvalidArgumentError(c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=c.REPOSITORY_NAME_FIELD_NAME))
    
    repo_name = path_parts[-2]

    try:
        zipfile.ZipFile(buffer, "r").extractall(repo_name)
    except Exception as e:
        raise exceptions.ZippingFileError(c.UNZIP_FAILED_ERROR_MESSAGE) from e


def print_clone_success_message(c: SCCSConstants, response: requests.Response) -> None:
    """Print a success message after cloning the repository."""

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.CLONE_SUCCESS_MESSAGE)


def main(c: SCCSConstants, url: str) -> None:
    """Run functions for the <sccs clone> command."""

    url = resolve_entered_url(c, url)

    response = request_repo(c, url, c.HTTP_TIMEOUT_SECONDS)

    buffer = io.BytesIO(response.content)

    unzip_repo_file(c, buffer, url)

    response.raise_for_status()

    print_clone_success_message(c, response)


if __name__ == "__main__":
    utils.run_command(main, utils.entered_argument(2))
