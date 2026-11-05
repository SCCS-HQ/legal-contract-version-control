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
