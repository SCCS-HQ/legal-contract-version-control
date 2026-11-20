import logging
import socket
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles
from remote_avora.constants_classes import RemoteAvoraConstants
from remote_avora.exceptions import RemoteAvoraException
from remote_avora.main import app

logger = logging.getLogger(__name__)


def create_repositories_directory(rc: RemoteAvoraConstants) -> None:
    """
    Create the /repos directory inside the current working directory, which is required
    to start the FastAPI application.
    """

    try:
        Path(rc.REPOSITORIES_BASE_DIRECTORY).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.debug("Failed to create repositories directory: %s", e)
        raise RemoteAvoraException(
            rc.REPOSITORIES_DIRECTORY_CREATION_ERROR_MESSAGE
        ) from e


def print_avora_server_startup(rc: RemoteAvoraConstants) -> None:
    """
    Print a message telling the user the Remote-Avora Server will be running on their
    computer's private IP address, and create a network socket to retrieve the user's
    private IP address.

    Print a message telling the user their server is starting.
    """

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((rc.PUBLIC_IP_ADDRESS, rc.PORT_80))
        ip_address = sock.getsockname()[rc.FIRST_ITEM_INDEX]
        sock.close()
    except OSError as e:
        logger.debug("Failed to retrieve IP address: %s", e)
        raise RemoteAvoraException(rc.IP_RETRIEVAL_ERROR_MESSAGE) from e

    print(rc.AVORA_SERVER_IP_MESSAGE.format(ip_address=ip_address))
    print(rc.STARTING_UVICORN_SERVER_MESSAGE)


def main(rc: RemoteAvoraConstants) -> None:
    """
    Print informational messages and start the Remote-Avora Server.
    """

    create_repositories_directory(rc)
    print_avora_server_startup(rc)

    app.mount(
        rc.REPOS_MOUNT_ENDPOINT,
        StaticFiles(directory=rc.REPOSITORIES_BASE_DIRECTORY),
        name=rc.STATIC_FILES_NAME,
    )

    uvicorn.run(app, host=rc.NETWORK_IP, port=rc.PORT_8000)