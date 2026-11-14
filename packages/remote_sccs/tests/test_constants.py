class SCCSTestConstants:
    COMMAND_FIELD_NAME = "command"
    CONSTANTS_CLASSES_ADDED_OR_REMOVED_MESSAGE = (
        "{module_name} has been modified. Added: {added}, Removed: {removed}."
    )
    CONSTANTS_CLASSES_CHANGED_VALUE_MESSAGE = (
        "Constant: {module_name}.{constant_name}, Expected: {expected_value!r}, Actual: "
        "{actual_value!r}."
    )
    DEFAULT_IP_ADDRESS = "127.0.0.1"
    DEFAULT_PORT = 8000
    DELETED_CONSTANT_ERROR_MESSAGE = (
        "{module_name} is missing constant: {constant_name}"
    )
    IP_ADDRESS_RETRIEVAL_ERROR_MESSAGE_TEMPLATE = "Error retrieving private IP address: {e}"
    IP_ADDRESS_RETRIEVAL_SUCCESS_MESSAGE_TEMPLATE = "Your Remote-SCCS server will be accessible on you internet network at http://{ip_address}:tc.DEFAULT_PORT"
    HELP_MESSAGES = (
        "Remote SCCS Help",
        "Available commands:",
        "  sccs help - Prints a help message listing the available commands and "
        "their descriptions.",
        "  sccs serve - Hosts a Remote-SCCS server on your computer anyone "
        "on your internet network can access.",
    )
    MINIMUM_ARGUMENTS = 2
    NEWLINE = "\n"
    REMOTE_SCCS = "remote_sccs"
    REMOTE_SCCS_DESCRIPTION = "Remote API for Self-Hosting of SCCS"
    REPOSITORIES_BASE_DIRECTORY = "./repos"
    REPOSITORIES_DIRECTORY_CREATION_ERROR_MESSAGE_TEMPLATE = "Error creating repositories directory: {e}"
    STARTING_UVICORN_SERVER_MESSAGE = "Starting Uvicorn Server..."
    TEST_STRING = "test"
    UNEXPECTED_ERROR_EXIT_CODE = 2
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred: {type_name}: {e}"
    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = "Unknown command: {command}"
    