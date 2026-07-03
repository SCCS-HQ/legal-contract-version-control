#!/usr/bin/env python3
"""Clone a hosted SCCS repository with a URL"""

import io
import sys
import zipfile

import exceptions
import requests
import utils
from urllib.parse import urlsplit
from constants_classes import SCCSConstants, ErrorWrappers

def resolve_entered_url(constants: SCCSConstants, url: str) -> str:
    """
    Resolve the entered URL by adding 'https://' if missing and appending '/clone'
    if missing.

    Return 'url' so it begins with 'https://' and ends with '/clone/'.
    """

    if not url :
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.URL_FIELD_NAME))

    if not any(url.startswith(i) for i in constants.ACCEPTED_SCHEMES):
        raise exceptions.InvalidArgumentError(constants.INVALID_URL_ERROR_MESSAGE)

    if not url.endswith(constants.CLONE_ENDPOINT):
       raise exceptions.InvalidArgumentError(constants.INVALID_ENDING_ERROR_MESSAGE)

    return url


def request_repo(constants: SCCSConstants, url: str, timeout: int) -> requests.Response:
    """
    Make a GET request to 'url' and ensure that the request was successful.

    Return the server response after making a get request to 'url'.
    """

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise exceptions.HTTPGetRequestError(
            constants.HTTP_REQUEST_ERROR_MESSAGE
        ) from e
    
    return response


def unzip_repo_file(constants: SCCSConstants, buffer: io.BytesIO, url: str) -> None:
    """Unzip 'buffer'."""

    path_parts = [p for p in urlsplit(url).path.split("/") if p]

    if not path_parts or path_parts[-1] != constants.CLONE_ENDPOINT:
        raise exceptions.InvalidArgumentError(constants.INVALID_ENDING_ERROR_MESSAGE)
    
    if len(path_parts) < 2:
        raise exceptions.InvalidArgumentError(constants.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(field=constants.REPOSITORY_NAME_FIELD_NAME))
    
    repo_name = path_parts[-2]

    try:
        zipfile.ZipFile(buffer, constants.ZIP_READ_MODE).extractall(repo_name)
    except Exception as e:
        raise exceptions.ZippingFileError(constants.UNZIP_FAILED_ERROR_MESSAGE) from e


def print_clone_success_message(constants: SCCSConstants, response: requests.Response) -> None:
    """Print a success message after cloning the repository."""

    print(constants.STATUS_CODE_MESSAGE + str(response.status_code))
    print(constants.CLONE_SUCCESS_MESSAGE)


def main(constants: SCCSConstants, url: str) -> None:
    """Run functions for the <sccs clone> command."""

    url = resolve_entered_url(constants, url)

    response = request_repo(constants, url, constants.HTTP_TIMEOUT_SECONDS)

    buffer = io.BytesIO(response.content)

    unzip_repo_file(constants, buffer, url)

    print_clone_success_message(constants, response)


if __name__ == "__main__":
    try:
        constants = SCCSConstants()
        error_wrappers = ErrorWrappers()
        main(constants, utils.entered_argument(2))

    except exceptions.SCCSException as e:
        print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
        sys.exit(1)

    except Exception as e:
        print(error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(type_name=type(e).__name__, e=e))
        sys.exit(2)
