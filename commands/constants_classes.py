#!/usr/bin/env python3

import datetime
from functools import cached_property

import exceptions


class SCCSConstants:
    # region Shared Constants

    # region Shared - Numbers

    COMMIT_IDENTIFIER_DISPLAY_LENGTH = 10
    HTTP_TIMEOUT_SECONDS = 60
    MAX_FILE_READ_SIZE = 64 * 1024
    NOT_SIBLINGS_ERROR_MESSAGE_TEMPLATE = "{staging_root} is not a sibling of {final_root}. The files must be siblings to ensure an atomic write."

    # endregion

    # region Shared - Paths (directories)

    BRANCHES_DIRECTORY = "branches"
    COMMIT_BYTE_HASH_DIRECTORY = "commit_file_hash"
    COMMIT_MESSAGES_DIRECTORY = "commit_messages"
    CONFIG_DIRECTORY = "config"
    CURRENT_BRANCH_DIRECTORY = "current_branch"
    DOCUMENT_DIRECTORY = "docx"
    HISTORY_DIRECTORY = "history"
    HTML_DIRECTORY = "html"
    OBJECTS_DIRECTORY = "objects"
    SCCS_DIRECTORY = ".sccs"
    VIEW_HTML_DIRECTORY = "view_html"

    # endregion

    # region Shared - Paths (files)

    COMMIT_BYTE_HASH_JSON_FILE = "commit_file_hash.json"
    COMMIT_MESSAGES_JSON_FILE = "commit_messages.json"
    CONFIG_JSON_FILE = "config.json"
    CURRENT_BRANCH_JSON_FILE = "current_branch.json"
    HISTORY_JSON_FILE = "history.json"

    # endregion

    # region Shared - Strings (messages, templates, field names, values,
    # separators, attributes, resources, endpoints)

    ACCEPTED_SCHEMES = ("http", "https")
    BRANCH_NAME_FIELD_NAME = "branch name"
    BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' is missing from repository metadata. If the branch "
        "does not exist, please create it."
    )
    BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE = (
        "Failed to {action} branch. Please try again."
    )
    COMMIT_IDENTIFIER_FIELD_NAME = "commit byte hash"
    CONTENT_TYPE_ZIP = "application/zip"
    CREATE_SUBCOMMAND = "create"
    DELETE_SUBCOMMAND = "delete"
    DOCUMENT_EXTENSION = ".docx"
    EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = (
        "{field} cannot be empty. Please provide a valid {field}."
    )
    ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
        "The entered file '{file_path}' does not exist. Please provide a valid file "
        "path to an existing file."
    )
    INVALID_URL_ERROR_MESSAGE = (
        f"Invalid remote URL provided. The URL must start with one of the following "
        f"schemes: {', '.join(ACCEPTED_SCHEMES)}, and use the format "
        f"'http(s)://<host>/<base-path>'. Base path is optional."
    )
    MAIN_BRANCH_NAME = "main"
    PATH_SEPARATOR = "/"
    POST_FILE_FIELD_NAME = "file"
    REPOSITORY_NAME_FIELD_NAME = "repository name"
    RGLOB_ALL_FILES_PATTERN = "*"
    SCCS_COMMAND_PREFIX = "sccs"
    STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}"
    UNZIP_FAILED_ERROR_MESSAGE = (
        "Failed to unzip repository file. Please try again or ensure the zip is valid."
    )
    ZIP_BUFFER_SEEK_ERROR_MESSAGE = "Failed to reset buffer position. Please try again."
    ZIP_EXTENSION = ".zip"
    ZIPPING_FILE_ERROR_MESSAGE = "Failed to zip current working directory."

    # endregion

    # region Shared - Configuration Values (keys, schemes, dict keys)

    ACCEPTED_CONFIG_KEYS = ("remote", "name", "email")
    AUTHOR_DICT_KEY = "author"
    BRANCHES_DICT_KEY = "branches"
    BYTE_HASH_DICT_KEY = "byte_hash"
    COMMIT_ORDER_DICT_KEY = "commit_order"
    COMMIT_MESSAGES_DICT_KEY = "commit_messages"
    CONFIG_DICT_KEY = "config"
    CURRENT_BRANCH_DICT_KEY = "current_branch"
    EMAIL_KEY = "email"
    HEX_DIGITS = "0123456789abcdef"
    HISTORY_DICT_KEY = "history"
    HTTP_OBJECTS_DICT_KEY = "objects"
    INVALID_KEY_ERROR_MESSAGE = (
        f"Invalid configuration key provided. Please provide one of the valid keys: "
        f"remote, name, email."
    )
    LATEST_COMMIT_DICT_KEY = "latest_commit"
    LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
    LOG_DICT_KEY = "log"
    MESSAGE_DICT_KEY = "message"
    NAME_KEY = "name"
    REMOTE_KEY = "remote"
    TIMESTAMP_DICT_KEY = "timestamp"
    UPDATED_BRANCHES_DICT_KEY = "updated_branches"

    # endregion

    # region Shared - HTML

    DEFAULT_HTML_STYLES = """
    <style>
            * {
                font-family: Arial, Helvetica, sans-serif;
            }

            .inserted {
                background-color: #d4fcbc;
                display: block;
                width: fit-content;
            }

            .deleted {
                background-color: #fbb6c2;
                display: block;
                width: fit-content;
            }

            .center {
                display: flex;
                justify-content: center;
            }
    </style>
    """

    # endregion

    # region Shared - Lists

    COMMANDS_LIST = (
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    )

    # endregion

    # region Shared - Dicts

    COMMAND_DESCRIPTIONS = {
        "branch": "Create a new branch, delete, or list branches.",
        "clone": "Clone a hosted SCCS repository with a URL.",
        "commit": "Commit changes to the repository.",
        "config": "Configure a repository's data value (remote, name, email)",
        "diff": "Show differences between the current document and a past commit.",
        "help": "Print this help message.",
        "init": "Initialize a new SCCS repository.",
        "log": "Print a list of past commits for the current branch.",
        "merge": "Merge the entered branch into the current branch.",
        "open": "Open a commit file and update the current document.",
        "publish": "Publish a local repository to a hosting service.",
        "pull": "Pull changes from a remote repository and merge them "
        "into the local repository.",
        "push": "Push changes from the local repository to a remote repository.",
        "revert": "Revert the current document to the specified commit.",
        "reset": "Delete all uncommitted changes.",
        "switch": "Switch between document branches.",
        "status": "Check the status of the current document for uncommitted changes.",
    }

    # endregion

    # region Shared - File I/O

    EMPTY_STRING = ""
    JSON_EXTENSION = ".json"
    NEWLINE = "\n"
    UTF_8 = "utf-8"

    # endregion

    # region Shared - Runtime

    @cached_property
    def PROGRAM_START_TIME(self) -> str:

        return datetime.datetime.now().isoformat()

    # endregion

    # endregion

    # region File-Specific Constants - branch.py

    # region branch.py - Numbers
    # (none)
    # endregion

    # region branch.py - Paths

    WALK_ROOT = "."

    # endregion

    # region branch.py - Strings

    ACCEPTED_SUBCOMMANDS = ("create", "delete", "list")
    BRANCHES_DIRECTORY_LIST_HEADER = "Branches:"
    BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' already exists."
    )
    BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' created from '{current_branch_name}' successfully and "
        "is set to the current branch."
    )
    BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' deleted successfully."
    )
    CURRENT_BRANCH_DELETION_ERROR_MESSAGE = (
        "Cannot delete the current branch. Please switch to another branch first."
    )
    CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
    DELETING_MAIN_ERROR_MESSAGE = (
        "You cannot delete 'main'. Please try deleting another branch."
    )
    INVALID_SUBCOMMAND_ERROR_MESSAGE = (
        "Invalid subcommand provided. Please provide one of the valid subcommands: "
        "create, delete, list."
    )
    LIST_SUBCOMMAND = "list"
    OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"
    ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE = (
        "Failed to rollback metadata after failure for branch '{branch_name}'. The "
        "repository metadata is likely in an inconsistent state."
    )
    SUBCOMMAND_FIELD_NAME = "subcommand"

    # endregion

    # region branch.py - Other

    COMMIT_AUTHOR_TEMPLATE = "{name} <{email}>"

    # endregion

    # endregion

    # region File-Specific Constants - clone.py

    # region clone.py - Numbers

    MINIMUM_PATH_PARTS = 2

    # endregion

    # region clone.py - Strings

    CLONE_ENDPOINT = "/clone"
    CLONE_SUCCESS_MESSAGE = "Repository cloned successfully."
    HTTP_REQUEST_ERROR_MESSAGE = (
        "Failed to request repository from the remote URL. Please try again."
    )
    INVALID_ENDING_ERROR_MESSAGE = (
        f"Invalid remote URL provided. Please provide a valid URL ending with "
        f"'{CLONE_ENDPOINT}'."
    )
    INVALID_REPOSITORY_NAME_ERROR_MESSAGE = (
        "Invalid repository name. Please ensure the repository is properly initialized "
        "with a valid name."
    )
    URL_FIELD_NAME = "URL"

    # endregion

    # endregion

    # region File-Specific Constants - commit.py

    # region commit.py - Strings

    COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = (
        "Commit {commit_identifier} created successfully."
    )
    COMMIT_MESSAGE_FIELD_NAME = "commit message"
    TEMPORARY_DIRECTORY_PREFIX = "sccs_temp_"

    # endregion

    # endregion

    # region File-Specific Constants - config.py

    # region config.py - Strings

    CONFIG_SUCCESS_MESSAGE_TEMPLATE = (
        "Configuration '{key}' set to '{value}' successfully."
    )
    INVALID_PATH_ENDING_ERROR_MESSAGE = (
        f"API URL must end with '/repos/your-repo-name'."
    )
    REPOSITORIES_PATH_SEGMENT = "repos"
    REQUIRED_PATH_ENDING_TEMPLATE = f"/{REPOSITORIES_PATH_SEGMENT}/{{repo_name}}"

    # endregion

    # endregion

    # region File-Specific Constants - diff.py

    # region diff.py - Strings

    CLASS_HTML_ATTRIBUTE = "class"
    DATA_NUMBER_HTML_ATTRIBUTE = "data-number"
    DELETED_HTML_ATTRIBUTE_VALUE = "deleted"
    DELETE_OPCODE = "delete"
    DIFF_ERROR_MESSAGE = "Failed to generate diff output. Please try again."
    DIFF_SUCCESS_MESSAGE = "Commit diff successfully created."
    HTML_PARSER = "html.parser"
    INSERTED_HTML_ATTRIBUTE_VALUE = "inserted"
    INSERT_OPCODE = "insert"
    REPLACE_OPCODE = "replace"
    STYLE_TAG_NAME = "style"
    TAGS_TO_UNWRAP = (
        "b",
        "i",
        "u",
        "strong",
        "em",
        "style",
        "table",
        "tr",
        "td",
        "ol",
        "ul",
    )

    # endregion

    # endregion

    # region File-Specific Constants - help.py

    # region help.py - Properties

    @property
    def HELP_MESSAGES(self) -> tuple[str, ...]:

        return (
            "SCCS Help",
            "Available commands:",
        ) + tuple(
            f"  {self.SCCS_COMMAND_PREFIX} {i}" f" - {self.COMMAND_DESCRIPTIONS[i]}"
            for i in self.COMMANDS_LIST
        )

    # endregion

    # endregion

    # region File-Specific Constants - init.py

    # region init.py - Numbers

    FULL_COMMIT_IDENTIFIER_LENGTH = 64

    # endregion

    # region init.py - Dicts

    DEFAULT_BRANCH_DATA = {
        CURRENT_BRANCH_DICT_KEY: MAIN_BRANCH_NAME,
        BRANCHES_DICT_KEY: [MAIN_BRANCH_NAME],
    }

    # endregion

    # region init.py - Strings

    ALREADY_INIT_ERROR_MESSAGE = "This document has already been initialized with SCCS."
    HTML_BOILERPLATE_TEMPLATE = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head><body>"
        "<div class='center'><div id='target'>{html}</div></div></body></html>"
    )
    HTML_EXTENSION = ".html"
    INIT_BYTE_HASH_DATA_ERROR_MESSAGE = (
        "Failed to write byte hash data during initialization. Please try again."
    )
    INIT_COPY_ERROR_MESSAGE = (
        "Failed to copy document or write HTML during initialization."
    )
    INIT_CREATE_ERROR_MESSAGE = "Failed to create SCCS directory layout."
    INITIAL_COMMIT_DICT_KEY = "initial_commit"
    INIT_COMMIT_MESSAGE = (
        "Initial commit (This is a default commit message " "for initial version)"
    )
    INITIAL_COMMIT_NUMBER_DICT_KEY = "1"
    INITIAL_VERSION_COMMIT_MESSAGE = "initial_version"
    INIT_BRANCH_DATA_ERROR_MESSAGE = (
        "Failed to write branch data during initialization."
    )
    INIT_SUCCESS_MESSAGE = "SCCS initialization complete."
    INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "
    INVALID_FILE_TYPE_ERROR_MESSAGE = (
        "File is not a .docx file. Please provide a valid .docx file."
    )
    INIT_TEMPORARY_DIRECTORY_PREFIX = "sccs_init_"
    SOURCE_FILE_DELETION_ERROR_WARNING_TEMPLATE = (
        "Warning: could not remove source file {document_path}: {e}. The repository has been initialized."
    )
    

    # endregion

    # endregion

    # region File-Specific Constants - log.py

    # region log.py - Strings

    LOG_AUTHOR_LABEL = "Author: "
    LOG_COMMIT_FILE_LABEL = "Commit File: "
    LOG_DATE_LABEL = "Date: "
    LOG_MESSAGE_LABEL = "Message: "
    LOG_SEPARATOR = "-" * 30

    # endregion

    # endregion

    # region File-Specific Constants - merge.py

    # region merge.py - Strings

    CURRENT_BRANCH_MERGE_ERROR_MESSAGE = "Cannot merge the current branch into itself."
    MERGE_COMMIT_MESSAGE_TEMPLATE = (
        "Merged branch '{branch_name}' into '{current_branch}'."
    )
    MERGE_COPY_ERROR_MESSAGE = "Failed to copy branch data during merge."
    MERGE_DOCUMENT_COPY_ERROR_MESSAGE = "Failed to copy document during merge."
    MERGE_SUCCESS_MESSAGE_TEMPLATE = (
        "Successfully merged branch '{branch_name}' into branch '{current_branch}'."
    )

    # endregion

    # endregion

    # region File-Specific Constants - open.py

    # region open.py - Strings

    OPEN_COPY_ERROR_MESSAGE = "Failed to copy commit file for open operation."
    OPEN_OUTPUT_FILE_NAME_TEMPLATE = "Opened_DOCX_Commit_{commit_identifier}"
    OPEN_SUCCESS_MESSAGE_TEMPLATE = (
        "Commit '{commit_identifier}' has been successfully opened in {output_file}. "
        "It is safe to delete this file. No changes will be lost unless {output_file} "
        "is modified after this point."
    )

    # endregion

    # endregion

    # region File-Specific Constants - publish.py

    # region publish.py - Strings

    PUBLISH_ENDPOINT_TEMPLATE = "{base_url}/publish"
    PUBLISH_SUCCESS_MESSAGE_TEMPLATE = "Repository published successfully to {url}."
    ZIP_BUFFER_CREATION_FAILED_ERROR_MESSAGE = (
        "Failed to create a buffer for the zipped repository. Please try again."
    )

    # endregion

    # endregion

    # region File-Specific Constants - pull.py

    # region pull.py - Strings

    PULL_ENDPOINT_TEMPLATE = "{base_url}/pull"
    PULL_SUCCESS_MESSAGE_TEMPLATE = "Repository pulled successfully from {url}."

    # endregion

    # endregion

    # region File-Specific Constants - push.py

    # region push.py - Numbers
    # (none)
    # endregion

    # region push.py - Paths

    # (none)

    # endregion

    # region push.py - Strings

    CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE = (
        "Push successful, but failed to clear updated branches list in current branch "
        "file."
    )
    MISSING_REMOTE_OBJECTS_ERROR_MESSAGE = (
        "The remote repository has extra commits that the local is missing. Please "
        "pull the latest changes before pushing."
    )
    NO_UPDATED_BRANCHES_ERROR_MESSAGE = (
        "No updated branches were found. Please update at least one branch before "
        "pushing changes."
    )
    PUSH_ENDPOINT_TEMPLATE = "{base_url}/push"
    PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to push to repository {url}."
    PUSH_HTTP_REQUEST_ERROR_MESSAGE = (
        "The HTTP request failed while attempting to push the new changes. Please try "
        "again later or check your internet connection."
    )
    PUSH_SUCCESS_MESSAGE_TEMPLATE = "Repository pushed successfully to {url}."
    REQUIRED_PATH_ENDING_TEMPLATE = f"/{REPOSITORIES_PATH_SEGMENT}/{{repo_name}}"
    REPOSITORIES_PATH_SEGMENT = "repos"
    TEMPORARY_DIRECTORY_TEMPLATE = "tmp_{repo_name}"

    # endregion

    # endregion

    # region File-Specific Constants - repository_layout.py

    # region repository_layout.py - Numbers
    # (none)
    # endregion

    # region repository_layout.py - Paths (directories)
    # (none)
    # endregion

    # region repository_layout.py - Paths (files)
    
    METADATA_JSON = "metadata.json"

    # endregion

    # region repository_layout.py - Strings
    ALLOWED_NAME_AND_EMAIL_CHARACTERS = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._%+-"
    )
    ALLOWED_REMOTE_CHARACTERS = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&'("
        ")*+,;=%"
    )

    DIFF_OUTPUT_HTML_FILE = "diff.html"
    INVALID_BRANCH_DATA_ERROR_MESSAGE = (
        "Invalid branch data. Please ensure that the branch data has not been manually "
        "modified and the targeted branch exists."
    )
    INVALID_COMMIT_HISTORY_DIRECTORY_DATA_ERROR_MESSAGE = (
        "Invalid commit history data. Please ensure that the commit data has not been "
        "manually modified."
    )
    INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE = (
        "Invalid commit file name. Please provide a shortened, 10 character commit "
        "hash or the full 64 character commit hash as the commit identifier."
    )
    INVALID_CHARACTER_IN_NAME_OR_EMAIL_ERROR_MESSAGE = (
        "Invalid character in config value. Only letters, numbers, ., _, %, +, and - "
        "are allowed."
    )
    INVALID_CHARACTER_IN_REMOTE_ERROR_MESSAGE = (
        "Invalid character in URL. Only letters, numbers, and -._~:/?#[]@!$&'()*+,;=% "
        "are allowed."
    )
    LEFT_ANGLE_BRACKET = "<"
    MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = (
        "Resource '{resource_name}' is missing from the repository directory."
    )
    MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Multiple commit files found matching '{commit_identifier}'. Please provide a "
        "full, 64 character commit hash."
    )
    NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "No uncommitted changes detected. Uncommitted changes are required before "
        "committing."
    )
    RIGHT_ANGLE_BRACKET = ">"
    SPACE = " "
    TARGET_BRANCH_NOT_SET_ERROR_MESSAGE = (
        "Target branch not set. Ensure the branch is set by using "
        "Repository*.target.set(foo)"
    )
    UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "Uncommitted changes detected. Please clean the working tree before proceeding."
    )

    # endregion

    # endregion

    # region File-Specific Constants - reset.py

    # region reset.py - Strings

    RESET_ERROR_MESSAGE = "Failed to reset the document. Please try again."
    RESET_SUCCESS_MESSAGE = (
        "All uncommitted changes have been deleted. The document has been reset to the "
        "latest commit."
    )

    # endregion

    # endregion

    # region File-Specific Constants - revert.py

    # region revert.py - Strings

    REVERT_COMMIT_MESSAGE_TEMPLATE = (
        "Reverted document to commit '{commit_identifier}'."
    )
    REVERT_COPY_ERROR_MESSAGE = (
        "Failed to revert document to selected commit. Please try again."
    )
    REVERT_SUCCESS_MESSAGE_TEMPLATE = (
        "Document successfully reverted to commit '{commit_identifier}' on commit "
        "'{new_commit_identifier}'."
    )
    SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
        "Source file '{file_name}' does not exist."
    )

    # endregion

    # endregion

    # region File-Specific Constants - sccs(sh)

    # region sccs(sh) - Strings

    PYTHON_EXTENSION = ".py"

    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = (
        f"Unknown command: {{entered_command}}. "
        f"Please use {', '.join(COMMANDS_LIST)} "
        f"along with required arguments."
    )

    # endregion

    # endregion

    # region File-Specific Constants - status.py

    # region status.py - Strings

    NO_UNCOMMITTED_CHANGES = "Status Report: No uncommitted changes detected."
    UNCOMMITTED_CHANGES_FOUND = "Status Report: Uncommitted changes detected."

    # endregion

    # endregion

    # region File-Specific Constants - switch.py

    # region switch.py - Strings

    INVALID_BRANCH_NAME_ERROR_MESSAGE = "Invalid subcommand or missing branch name."
    SWITCH_COMMIT_FILE_MISSING_ERROR_MESSAGE_TEMPLATE = (
        "Commit file missing for branch '{branch_name}'."
    )
    SWITCH_COPY_ERROR_MESSAGE = (
        "Failed to copy commit file during branch switch. Please try again."
    )
    SWITCH_SUCCESS_MESSAGE_TEMPLATE = "Successfully switched to branch '{branch_name}'."
    UTILS_ARGUMENT_ERROR_MESSAGE = (
        "Required argument missing. Please provide the required argument."
    )

    # endregion

    # endregion

    # region File-Specific Constants - utils.py

    # region utils.py - String

    PATH_IS_ABSOLUTE_OR_CONTAINS_DOUBLE_PERIOD_ERROR_MESSAGE = (
        "Invalid file path: {entry_path} in zip. Please ensure the path does not "
        "include '..' and is not an absolute path."
    )
    TARGET_PATH_NOT_RELATIVE_TO_PARENT_DIRECTORY_ERROR_MESSAGE = (
        "Invalid file path: {target_path} in zip. Please ensure that {target_path} is "
        "inside {destination_resolved}."
    )
    EXPECTED_ERROR_TEMPLATE = "An error occurred: {e}"
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred: {type_name}: {e}"

    # endregion

    # endregion


_missing_commands = [
    i
    for i in SCCSConstants.COMMANDS_LIST
    if i not in SCCSConstants.COMMAND_DESCRIPTIONS
]
if _missing_commands:
    raise exceptions.SCCSException(
        f"COMMAND_DESCRIPTIONS is missing entries for: "
        f"{', '.join(_missing_commands)}"
    )


class ErrorWrappers:
    EXPECTED_ERROR_TEMPLATE = "An error occurred: {e}"
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred: {type_name}: {e}"
