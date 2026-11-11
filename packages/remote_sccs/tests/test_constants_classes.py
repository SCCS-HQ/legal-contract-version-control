"""Snapshot tests for ``RemoteSCCSConstants`` and ``RemoteErrorWrappers``.

These tests use a golden-master / snapshot pattern to prevent constant drift
between the production constants classes and their expected values.
"""

import re
from types import FunctionType, MappingProxyType

import pytest
from remote_sccs.constants_classes import RemoteErrorWrappers, RemoteSCCSConstants
from test_constants import SCCSTestConstants

REMOTE_ERROR_WRAPPERS_SNAPSHOT: dict[str, object] = {
    "UNEXPECTED_ERROR_TEMPLATE": "An unexpected error occurred: {type_name}: {e}",
}

REMOTE_SCCS_CONSTANTS_SNAPSHOT: dict[str, object] = {
    "BRANCHES_DIRECTORY": "branches",
    "BYTES_PER_MEGABYTE": 1048576,
    "CLONE_ENDPOINT_TEMPLATE": "/repos/{repository_name}/clone",
    "HELP_COMMAND_NAME": "help",
    "SERVE_COMMAND_NAME": "serve",
    "COMMAND_DESCRIPTIONS": MappingProxyType(
        {
            "serve": (
                "Hosts a Remote-SCCS server on your computer anyone "
                "on your internet network can access."
            ),
            "help": (
                "Prints a help message listing the available commands "
                "and their descriptions."
            ),
        }
    ),
    "COMMAND_FIELD_NAME": "command",
    "CONTENT_DISPOSITION_HEADER_SPACED_TEMPLATE": (
        "attachment; filename={repository_name}.zip"
    ),
    "CONTENT_DISPOSITION_HEADER_TEMPLATE": "attachment;filename={repository_name}.zip",
    "CONTENT_DISPOSITION_HEADER_TITLE": "Content-Disposition",
    "CONTENT_TYPE_ZIP": "application/zip",
    "CURRENT_BRANCH_DICT_KEY": "current_branch",
    "DOUBLE_PERIOD": "..",
    "EASTER_EGG_MESSAGE": "Boo!",
    "FILE_PUBLISHED_MESSAGE": "File published successfully",
    "FILE_START_POSITION": 0,
    "FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE": "File {filename} is too large",
    "FIRST_ITEM_INDEX": 0,
    "HTTP_BAD_REQUEST_STATUS_CODE": 400,
    "HTTP_NOT_FOUND_STATUS_CODE": 404,
    "INVALID_JSON_ERROR_MESSAGE": "Invalid JSON data",
    "INVALID_REPOSITORY_NAME_ERROR_MESSAGE": "Invalid repository name",
    "INVALID_ZIP_PATH_ERROR_MESSAGE": "Invalid file path in zip",
    "IP_RETRIEVAL_ERROR_MESSAGE_TEMPLATE": "Error retrieving private IP address: {e}",
    "LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE": (
        "Local repository has objects that the remote does not have. "
        "Run 'sccs push' to upload these objects before pulling."
    ),
    "MAX_FILES_IN_ZIP": 1000,
    "MAX_INDIVIDUAL_FILE_SIZE": 10485760,
    "MAX_TOTAL_UPLOAD_SIZE": 104857600,
    "MESSAGE_DICT_KEY": "message",
    "METADATA_JSON": "metadata.json",
    "MINIMUM_ARGUMENTS": 2,
    "NETWORK_IP": "0.0.0.0",
    "NEWLINE": "\n",
    "OBJECTS_DICT_KEY": "objects",
    "OBJECTS_DIRECTORY": "objects",
    "OBJECTS_NOT_FOUND_ERROR_MESSAGE": "Repository objects not found",
    "OLD_ROOT_TEMPLATE": re.compile(r"\{repository_name\}\.old-[0-9a-f]{32}"),
    "PORT_80": 80,
    "PORT_8000": 8000,
    "PUBLIC_IP_ADDRESS": "8.8.8.8",
    "PUBLISH_ENDPOINT_TEMPLATE": "/repos/{repository_name}/publish",
    "PULL_ENDPOINT_TEMPLATE": "/repos/{repository_name}/pull",
    "PUSH_ENDPOINT_TEMPLATE": "/repos/{repository_name}/push",
    "PUSH_SUCCESS_MESSAGE": "Changes pushed successfully",
    "REMOTE_KEY": "remote",
    "REMOTE_SCCS": "remote_sccs",
    "REMOTE_SCCS_DESCRIPTION": "Remote API for Self-Hosting of SCCS",
    "REMOTE_URL_REQUIRED_ERROR_MESSAGE": "Remote URL is required",
    "REPOSITORIES_BASE_DIRECTORY": "./repos",
    "REPOSITORIES_DIRECTORY_CREATION_ERROR_MESSAGE_TEMPLATE": (
        "Error creating repositories directory: {e}"
    ),
    "REPOSITORY_EXISTS_ERROR_MESSAGE": "Repository already exists",
    "REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE": (
        "Repository name does not match file name"
    ),
    "REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE": (
        "Repository not found: {repository_name}"
    ),
    "REPOSITORY_URL_DICT_KEY": "repository_url",
    "REPOS_MOUNT_ENDPOINT": "/repos",
    "RGLOB_ALL_FILES_PATTERN": "*",
    "ROOT_ENDPOINT": "/",
    "SCCS_DIRECTORY": ".sccs",
    "SCCS_SERVER_IP_MESSAGE": (
        "Your Remote-SCCS server will be accessible on you internet "
        "network at http://{ip_address}:8000"
    ),
    "SINGLE_PERIOD": ".",
    "STARTING_UVICORN_SERVER_MESSAGE": "Starting Uvicorn Server...",
    "STATIC_FILES_NAME": "repos",
    "TEMPORARY_DIRECTORY_PREFIX": "sccs_temp_",
    "TOO_MANY_FILES_ERROR_MESSAGE": "Too many files in the uploaded zip",
    "UNEXPECTED_ERROR_EXIT_CODE": 2,
    "UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE": "Unknown command: {command}",
    "UPDATED_BRANCHES_DICT_KEY": "updated_branches",
    "UPLOAD_TOO_LARGE_ERROR_MESSAGE": "Uploaded file is too large",
    "UTF_8": "utf-8",
}


