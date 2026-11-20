import io
import re
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import requests
from avora import utils
from avora.constants_classes import AvoraConstants
from avora.exceptions import AvoraException


def print_clone_success_message(c: AvoraConstants, response: requests.Response) -> None:
    """
    Print the status code and a success message after a successful clone operation.
    """

    print(c.STATUS_CODE_MESSAGE_TEMPLATE.format(status_code=response.status_code))
    print(c.CLONE_SUCCESS_MESSAGE)


def repository_name_from_url(c: AvoraConstants, url: str) -> str:
    """
    Extracts the repository name from the provided URL by splitting the path and
    validating the last two parts of the path.

    Raises an AvoraException if the URL is invalid or does not contain a valid repository
    name.
    """

    path_parts = [i for i in urlsplit(url).path.split(c.PATH_SEPARATOR) if i]

    if not path_parts or not urlsplit(url).path.endswith(c.CLONE_ENDPOINT):
        raise AvoraException(c.INVALID_ENDING_ERROR_MESSAGE)

    if len(path_parts) < c.MINIMUM_PATH_PARTS:
        raise AvoraException(
            c.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE.format(
                field=c.REPOSITORY_NAME_FIELD_NAME
            )
        )

    return path_parts[c.REPOSITORY_NAME_PATH_INDEX]


def request_repository(c: AvoraConstants, url: str) -> requests.Response:
    """
    Sends a GET request to the specified URL with a timeout and returns the response.

    Raises an AvoraException if the request fails.
    """

    try:
        response = requests.get(url, timeout=c.HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        raise AvoraException(c.HTTP_REQUEST_ERROR_MESSAGE) from e

    return response


def unzip_repository_file(
    c: AvoraConstants, zip_buffer: io.BytesIO, url: str, staging_root: Path
) -> None:
    """
    Unzip the repository file from the provided zip buffer into the staging root
    directory.

    Raises an AvoraException if the repository name is invalid or if the extraction
    fails.
    """

    repository_name = repository_name_from_url(c, url)

    destination = Path(staging_root / repository_name)

    validate_repository_name(c, destination.name)

    with zipfile.ZipFile(zip_buffer, "r") as zf:
        for i in zf.namelist():
            utils.safe_extract_zip(c, zf, i, destination)


def validate_entered_url(c: AvoraConstants, url: str) -> None:
    """
    Validates the entered URL by checking if it is not empty, starts with an accepted
    scheme, and ends with the expected clone endpoint.

    Raises an AvoraException if the URL is invalid.
    """

    utils.raise_if_empty(c, url, c.URL_FIELD_NAME)

    if not any(url.startswith(i) for i in c.ACCEPTED_SCHEMES):
        raise AvoraException(c.INVALID_URL_ERROR_MESSAGE)

    if not url.endswith(c.CLONE_ENDPOINT):
        raise AvoraException(c.INVALID_ENDING_ERROR_MESSAGE)


def validate_repository_name(c: AvoraConstants, name: str) -> None:
    """
    Validate the entered repository name by checking that it contains only allowed
    characters and is not a single or double period. Raise an AvoraException if the
    repository name is invalid.
    """

    if not re.fullmatch(r"^[A-Za-z0-9._-]+$", name) or name in (
        c.SINGLE_PERIOD,
        c.DOUBLE_PERIOD,
    ):
        raise AvoraException(c.INVALID_REPOSITORY_NAME_ERROR_MESSAGE)


def main(c: AvoraConstants, url: str) -> None:
    """
    Run the clone command by validating the entered URL, requesting the repository from
    the remote URL, and extracting it into a staging directory.

    Promote the staging directory to the destination directory and print a success
    message when the operation completes.
    """

    validate_entered_url(c, url)

    response = request_repository(c, url)

    zip_buffer = io.BytesIO(response.content)

    repository_name = repository_name_from_url(c, url)

    validate_repository_name(c, repository_name)

    destination = Path.cwd() / repository_name

    if destination.exists():
        raise AvoraException(c.CLONE_DESTINATION_EXISTS_ERROR_MESSAGE)

    staging_root = utils.create_staging_directory(c, destination)

    repository_root = Path(staging_root / repository_name)

    try:
        unzip_repository_file(c, zip_buffer, url, staging_root)
        utils.promote_staging(c, repository_root, destination)
    except Exception:
        utils.cleanup_staging(staging_root)
        raise

    print_clone_success_message(c, response)