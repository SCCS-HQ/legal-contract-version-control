#!/usr/bin/env python3

import datetime
import uuid
from types import MappingProxyType


class ErrorWrappers:
    """
    A class to hold the templates used to wrap expected and unexpected errors raised
    while running a command.
    """

    EXPECTED_ERROR_TEMPLATE = "An error occurred: {e}"
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred: {type_name}: {e}"


class SCCSConstants:
    """
    A class to hold constants used throughout the SCCS application. This includes error
    messages, field names, directory names, and other static values that are referenced
    in multiple places in the codebase.
    """

    ACCEPTED_CONFIG_KEYS = ("remote", "name", "email")
    ACCEPTED_SCHEMES = ("http", "https")
    ACCEPTED_SUBCOMMANDS = ("create", "delete", "list")
    ALLOWED_NAME_AND_EMAIL_CHARACTERS = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._%+-"
    )
    ALLOWED_REMOTE_CHARACTERS = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&'("
        ")*+,;=%"
    )
    ALREADY_INIT_ERROR_MESSAGE = "This document has already been initialized with SCCS."
    AUTHOR_DICT_KEY = "author"

    BRANCHES_DICT_KEY = "branches"
    BRANCHES_DIRECTORY_LIST_HEADER = "Branches:"
    BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' already exists."
    )
    BRANCH_COMMAND_NAME = "branch"
    BRANCH_CREATE_ARGUMENT_HELP = "The branch to create."
    BRANCH_CREATE_SUBCOMMAND_HELP = "Create a new branch."
    BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' created from '{current_branch_name}' successfully and "
        "is set to the current branch."
    )
    BRANCH_DELETE_ARGUMENT_HELP = "The branch to delete."
    BRANCH_DELETE_SUBCOMMAND_HELP = "Delete an existing branch."
    BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' deleted successfully."
    )
    BRANCH_LIST_SUBCOMMAND_HELP = "List all branches."
    BRANCH_MERGE_ARGUMENT_HELP = "The branch to merge into the current branch."
    BRANCH_NAME_ARGUMENT_NAME = "branch_name"
    BRANCH_NAME_FIELD_NAME = "branch name"
    BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' is missing from repository metadata. If the branch "
        "does not exist, please create it."
    )
    BRANCH_SWITCH_ARGUMENT_HELP = "The branch to switch to."
    BYTE_HASH_DICT_KEY = "byte_hash"

    CLASS_HTML_ATTRIBUTE = "class"
    CLONE_COMMAND_NAME = "clone"
    CLONE_DESTINATION_EXISTS_ERROR_MESSAGE = (
        "A directory with the repository name already exists in the current directory."
    )
    CLONE_ENDPOINT = "/clone"
    CLONE_SUCCESS_MESSAGE = "Repository cloned successfully."
    COMMAND_FIELD_NAME = "command"
    COMMIT_AUTHOR_TEMPLATE = "{name} <{email}>"
    COMMIT_COMMAND_NAME = "commit"
    COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = (
        "Commit {commit_identifier} created successfully."
    )
    COMMIT_IDENTIFIER_ARGUMENT_NAME = "commit_identifier"
    COMMIT_IDENTIFIER_DIFF_ARGUMENT_HELP = "The commit identifier to diff against."
    COMMIT_IDENTIFIER_DISPLAY_LENGTH = 10
    COMMIT_IDENTIFIER_FIELD_NAME = "commit byte hash"
    COMMIT_IDENTIFIER_OPEN_ARGUMENT_HELP = "The commit identifier to open."
    COMMIT_IDENTIFIER_REVERT_ARGUMENT_HELP = (
        "The commit identifier to revert the document to."
    )
    COMMIT_MESSAGES_DICT_KEY = "commit_messages"
    COMMIT_MESSAGE_ARGUMENT_HELP = "The message describing the commit."
    COMMIT_MESSAGE_ARGUMENT_NAME = "commit_message"
    COMMIT_MESSAGE_FIELD_NAME = "commit message"
    COMMIT_NUMBER_INCREMENT = 1
    COMMIT_ORDER_DICT_KEY = "commit_order"
    CONFIG_COMMAND_NAME = "config"
    CONFIG_DICT_KEY = "config"
    CONFIG_KEY_ARGUMENT_HELP_TEMPLATE = (
        "The configuration key to set. One of: {keys}."
    )
    CONFIG_KEY_ARGUMENT_NAME = "key"
    CONFIG_SUCCESS_MESSAGE_TEMPLATE = (
        "Configuration '{key}' set to '{value}' successfully."
    )
    CONFIG_VALUE_ARGUMENT_HELP = "The value to set the configuration key to."
    CONFIG_VALUE_ARGUMENT_NAME = "value"
    CONTENT_TYPE_ZIP = "application/zip"
    CREATE_SUBCOMMAND = "create"
    CURRENT_BRANCH_DELETION_ERROR_MESSAGE = (
        "Cannot delete the current branch. Please switch to another branch first."
    )
    CURRENT_BRANCH_DICT_KEY = "current_branch"
    CURRENT_BRANCH_MERGE_ERROR_MESSAGE = "Cannot merge the current branch into itself."
    CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"

    DATA_DATA = "data"
    DATA_NUMBER_HTML_ATTRIBUTE = "data-number"
    DATA_REMOTE = "remote"
    DEBUG_FLAG = "--debug"
    DEBUG_FLAG_HELP_MESSAGE = "Does not except Exception or SCCSException."
    DEBUG_FLAG_SHORT = "-d"
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
    DELETED_HTML_ATTRIBUTE_VALUE = "deleted"
    DELETE_OPCODE = "delete"
    DELETE_SUBCOMMAND = "delete"
    DELETING_MAIN_ERROR_MESSAGE = (
        "You cannot delete 'main'. Please try deleting another branch."
    )
    DIFF_COMMAND_NAME = "diff"
    DIFF_ERROR_MESSAGE = "Failed to generate diff output. Please try again."
    DIFF_OUTPUT_HTML_FILE = "diff.html"
    DIFF_SUCCESS_MESSAGE = "Commit diff successfully created."
    DOCUMENT_DIRECTORY = "docx"
    DOCUMENT_EXTENSION = ".docx"
    DOCUMENT_PATH_ARGUMENT_HELP = "The path to the document to initialize with SCCS."
    DOCUMENT_PATH_ARGUMENT_NAME = "document_path"
    DOUBLE_PERIOD = ".."

    EMAIL_KEY = "email"
    EMPTY_STRING = ""
    EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = (
        "{field} cannot be empty. Please provide a valid {field}."
    )
    ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
        "The entered file '{file_path}' does not exist. Please provide a valid file "
        "path to an existing file."
    )
    EXPECTED_ERROR_EXIT_CODE = 1

    FILE_START_POSITION = 0
    FIRST_ELEMENT_INDEX = 0
    FULL_COMMIT_IDENTIFIER_LENGTH = 64

    HELP_COMMAND_NAME = "help"

    @property
    def HELP_MESSAGES(self) -> tuple[str, ...]:
        """
        Return the help messages listing the available SCCS commands and their
        descriptions.
        """

        return (
            "SCCS Help",
            "Available commands:",
        ) + tuple(
            f"  sccs {i}" f" - {self.COMMAND_DESCRIPTIONS[i]}"
            for i in (
                self.BRANCH_COMMAND_NAME,
                self.CLONE_COMMAND_NAME,
                self.COMMIT_COMMAND_NAME,
                self.CONFIG_COMMAND_NAME,
                self.DIFF_COMMAND_NAME,
                self.HELP_COMMAND_NAME,
                self.INIT_COMMAND_NAME,
                self.LOG_COMMAND_NAME,
                self.MERGE_COMMAND_NAME,
                self.OPEN_COMMAND_NAME,
                self.PUBLISH_COMMAND_NAME,
                self.PULL_COMMAND_NAME,
                self.PUSH_COMMAND_NAME,
                self.RESET_COMMAND_NAME,
                self.REVERT_COMMAND_NAME,
                self.STATUS_COMMAND_NAME,
                self.SWITCH_COMMAND_NAME
            )
        )

    HEX_DIGITS = "0123456789abcdef"
    HISTORY_DICT_KEY = "history"
    HTML_BOILERPLATE_TEMPLATE = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head><body>"
        "<div class='center'><div id='target'>{html}</div></div></body></html>"
    )
    HTML_DIRECTORY = "html"
    HTML_EXTENSION = ".html"
    HTML_PARSER = "html.parser"
    HTTP_OBJECTS_DICT_KEY = "objects"
    HTTP_REQUEST_ERROR_MESSAGE = (
        "Failed to request repository from the remote URL. Please try again."
    )
    HTTP_TIMEOUT_SECONDS = 60

    INITIAL_COMMIT_DICT_KEY = "initial_commit"
    INITIAL_COMMIT_NUMBER = 1
    INITIAL_COMMIT_NUMBER_DICT_KEY = "1"
    INITIAL_VERSION_COMMIT_MESSAGE = "initial_version"
    INIT_COMMAND_NAME = "init"
    INIT_COMMIT_MESSAGE = (
        "Initial commit (This is a default commit message "
        "for initial version)"
    )
    INIT_COPY_ERROR_MESSAGE = (
        "Failed to copy document or write HTML during initialization."
    )
    INIT_CREATE_ERROR_MESSAGE = "Failed to create SCCS directory layout."
    INIT_SUCCESS_MESSAGE = "SCCS initialization complete."
    INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "
    INSERTED_HTML_ATTRIBUTE_VALUE = "inserted"
    INSERT_OPCODE = "insert"
    INVALID_BRANCH_DATA_ERROR_MESSAGE = (
        "Invalid branch data. Please ensure that the branch data has not been manually "
        "modified and the targeted branch exists."
    )
    INVALID_BRANCH_NAME_ERROR_MESSAGE = "Invalid subcommand or missing branch name."
    INVALID_CHARACTER_IN_NAME_OR_EMAIL_ERROR_MESSAGE = (
        "Invalid character in config value. Only letters, numbers, ., _, %, +, and - "
        "are allowed."
    )
    INVALID_CHARACTER_IN_REMOTE_ERROR_MESSAGE = (
        "Invalid character in URL. Only letters, numbers, and -._~:/?#[]@!$&'()*+,;=% "
        "are allowed."
    )
    INVALID_COMMIT_HISTORY_DIRECTORY_DATA_ERROR_MESSAGE = (
        "Invalid commit history data. Please ensure that the commit data has not been "
        "manually modified."
    )
    INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE = (
        "Invalid commit file name. Please provide a shortened, 10 character commit "
        "hash or the full 64 character commit hash as the commit identifier."
    )
    INVALID_ENDING_ERROR_MESSAGE = (
        f"Invalid remote URL provided. Please provide a valid URL ending with "
        f"'{CLONE_ENDPOINT}'."
    )
    INVALID_FILE_TYPE_ERROR_MESSAGE = (
        "File is not a .docx file. Please provide a valid .docx file."
    )
    INVALID_KEY_ERROR_MESSAGE = (
        "Invalid configuration key provided. Please provide one of the valid keys: "
        "remote, name, email."
    )
    INVALID_PATH_ENDING_ERROR_MESSAGE = "API URL must end with '/repos/your-repo-name'."
    INVALID_REPOSITORY_NAME_ERROR_MESSAGE = (
        "Invalid repository name. Please ensure the repository is properly initialized "
        "with a valid name."
    )
    INVALID_SUBCOMMAND_ERROR_MESSAGE = (
        "Invalid subcommand provided. Please provide one of the valid subcommands: "
        "create, delete, list."
    )
    INVALID_URL_ERROR_MESSAGE = (
        f"Invalid remote URL provided. The URL must start with one of the following "
        f"schemes: {', '.join(ACCEPTED_SCHEMES)}, and use the format "
        f"'http(s)://<host>/<base-path>'. Base path is optional."
    )

    JSON_INDENT = 4

    LAST_TAG_INDEX = -1
    LATEST_COMMIT_DICT_KEY = "latest_commit"
    LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
    LIST_SUBCOMMAND = "list"
    LOCAL_SCCS = "local_sccs"
    LOCAL_SCCS_DESCRIPTION = "Simple Contracts Communication System"
    LOG_AUTHOR_LABEL = "Author: "
    LOG_COMMAND_NAME = "log"
    LOG_COMMIT_FILE_LABEL = "Commit File: "
    LOG_DATE_LABEL = "Date: "
    LOG_DICT_KEY = "log"
    LOG_MESSAGE_LABEL = "Message: "
    LOG_SEPARATOR = "-" * 30

    MAIN_BRANCH_NAME = "main"
    MAXIMUM_COMMIT_FILE_MATCHES = 1
    MAX_FILE_READ_SIZE = 64 * 1024
    MERGE_COMMAND_NAME = "merge"
    MERGE_COMMIT_MESSAGE_TEMPLATE = (
        "Merged branch '{branch_name}' into '{current_branch}'."
    )
    MERGE_DOCUMENT_COPY_ERROR_MESSAGE = "Failed to copy document during merge."
    MERGE_SUCCESS_MESSAGE_TEMPLATE = (
        "Successfully merged branch '{branch_name}' into branch '{current_branch}'."
    )
    MESSAGE_DICT_KEY = "message"
    METADATA_JSON = "metadata.json"
    MINIMUM_ARGUMENTS = 2
    MINIMUM_PATH_PARTS = 2
    MISSING_REMOTE_OBJECTS_ERROR_MESSAGE = (
        "The remote repository has extra commits that the local is missing. Please "
        "pull the latest changes before pushing."
    )
    MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = (
        "Resource '{resource_name}' is missing from the repository directory."
    )
    MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Multiple commit files found matching '{commit_identifier}'. Please provide a "
        "full, 64 character commit hash."
    )

    NAME_KEY = "name"
    NEWLINE = "\n"
    NO_UNCOMMITTED_CHANGES = "Status Report: No uncommitted changes detected."
    NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "No uncommitted changes detected. Uncommitted changes are required before "
        "committing."
    )

    OBJECTS_DIRECTORY = "objects"
    OLD_ROOT_TEMPLATE = f"{{repository_name}}.old-{uuid.uuid4().hex}"
    OPEN_COMMAND_NAME = "open"
    OPEN_COPY_ERROR_MESSAGE = "Failed to copy commit file for open operation."
    OPEN_OUTPUT_FILE_NAME_TEMPLATE = "Opened_DOCX_Commit_{commit_identifier}"
    OPEN_SUCCESS_MESSAGE_TEMPLATE = (
        "Commit '{commit_identifier}' has been successfully opened in {output_file}. "
        "It is safe to delete this file. No changes will be lost unless {output_file} "
        "is modified after this point."
    )
    OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"

    PATH_IS_ABSOLUTE_OR_CONTAINS_DOUBLE_PERIOD_ERROR_MESSAGE = (
        "Invalid file path: {entry_path} in zip. Please ensure the path does not "
        "include '..' and is not an absolute path."
    )
    PATH_SEPARATOR = "/"
    POST_FILE_FIELD_NAME = "file"
    PROGRAM_START_TIME = datetime.datetime.now(datetime.timezone.utc).isoformat()
    PUBLISH_COMMAND_NAME = "publish"
    PUBLISH_ENDPOINT_TEMPLATE = "{base_url}/publish"
    PUBLISH_SUCCESS_MESSAGE_TEMPLATE = "Repository published successfully to {url}."
    PULL_COMMAND_NAME = "pull"
    PULL_ENDPOINT_TEMPLATE = "{base_url}/pull"
    PULL_SUCCESS_MESSAGE_TEMPLATE = "Repository pulled successfully from {url}."
    PUSH_COMMAND_NAME = "push"
    PUSH_ENDPOINT_TEMPLATE = "{base_url}/push"
    PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to push to repository {url}."
    PUSH_HTTP_REQUEST_ERROR_MESSAGE = (
        "The HTTP request failed while attempting to push the new changes. Please try "
        "again later or check your internet connection."
    )
    PUSH_SUCCESS_MESSAGE_TEMPLATE = "Repository pushed successfully to {url}."
    PWD_ENVIRONMENT_VARIABLE = "PWD"

    REMOTE_KEY = "remote"
    REPLACE_OPCODE = "replace"
    REPOSITORIES_PATH_SEGMENT = "repos"
    REPOSITORY_NAME_FIELD_NAME = "repository name"
    REPOSITORY_NAME_PATH_INDEX = -2
    REQUIRED_PATH_ENDING_TEMPLATE = f"/{REPOSITORIES_PATH_SEGMENT}/{{repo_name}}"
    RESET_COMMAND_NAME = "reset"
    RESET_ERROR_MESSAGE = "Failed to reset the document. Please try again."
    RESET_SUCCESS_MESSAGE = (
        "All uncommitted changes have been deleted. The document has been reset to the "
        "latest commit."
    )
    REVERT_COMMAND_NAME = "revert"
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
    RGLOB_ALL_FILES_PATTERN = "*"

    SCCS_DIRECTORY = ".sccs"
    SINGLE_PERIOD = "."
    SOURCE_FILE_DELETION_ERROR_WARNING_TEMPLATE = (
        "Warning: could not remove source file {document_path}: {e}. The repository "
        "has been initialized."
    )
    SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
        "Source file '{file_name}' does not exist."
    )
    STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}"
    STATUS_COMMAND_NAME = "status"
    STORE_TRUE_ACTION = "store_true"
    STYLE_TAG_NAME = "style"
    SUBCOMMAND_FIELD_NAME = "subcommand"
    SWITCH_COMMAND_NAME = "switch"
    SWITCH_COMMIT_FILE_MISSING_ERROR_MESSAGE_TEMPLATE = (
        "Commit file missing for branch '{branch_name}'."
    )
    SWITCH_COPY_ERROR_MESSAGE = (
        "Failed to copy commit file during branch switch. Please try again."
    )
    SWITCH_SUCCESS_MESSAGE_TEMPLATE = "Successfully switched to branch '{branch_name}'."

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
    TARGET_BRANCH_NOT_SET_ERROR_MESSAGE = (
        "Target branch not set. Ensure the branch is set by using "
        "Repository*.target.set(foo)"
    )
    TARGET_PATH_NOT_RELATIVE_TO_PARENT_DIRECTORY_ERROR_MESSAGE = (
        "Invalid file path: {target_path} in zip. Please ensure that {target_path} is "
        "inside {destination_resolved}."
    )
    TEMPORARY_DIRECTORY_PREFIX = "sccs_temp_"
    TIMESTAMP_DICT_KEY = "timestamp"

    UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "Uncommitted changes detected. Please clean the working tree before proceeding."
    )
    UNCOMMITTED_CHANGES_FOUND = "Status Report: Uncommitted changes detected."
    UNEXPECTED_ERROR_EXIT_CODE = 2
    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = "Unknown command: {command}"
    UPDATED_BRANCHES_DICT_KEY = "updated_branches"
    URL_ARGUMENT_HELP = "The URL of the hosted repository to clone."
    URL_ARGUMENT_NAME = "url"
    URL_FIELD_NAME = "URL"
    UTF_8 = "utf-8"
    UTILS_ARGUMENT_ERROR_MESSAGE = (
        "Required argument missing. Please provide the required argument."
    )

    VIEW_HTML_DIRECTORY = "view_html"

    WALK_ROOT = "."

    ZIPPING_FILE_ERROR_MESSAGE = "Failed to zip current working directory."
    ZIP_BUFFER_CREATION_FAILED_ERROR_MESSAGE = (
        "Failed to create a buffer for the zipped repository. Please try again."
    )
    ZIP_BUFFER_SEEK_ERROR_MESSAGE = (
        "Failed to reset buffer position. Please try again."
    )
    ZIP_EXTENSION = ".zip"

    # Next constants out of alphabetical order as they use constants that would be
    # defined after them.
    COMMAND_DESCRIPTIONS = MappingProxyType(
        {
            BRANCH_COMMAND_NAME: "Create a new branch, delete, or list branches.",
            CLONE_COMMAND_NAME: "Clone a hosted SCCS repository with a URL.",
            COMMIT_COMMAND_NAME: "Commit changes to the repository.",
            CONFIG_COMMAND_NAME: (
                "Configure a repository's data value (remote, name, email)"
            ),
            DIFF_COMMAND_NAME: (
                "Show differences between the current document and a past commit."
            ),
            HELP_COMMAND_NAME: (
                "Prints a help message listing the available commands and their "
                "descriptions."
            ),
            INIT_COMMAND_NAME: "Initialize a new SCCS repository.",
            LOG_COMMAND_NAME: "Print a list of past commits for the current branch.",
            MERGE_COMMAND_NAME: "Merge the entered branch into the current branch.",
            OPEN_COMMAND_NAME: "Open a commit file and update the current document.",
            PUBLISH_COMMAND_NAME: "Publish a local repository to a hosting service.",
            PULL_COMMAND_NAME: (
                "Pull changes from a remote repository and merge them "
                "into the local repository."
            ),
            PUSH_COMMAND_NAME: (
                "Push changes from the local repository to a remote repository."
            ),
            RESET_COMMAND_NAME: "Delete all uncommitted changes.",
            REVERT_COMMAND_NAME: "Revert the current document to the specified commit.",
            STATUS_COMMAND_NAME: (
                "Check the status of the current document for uncommitted changes."
            ),
            SWITCH_COMMAND_NAME: "Switch between document branches.",
        }
    )

    DEFAULT_BRANCH_DATA = MappingProxyType(
        {
            CURRENT_BRANCH_DICT_KEY: MAIN_BRANCH_NAME,
            BRANCHES_DICT_KEY: [MAIN_BRANCH_NAME],
            UPDATED_BRANCHES_DICT_KEY: [],
        }
    )