def test_remote_sccs_constants_help_messages_returns_correct_help_message(
    rc: RemoteSCCSConstants,
) -> None:
    """Verify the ``HELP_MESSAGES`` property returns the expected tuple."""

    assert rc.HELP_MESSAGES == (
        "Remote SCCS Help",
        "Available commands:",
        "  sccs help - Prints a help message listing the available commands and "
        "their descriptions.",
        "  sccs serve - Hosts a Remote-SCCS server on your computer anyone "
        "on your internet network can access.",
    )


@pytest.mark.parametrize(
    "module, constant_name, expected_value",
    [
        *[
            (RemoteSCCSConstants, name, value)
            for name, value in sorted(REMOTE_SCCS_CONSTANTS_SNAPSHOT.items())
        ],
        *[
            (RemoteErrorWrappers, name, value)
            for name, value in sorted(REMOTE_ERROR_WRAPPERS_SNAPSHOT.items())
        ],
    ],
)
def test_remote_sccs_constants_match_snapshot(
    module: type,
    constant_name: str,
    expected_value: object,
    tc: SCCSTestConstants,
) -> None:
    """Verify every snapshot constant exists on the class and matches its value."""

    try:
        actual_value = getattr(module, constant_name)
    except AttributeError:
        pytest.fail(
            tc.DELETED_CONSTANT_ERROR_MESSAGE.format(
                module_name=module.__name__, constant_name=constant_name
            )
        )

    if isinstance(expected_value, re.Pattern):
        assert (
            expected_value.fullmatch(actual_value) is not None
        ), tc.CONSTANTS_CLASSES_CHANGED_VALUE_MESSAGE.format(
            module_name=module.__name__,
            constant_name=constant_name,
            expected_value=expected_value.pattern,
            actual_value=actual_value,
        )
    else:
        assert (
            actual_value == expected_value
        ), tc.CONSTANTS_CLASSES_CHANGED_VALUE_MESSAGE.format(
            module_name=module.__name__,
            constant_name=constant_name,
            expected_value=expected_value,
            actual_value=actual_value,
        )


@pytest.mark.parametrize(
    "constants_class, snapshot",
    [
        (RemoteSCCSConstants, REMOTE_SCCS_CONSTANTS_SNAPSHOT),
        (RemoteErrorWrappers, REMOTE_ERROR_WRAPPERS_SNAPSHOT),
    ],
)
def test_remote_snapshot_covers_every_constant(
    constants_class: type,
    snapshot: dict[str, object],
    tc: SCCSTestConstants,
) -> None:
    """Verify the snapshot and class definitions are in sync (no drift)."""

    actual_names = {
        name
        for name, value in vars(constants_class).items()
        if name.isupper()
        and not isinstance(value, (property, classmethod, staticmethod, FunctionType))
    }
    snapshot_names = set(snapshot)

    assert (
        actual_names == snapshot_names
    ), tc.CONSTANTS_CLASSES_ADDED_OR_REMOVED_MESSAGE.format(
        module_name=constants_class.__name__,
        added=sorted(actual_names - snapshot_names),
        removed=sorted(snapshot_names - actual_names),
    )
