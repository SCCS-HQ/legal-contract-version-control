#!/usr/bin/env python3
"""Constants and classes for SCCS commands."""

import datetime
from functools import cached_property


class SCCSConstants:
    #region Shared (holds all shared sections)

    #region Shared - Strings (messages, templates, field names, values, separators, attributes, resources, endpoints)

    COMMA_SPACE = ", "
    HISTORY_DICT_KEY = "history"
    BRANCH_NAME_FIELD_NAME = "branch name"
    BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' is missing from repository metadata."
    BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE = "Failed to {action} branch."
    BUFFER_SEEK_ERROR_MESSAGE = "Failed to reset buffer position."
    COMMIT_FILE_FIELD_NAME = "commit file hash"
    CONTENT_TYPE_ZIP = "application/zip"
    CREATE_SUBCOMMAND = "create"
    DELETE_SUBCOMMAND = "delete"
    DOCX_EXTENSION = ".docx"
    EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = "{field} cannot be empty. Please provide a valid {field}."
    ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
        "The entered file '{file_path}' does not exist. Please provide a valid file path to an existing file."
    )
    POST_FILE_FIELD_NAME = "file"
    PATH_SEPARATOR = "/"
    REQUIRED_PATH_ENDING_TEMPLATE = "/repos/{repo_name}"
    INVALID_PATH_ENDING_ERROR_MESSAGE = (
        f"API URL must end with '{REQUIRED_PATH_ENDING_TEMPLATE}'."
    )
    ACCEPTED_SCHEMES = ("http", "https")
    INVALID_URL_ERROR_MESSAGE = (
        f"Invalid remote URL provided. The URL must start with one of the following schemes: "
        f"{COMMA_SPACE.join(ACCEPTED_SCHEMES)},"
        "and use the format 'http(s)://<host>/<base-path>'. Base path is optional."
    )
    REPOSITORY_NAME_FIELD_NAME = "repository name"
    RGLOB_ALL_FILES_PATTERN = "*"
    STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}"
    UNZIP_FAILED_ERROR_MESSAGE = (
        "Failed to unzip repository file. Please try again or ensure the zip is valid."
    )
    ZIP_EXTENSION = ".zip"
    ZIPPING_FILE_ERROR_MESSAGE = "Failed to zip current working directory."
    MAIN_BRANCH_NAME = "main"

    ## cross-file constants (referenced by 2+ command modules)
    SCCS_COMMAND_PREFIX = "sccs"

    #endregion

    #region Shared - Numbers

    COMMIT_HASH_DISPLAY_LENGTH = 10
    HTTP_TIMEOUT_SECONDS = 60
    MAX_FILE_READ_SIZE = 64 * 1024

    #endregion

    #region Shared - Paths (directories)

    BRANCHES_DIR = "branches"
    COMMIT_FILE_HASH_DIR = "commit_file_hash"
    COMMIT_MESSAGES_DIR = "commit_messages"
    CONFIG_DIR = "config"
    CURRENT_BRANCH_DIR = "current_branch"
    DOCX_DIR = "docx"
    HISTORY_DIR = "history"
    HTML_DIR = "html"
    OBJECTS_DIR = "objects"
    SCCS_DIR = ".sccs"
    VIEW_HTML_DIR = "view_html"

    #endregion

    #region Shared - Paths (files)

    COMMIT_FILE_HASH_JSON_FILE = "commit_file_hash.json"
    COMMIT_MESSAGES_JSON_FILE = "commit_messages.json"
    CONFIG_JSON_FILE = "config.json"
    CURRENT_BRANCH_JSON_FILE = "current_branch.json"
    HISTORY_JSON_FILE = "history.json"

    #endregion

    #region Shared - Configuration Values (keys, schemes, dict keys)

    REMOTE_KEY = "remote"
    NAME_KEY = "name"
    EMAIL_KEY = "email"
    ACCEPTED_CONFIG_KEYS = (REMOTE_KEY, NAME_KEY, EMAIL_KEY)

    INVALID_KEY_ERROR_MESSAGE = (
        f"Invalid configuration key provided. Accepted keys are: {COMMA_SPACE.join(ACCEPTED_CONFIG_KEYS)}."
    )

    AUTHOR_DICT_KEY = "author"
    BRANCHES_DICT_KEY = "branches"
    COMMIT_ORDER_DICT_KEY = "commit_order"
    CURRENT_BRANCH_DICT_KEY = "current_branch"
    LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
    LOG_DICT_KEY = "log"
    MESSAGE_DICT_KEY = "message"
    TIMESTAMP_DICT_KEY = "timestamp"
    UPDATED_BRANCHES_DICT_KEY = "updated_branches"
    HTTP_OBJECTS_DICT_KEY = "objects"

    #endregion

    #region Shared - HTML

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


    #endregion

    #region Shared - Lists

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

    #endregion

    #region Shared - Dicts

    COMMAND_DESCRIPTIONS = {
        "branch": "Create a new branch, delete, or list branches.",
        "clone": "Clone a hosted SCCS repository with a URL.",
        "commit": "Commit changes to the repository.",
        "config": "Configure a repository's data value (remote, name, email)",
        "diff": "Show differences between the current document and a past commit.",
        "help": "Print this help message.",
        "init": "Initialize a new SCCS repository.",
        "log": "Print a list of past commits for the current branch.",
        "open": "Open a commit file and update the current document.",
        "publish": "Publish a local repository to a hosting service.",
        "pull": "Pull changes from a remote repository and merge them into the local repository.",
        "push": "Push changes from the local repository to a remote repository.",
        "revert": "Revert the current document to the specified commit.",
        "reset": "Delete all uncommitted changes.",
        "switch": "Switch between document branches.",
        "status": "Check the status of the current document for uncommitted changes.",
        "merge": "Merge the entered branch into the current branch.",
    }

    #endregion

    #endregion

    #region branch.py

    ## strings - subcommands / templates / values
    WALK_ROOT = "."
    COMMIT_AUTHOR_TEMPLATE = "{name} <{email}>"
    LIST_SUBCOMMAND = "list"
    ACCEPTED_SUBCOMMANDS = ("create", "delete", "list")

    ## strings - validation / argument errors
    INVALID_SUBCOMMAND_ERROR_MESSAGE = "Invalid subcommand provided. Accepted subcommands are: create, delete, list."

    ## strings - branch existence / deletion errors
    BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' already exists."
    CURRENT_BRANCH_DELETION_ERROR_MESSAGE = "Cannot delete the current branch. Switch branches first."

    ## strings - success messages
    BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' created from '{current_branch_name}' successfully."
    BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' deleted successfully."

    ## strings - rollback / update errors
    ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to rollback metadata after failure for branch '{branch_name}'."

    ## strings - listing messages
    BRANCHES_DIR_LIST_HEADER = "Branches:"
    CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
    OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"

    ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
    SUBCOMMAND_FIELD_NAME = "subcommand"

    #endregion

    #region clone.py

    ## strings - endpoints and timeouts
    CLONE_ENDPOINT = "/clone/"

    ## strings - error messages
    INVALID_ENDING_ERROR_MESSAGE = (
        f"Invalid remote URL provided. Please provide a valid URL ending with '{CLONE_ENDPOINT}'."
    )
    HTTP_REQUEST_ERROR_MESSAGE = "Failed to request repository from the remote url."

    ## strings - status / success messages
    CLONE_SUCCESS_MESSAGE = "Repository cloned successfully."

    ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
    URL_FIELD_NAME = "URL"

    #endregion

    #region commit.py

    ## strings - success / error messages
    COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = "Commit {sha_hash} created successfully."
    COMMIT_FAILURE_ERROR_MESSAGE = "Failed to commit changes."

    ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
    COMMIT_MESSAGE_FIELD_NAME = "commit message"

    #endregion

    #region config.py

    ## strings - repos url part
    REPOS_PATH_SEGMENT = "repos"

    ## strings - error messages
    INVALID_REPO_NAME_ERROR_MESSAGE = (
        "Invalid repository name. Please ensure the repository is properly "
        "initialized with a valid name."
    )

    ## strings - success messages
    CONFIG_SUCCESS_MESSAGE_TEMPLATE = "Configuration '{key}' set to '{value}' successfully."

    #endregion

    #region diff.py

    ## strings - HTML attributes
    STYLE_TAG_NAME = "style"
    DATA_NUMBER_HTML_ATTRIBUTE = "data-number"
    CLASS_HTML_ATTRIBUTE = "class"
    DELETED_HTML_ATTRIBUTE_VALUE = "deleted"
    INSERTED_HTML_ATTRIBUTE_VALUE = "inserted"

    ## strings - parser and tags
    HTML_PARSER = "html.parser"
    TAGS_TO_UNWRAP = ("b", "i", "u", "strong", "em", "style", "table", "tr", "td", "ol", "ul")

    ## strings - opcodes
    REPLACE_OPCODE = "replace"
    INSERT_OPCODE = "insert"
    DELETE_OPCODE = "delete"

    ## strings - success messages
    DIFF_SUCCESS_MESSAGE = "Commit diff successfully created."

    #endregion

    #region help.py

    ## HELP_MESSAGES is assigned at module level after the class (see bottom of file),
    ## because it depends on COMMANDS_LIST and COMMAND_DESCRIPTIONS which are not yet
    ## bound to the class name during class-body execution.

    #endregion

    #region init.py

    ## strings - hash segments
    EMPTY_STRING = ""
    SPACE = " "
    HTML_BOILERPLATE_TEMPLATE = "<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head><body><div class='center'><div id='target'>{html}</div></div></body></html>"
    HEX_DIGITS = "0123456789abcdef"
    FULL_COMMIT_HASH_LENGTH = 64
    HTML_EXTENSION = ".html"
    INITIAL_VERSION_COMMIT_MESSAGE = "initial_version"

    ## strings - runtime defaults
    INITIAL_COMMIT_MESSAGE = "initial commit (This is a default commit message for initial version)"

    ## strings - templates and prompts
    INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "

    ## strings - error / status messages
    ALREADY_INITIALIZED_ERROR_MESSAGE = "This file has already been initialized with SCCS."
    INVALID_FILE_TYPE_ERROR_MESSAGE = "File is not a .docx file. Please provide a valid .docx file."
    INIT_SUCCESS_MESSAGE = "SCCS initialization complete."

    ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
    DOCUMENT_PATH_FIELD_NAME = "document path"

    ## numbers
    LOG_SEPARATOR_LENGTH = 30

    ## dicts
    DEFAULT_BRANCH_DATA = {
        CURRENT_BRANCH_DICT_KEY: MAIN_BRANCH_NAME,
        BRANCHES_DICT_KEY: [MAIN_BRANCH_NAME],
    }

    ## dict keys
    INITIAL_COMMIT_DICT_KEY = "initial_commit"
    INITIAL_COMMIT_NUMBER_DICT_KEY = "1"

    #endregion

    #region log.py

    ## strings - display format constants
    LOG_SEPARATOR = "-" * 30
    LOG_COMMIT_FILE_LABEL = "Commit File: "
    LOG_AUTHOR_LABEL = "Author: "
    LOG_DATE_LABEL = "Date: "
    LOG_MESSAGE_LABEL = "Message: "

    #endregion

    #region merge.py

    ## strings - error messages
    CURRENT_BRANCH_MERGE_ERROR_MESSAGE = "Cannot merge the current branch into itself."

    ## strings - success / template messages
    MERGE_COMMIT_MESSAGE_TEMPLATE = "Merged branch '{branch}' into '{current_branch}'."
    MERGE_SUCCESS_MESSAGE_TEMPLATE = "Successfully merged branch '{branch}' into branch '{current_branch}'."

    #endregion

    #region open.py

    ## strings - output filename template
    OPEN_OUTPUT_FILE_NAME_TEMPLATE = "Opened_DOCX_Commit_{commit_hash}"

    ## strings - success messages
    OPEN_SUCCESS_MESSAGE_TEMPLATE = "Commit '{commit_hash}' has been successfully opened in {output_file}. It is safe to delete this file. No changes will be lost unless {output_file} is modified after this point."

    #endregion

    #region publish.py

    ## strings - error messages
    BUFFER_CREATION_FAILED_ERROR_MESSAGE = "Failed to create a buffer for the zipped repository. Please try again."

    ## strings - content type / endpoints / field names
    CONTENT_TYPE_JSON = "application/json"
    PUBLISH_ENDPOINT_TEMPLATE = "{base_url}/publish"
    POST_DATA_FIELD_NAME = "data"

    ## strings - success messages
    PUBLISH_SUCCESS_MESSAGE_TEMPLATE = "Repository published successfully to {url}."

    #endregion

    #region pull.py

    ## strings - endpoints / success messages
    PULL_ENDPOINT_TEMPLATE = "{base_url}/pull"
    PULL_SUCCESS_MESSAGE_TEMPLATE = "Repository pulled successfully from {url}."

    #endregion

    #region push.py

    ## strings - extensions / dir templates
    JSON_EXTENSION = ".json"
    TMP_DIR_TEMPLATE = "tmp_{repo_name}"

    ## strings - endpoints
    PUSH_ENDPOINT_TEMPLATE = "{base_url}/push"

    ## strings - error messages
    PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to push to repository {url}."
    CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE = "Push successful, but failed to clear updated branches list in current " "branch file."

    ## strings - success messages
    PUSH_SUCCESS_MESSAGE_TEMPLATE = "Repository pushed successfully to {url}."

    #endregion

    #region repository_layout.py

    ## strings - error / status messages
    TARGET_BRANCH_NOT_SET_ERROR_MESSAGE = (
        "Target branch not set. Please chain this method call with a branch "
        "method before calling history_path(). For example,"
        "'repo_layout.main_branch().foo()'."
    )
    INVALID_COMMIT_HASH_ERROR_MESSAGE = (
        "Invalid commit file name. Please provide a shortened, 10 character commit "
        "hash or the full 64 character commit hash as the commit identifier."
    )
    MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Multiple commit files found matching '{commit}'. Please provide a full, "
        "64 character commit hash."
    )
    INVALID_COMMIT_HISTORY_DIR_DATA_ERROR_MESSAGE = (
        "Invalid commit history data. Please ensure that the commit data has not"
        "been manually modified."
    )
    INVALID_BRANCH_DATA_ERROR_MESSAGE = (
        "Invalid branch data. Please ensure that the branch data has not been manually"
        "modified and the targeted branch exists."
    )
    UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "Uncommitted changes detected. Please clean the working tree before proceeding."
    )
    NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "No uncommitted changes detected. Uncommitted changes are required before committing."
    )

    ## strings - diff output filename
    DIFF_OUTPUT_HTML_FILE = "diff.html"

    ## strings - resource errors
    MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = "Resource '{resource_name}' is missing from the repository directory."

    ## strings - branch name attribute / extensions
    BRANCH_NAME_ATTRIBUTE = "branch_name"
    TMP_EXTENSION = ".tmp"

    #endregion

    #region reset.py

    ## strings - success / error messages
    RESET_SUCCESS_MESSAGE = "All uncommitted changes have been deleted. The document has been reset to the latest commit."
    RESET_ERROR_MESSAGE = "Failed to reset the document."

    #endregion

    #region revert.py

    ## strings - error messages
    NEWLINE = "\n"
    UTF_8 = "utf-8"
    SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = "Source file '{file_name}' does not exist."

    ## strings - success / template messages
    REVERT_SUCCESS_MESSAGE_TEMPLATE = "Document successfully reverted to commit '{commit_hash}' on commit '{new_commit_hash}'."
    REVERT_COMMIT_MESSAGE_TEMPLATE = "Reverted document to commit '{commit_hash}'."

    #endregion

    #region sccs(sh)

    ## strings - extensions
    PYTHON_EXTENSION = ".py"

    ## strings - error messages
    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = f"Unknown command: {{entered_command}}. Please use {COMMA_SPACE.join(COMMANDS_LIST)} along with required arguments."

    #endregion

    #region status.py

    ## strings - status messages
    UNCOMMITTED_CHANGES_FOUND = "Status Report: Uncommitted changes detected."
    NO_UNCOMMITTED_CHANGES = "Status Report: No uncommitted changes detected."

    #endregion

    #region switch.py

    ## strings - success messages
    SWITCH_SUCCESS_MESSAGE_TEMPLATE = "Successfully switched to branch '{branch_name}'."

    #endregion

    @cached_property
    def PROGRAM_START_TIME(self) -> str:
        """Return the program start time in a human-readable format."""
        return datetime.datetime.now().isoformat()


# --- Module-level post-class setup ---
# These depend on COMMANDS_LIST / COMMAND_DESCRIPTIONS, which are not bound to the
# class name during class-body execution, so they are assigned here once at import.

SCCSConstants.HELP_MESSAGES = (
    "SCCS Help",
    "Available commands:",
) + tuple(
    f"  {SCCSConstants.SCCS_COMMAND_PREFIX}{i} - {SCCSConstants.COMMAND_DESCRIPTIONS[i]}"
    for i in SCCSConstants.COMMANDS_LIST
)

_missing_commands = [cmd for cmd in SCCSConstants.COMMANDS_LIST if cmd not in SCCSConstants.COMMAND_DESCRIPTIONS]
if _missing_commands:
    raise ValueError(
        f"COMMAND_DESCRIPTIONS is missing entries for: {COMMA_SPACE.join(_missing_commands)}"
    )


class ErrorWrappers:
    EXPECTED_ERROR_TEMPLATE = "An error occurred:{e}"
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred:{type_name}: {e}"
