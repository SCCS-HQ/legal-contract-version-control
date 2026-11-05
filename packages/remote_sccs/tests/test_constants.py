class SCCSTestConstants:
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
    NEWLINE = "\n"