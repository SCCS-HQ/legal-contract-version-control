"""Test constants used across the remote_sccs test suite.

This module is intentionally not a test file: it defines a single data class
that mirrors the production ``RemoteSCCSConstants`` values so tests can reference
expected strings, status codes, path templates, and other static values.
"""


class SCCSTestConstants:
    """Provide expected constant values for the remote_sccs test suite.

    These mirror the production ``RemoteSCCSConstants`` values but are kept
    separate so tests can reference expected strings, status codes, path
    templates, and other static values without depending on the production
    class internals.
    """

    ABSOLUTE_PATH = "/absolute/path/file.txt"
    ABSOLUTE_PATH_WITH_DOUBLE_PERIOD = "/absolute/path/../file.txt"
    COMMAND_FIELD_NAME = "command"
    CONSTANTS_CLASSES_ADDED_OR_REMOVED_MESSAGE = (
        "{module_name} has been modified. Added: {added}, Removed: {removed}."
    )
    CONSTANTS_CLASSES_CHANGED_VALUE_MESSAGE = (
        "Constant: {module_name}.{constant_name}, Expected: {expected_value!r}, "
        "Actual: {actual_value!r}."
    )
    CURRENT_BRANCH_DICT_KEY = "current_branch"
    DEFAULT_IP_ADDRESS = "127.0.0.1"
    DEFAULT_PORT = 8000
    DELETED_CONSTANT_ERROR_MESSAGE = (
        "{module_name} is missing constant: {constant_name}"
    )
    DOUBLE_PERIOD = ".."
    EASTER_EGG_MESSAGE = "Boo!"
    EMPTY_STRING = ""
    FILE_PUBLISHED_MESSAGE = "File published successfully"
    FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE = "File {filename} is too large"
    HELP_MESSAGES = (
        "Remote SCCS Help",
        "Available commands:",
        "  sccs help - Prints a help message listing the available commands and "
        "their descriptions.",
        "  sccs serve - Hosts a Remote-SCCS server on your computer anyone "
        "on your internet network can access.",
    )
    INVALID_FILE_PATH_IN_ZIP_ERROR_MESSAGE = "Invalid file path in zip"
    INVALID_JSON_DATA_ERROR_MESSAGE = "Invalid JSON data"
    INVALID_REPOSITORY_NAME = "../repo"
    INVALID_REPOSITORY_NAME_ERROR_MESSAGE = "Invalid repository name"
    IP_ADDRESS_RETRIEVAL_ERROR_MESSAGE = (
        "Error retrieving private IP address"
    )
    IP_ADDRESS_RETRIEVAL_SUCCESS_MESSAGE_TEMPLATE = (
        "Your Remote-SCCS server will be accessible on you internet network "
        "at http://{ip_address}:8000"
    )
    LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE = (
        "Local repository has objects that the remote does not have. "
        "Run 'sccs push' to upload these objects before pulling."
    )
    MESSAGE_DICT_KEY = "message"
    METADATA_JSON = "metadata.json"
    MINIMUM_ARGUMENTS = 2
    NEWLINE = "\n"
    OBJECTS_DICT_KEY = "objects"
    OBJECTS_DIRECTORY = "objects"
    OBJECTS_NOT_FOUND_ERROR_MESSAGE = "Repository objects not found"
    PATH_SEPARATOR = "/"
    PUSH_SUCCESS_MESSAGE = "Changes pushed successfully"
    REMOTE_DICT_KEY = "remote"
    REMOTE_SCCS = "remote_sccs"
    REMOTE_SCCS_DESCRIPTION = "Remote API for Self-Hosting of SCCS"
    REMOTE_URL_REQUIRED_ERROR_MESSAGE = "Remote URL is required"
    REPOSITORIES_BASE_DIRECTORY = "./repos"
    REPOSITORIES_DIRECTORY_CREATION_ERROR_MESSAGE = (
        "Error creating repositories directory"
    )
    REPOSITORY_EXISTS_ERROR_MESSAGE = "Repository already exists"
    REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE = "Repository name does not match file name"
    REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Repository not found: {repository_name}"
    )
    REPOSITORY_URL_DICT_KEY = "repository_url"
    SCCS_DIRECTORY = ".sccs"
    SCCS_TEMP_DIRECTORY_GLOB_PATTERN = "sccs_temp_*"
    SECOND_TEST_STRING = "test2"
    STARTING_UVICORN_SERVER_MESSAGE = "Starting Uvicorn Server..."
    STATUS_CODE_400 = 400
    STATUS_CODE_404 = 404
    TEST_STRING = "test"
    TEST_ZIP_FILE_NAME = "test.zip"
    TEXT_FILE_EXTENSION = ".txt"
    TOO_MANY_FILES_ERROR_MESSAGE = "Too many files in the uploaded zip"
    UNEXPECTED_ERROR_EXIT_CODE = 2
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred: {type_name}: {e}"
    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = "Unknown command: {command}"
    UPDATED_BRANCHES_DICT_KEY = "updated_branches"
    UPLOAD_TOO_LARGE_ERROR_MESSAGE = "Uploaded file is too large"
    VALID_REPOSITORY_NAME = "repo"
    ZIP_FILE_EXTENSION = ".zip"
