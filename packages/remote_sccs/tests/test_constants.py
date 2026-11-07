class SCCSTestConstants:
    COMMAND_FIELD_NAME = "command"
    CONSTANTS_CLASSES_ADDED_OR_REMOVED_MESSAGE = (
        "{module_name} has been modified. Added: {added}, Removed: {removed}."
    )
    CONSTANTS_CLASSES_CHANGED_VALUE_MESSAGE = (
        "Constant: {module_name}.{constant_name}, Expected: {expected_value!r}, Actual: "
        "{actual_value!r}."
    )
    DELETED_CONSTANT_ERROR_MESSAGE = (
        "{module_name} is missing constant: {constant_name}"
    )
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
    TEST_STRING = "test"
    UNEXPECTED_ERROR_EXIT_CODE = 2
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred: {type_name}: {e}"
    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = "Unknown command: {command}"
    