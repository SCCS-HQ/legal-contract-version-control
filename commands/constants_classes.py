#!/usr/bin/env python3

import datetime
from functools import cached_property


class SCCSConstants:
    #region Shared (constants used in multiple command modules)

    #region Shared - Strings (messages, templates, field names, values,
    # separators, attributes, resources, endpoints)

    ACCEPTED_SCHEMES = ("http", "https")
    BRANCH_NAME_FIELD_NAME = "branch name"
    BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' is missing from repository metadata."
    )
    BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE = "Failed to {action} branch."
    BUFFER_SEEK_ERROR_MESSAGE = "Failed to reset buffer position."
    COMMA_SPACE = ", "
    COMMIT_FILE_FIELD_NAME = "commit file hash"
    CONTENT_TYPE_ZIP = "application/zip"
    CREATE_SUBCOMMAND = "create"
    DELETE_SUBCOMMAND = "delete"
    DOCX_EXTENSION = ".docx"
    EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = (
        "{field} cannot be empty. Please provide a valid {field}."
    )
    ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
        "The entered file '{file_path}' does not exist. Please provide"
        " a valid file path to an existing file."
    )
    HISTORY_DICT_KEY = "history"
    INVALID_URL_ERROR_MESSAGE = (
        f"Invalid remote URL provided. The URL must start with one of"
        f" the following schemes: "
        f"{COMMA_SPACE.join(ACCEPTED_SCHEMES)},"
        " and use the format 'http(s)://<host>/<base-path>'. Base path is optional."
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
    ZIPPING_FILE_ERROR_MESSAGE = "Failed to zip current working directory."

    ## cross-file constants (referenced by 2+ command modules)
    ZIP_EXTENSION = ".zip"

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

    # The 3 following constants are not alphabetized because they would
    # be dependencies of earlier constants.
    EMAIL_KEY = "email"
    NAME_KEY = "name"
    REMOTE_KEY = "remote"

    ACCEPTED_CONFIG_KEYS = (REMOTE_KEY, NAME_KEY, EMAIL_KEY)
    AUTHOR_DICT_KEY = "author"
    BRANCHES_DICT_KEY = "branches"
    COMMIT_ORDER_DICT_KEY = "commit_order"

    CURRENT_BRANCH_DICT_KEY = "current_branch"


    HEX_DIGITS = "0123456789abcdef"
    HTTP_OBJECTS_DICT_KEY = "objects"
    INVALID_KEY_ERROR_MESSAGE = (
        f"Invalid configuration key provided. Accepted keys are:"
        f" {COMMA_SPACE.join(ACCEPTED_CONFIG_KEYS)}."
    )
    LATEST_COMMIT_DICT_KEY = "latest_commit"
    LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
    LOG_DICT_KEY = "log"
    MESSAGE_DICT_KEY = "message"

    TIMESTAMP_DICT_KEY = "timestamp"
    UPDATED_BRANCHES_DICT_KEY = "updated_branches"

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
        "merge": "Merge the entered branch into the current branch.",
        "open": "Open a commit file and update the current document.",
        "publish": "Publish a local repository to a hosting service.",
        "pull": "Pull changes from a remote repository and merge them"
        " into the local repository.",
        "push": "Push changes from the local repository to a remote repository.",
        "revert": "Revert the current document to the specified commit.",
        "reset": "Delete all uncommitted changes.",
        "switch": "Switch between document branches.",
        "status": "Check the status of the current document for uncommitted changes.",
    }

    #endregion

    #region Shared - File I/O

    EMPTY_STRING = ""
    JSON_EXTENSION = ".json"
    NEWLINE = "\n"
    UTF_8 = "utf-8"

    #endregion

    #region Shared - Runtime

    @cached_property
    def PROGRAM_START_TIME(self) -> str:
        return datetime.datetime.now().isoformat()

    #endregion

    #endregion

    #region branch.py

    ## strings - subcommands / templates / values
    ACCEPTED_SUBCOMMANDS = ("create", "delete", "list")
    BRANCHES_DIR_LIST_HEADER = "Branches:"
    BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' already exists."
    )
    BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' created from '{current_branch_name}'"
        " successfully."
    )

    ## strings - validation / argument errors
    BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = (
        "Branch '{branch_name}' deleted successfully."
    )

    ## strings - branch existence / deletion errors
    COMMIT_AUTHOR_TEMPLATE = "{name} <{email}>"
    CURRENT_BRANCH_DELETION_ERROR_MESSAGE = (
        "Cannot delete the current branch. Switch branches first."
    )

    ## strings - success messages
    CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
    INVALID_SUBCOMMAND_ERROR_MESSAGE = (
        "Invalid subcommand provided. Accepted subcommands are:"
        " create, delete, list."
    )

    ## strings - rollback / update errors
    LIST_SUBCOMMAND = "list"

    ## strings - listing messages
    OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"
    ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE = (
        "Failed to rollback metadata after failure for branch"
        " '{branch_name}'."
    )
    SUBCOMMAND_FIELD_NAME = "subcommand"

    ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
    WALK_ROOT = "."

    #endregion

    #region clone.py

    ## strings - endpoints and timeouts
    CLONE_ENDPOINT = "/clone/"

    ## strings - error messages
    CLONE_SUCCESS_MESSAGE = "Repository cloned successfully."
    HTTP_REQUEST_ERROR_MESSAGE = "Failed to request repository from the remote url."

    ## strings - status / success messages
    INVALID_ENDING_ERROR_MESSAGE = (
        f"Invalid remote URL provided. Please provide a valid URL"
        f" ending with '{CLONE_ENDPOINT}'."
    )

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

    # The 2 following constants are not alphabetized because they would
    # be dependencies of earlier constants.
    ## strings - error messages
    REPOS_PATH_SEGMENT = "repos"

    ## strings - success messages
    REQUIRED_PATH_ENDING_TEMPLATE = f"/{REPOS_PATH_SEGMENT}/{{repo_name}}"

    ## strings - repos url part
    CONFIG_SUCCESS_MESSAGE_TEMPLATE = (
        "Configuration '{key}' set to '{value}' successfully."
    )
    INVALID_PATH_ENDING_ERROR_MESSAGE = (
        f"API URL must end with '{REQUIRED_PATH_ENDING_TEMPLATE}'."
    )
    INVALID_REPO_NAME_ERROR_MESSAGE = (
        "Invalid repository name. Please ensure the repository is properly "
        "initialized with a valid name."
    )


    #endregion

    #region diff.py

    ## strings - HTML attributes
    CLASS_HTML_ATTRIBUTE = "class"
    DATA_NUMBER_HTML_ATTRIBUTE = "data-number"
    DELETED_HTML_ATTRIBUTE_VALUE = "deleted"
    DELETE_OPCODE = "delete"
    DIFF_SUCCESS_MESSAGE = "Commit diff successfully created."

    ## strings - parser and tags
    HTML_PARSER = "html.parser"
    INSERTED_HTML_ATTRIBUTE_VALUE = "inserted"

    ## strings - opcodes
    INSERT_OPCODE = "insert"
    REPLACE_OPCODE = "replace"
    STYLE_TAG_NAME = "style"

    ## strings - success messages
    TAGS_TO_UNWRAP = (
        "b", "i", "u", "strong", "em", "style", "table", "tr",
        "td", "ol", "ul",
    )

    #endregion

    #region help.py

    ## HELP_MESSAGES is assigned at module level after the class (see bottom of file),
    ## because it depends on COMMANDS_LIST and COMMAND_DESCRIPTIONS which are not yet
    ## bound to the class name during class-body execution.
    HELP_MESSAGES: tuple

    #endregion

    #region init.py

    ## strings - hash segments
    ALREADY_INITIALIZED_ERROR_MESSAGE = (
        "This file has already been initialized with SCCS."
    )
    DEFAULT_BRANCH_DATA = {
        CURRENT_BRANCH_DICT_KEY: MAIN_BRANCH_NAME,
        BRANCHES_DICT_KEY: [MAIN_BRANCH_NAME],
    }
    FULL_COMMIT_HASH_LENGTH = 64
    HTML_BOILERPLATE_TEMPLATE = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'>"
        "{styles}</head><body><div class='center'>"
        "<div id='target'>{html}</div></div></body></html>"
    )

    ## strings - runtime defaults
    HTML_EXTENSION = ".html"

    ## strings - templates and prompts
    INITIAL_COMMIT_DICT_KEY = "initial_commit"

    ## strings - error / status messages
    INITIAL_COMMIT_MESSAGE = (
        "initial commit (This is a default commit message"
        " for initial version)"
    )
    INITIAL_COMMIT_NUMBER_DICT_KEY = "1"
    INITIAL_VERSION_COMMIT_MESSAGE = "initial_version"

    ## dicts
    INIT_SUCCESS_MESSAGE = "SCCS initialization complete."

    ## dict keys
    INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "
    INVALID_FILE_TYPE_ERROR_MESSAGE = (
        "File is not a .docx file. Please provide a valid .docx file."
    )

    #endregion

    #region log.py

    ## strings - display format constants
    LOG_AUTHOR_LABEL = "Author: "
    LOG_COMMIT_FILE_LABEL = "Commit File: "
    LOG_DATE_LABEL = "Date: "
    LOG_MESSAGE_LABEL = "Message: "
    LOG_SEPARATOR = "-" * 30

    #endregion

    #region merge.py

    ## strings - error messages
    CURRENT_BRANCH_MERGE_ERROR_MESSAGE = "Cannot merge the current branch into itself."

    ## strings - success / template messages
    MERGE_COMMIT_MESSAGE_TEMPLATE = "Merged branch '{branch}' into '{current_branch}'."
    MERGE_SUCCESS_MESSAGE_TEMPLATE = (
        "Successfully merged branch '{branch}' into branch"
        " '{current_branch}'."
    )

    #endregion

    #region open.py

    ## strings - output filename template
    OPEN_OUTPUT_FILE_NAME_TEMPLATE = "Opened_DOCX_Commit_{commit_hash}"

    ## strings - success messages
    OPEN_SUCCESS_MESSAGE_TEMPLATE = (
        "Commit '{commit_hash}' has been successfully opened"
        " in {output_file}. It is safe to delete this file."
        " No changes will be lost unless {output_file} is"
        " modified after this point."
    )

    #endregion

    #region publish.py

    ## strings - error messages
    BUFFER_CREATION_FAILED_ERROR_MESSAGE = (
        "Failed to create a buffer for the zipped repository."
        " Please try again."
    )

    ## strings - endpoints
    PUBLISH_ENDPOINT_TEMPLATE = "{base_url}/publish"

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
    CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE = (
        "Push successful, but failed to clear updated branches"
        " list in current branch file."
    )

    ## strings - endpoints
    PUSH_ENDPOINT_TEMPLATE = "{base_url}/push"

    ## strings - error messages
    PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to push to repository {url}."
    PUSH_SUCCESS_MESSAGE_TEMPLATE = "Repository pushed successfully to {url}."

    ## strings - success messages
    TMP_DIR_TEMPLATE = "tmp_{repo_name}"

    #endregion

    #region repository_layout.py

    ## strings - error / status messages
    DIFF_OUTPUT_HTML_FILE = "diff.html"
    INVALID_BRANCH_DATA_ERROR_MESSAGE = (
        "Invalid branch data. Please ensure that the branch data has not been manually"
        "modified and the targeted branch exists."
    )
    INVALID_COMMIT_HASH_ERROR_MESSAGE = (
        "Invalid commit file name. Please provide a shortened, 10 character commit "
        "hash or the full 64 character commit hash as the commit identifier."
    )
    INVALID_COMMIT_HISTORY_DIR_DATA_ERROR_MESSAGE = (
        "Invalid commit history data. Please ensure that the commit data has not"
        "been manually modified."
    )
    MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = (
        "Resource '{resource_name}' is missing from the"
        " repository directory."
    )
    MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE = (
        "Multiple commit files found matching '{commit}'. Please provide a full, "
        "64 character commit hash."
    )
    NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "No uncommitted changes detected. Uncommitted changes are required"
        " before committing."
    )

    ## strings - diff output filename
    TARGET_BRANCH_ATTRIBUTE = "_target_branch"

    ## strings - resource errors
    TARGET_BRANCH_NOT_SET_ERROR_MESSAGE = (
        "Target branch not set. Please chain this method call with a branch "
        "method before calling history_path(). For example,"
        "'repo_layout.main_branch().foo()'."
    )

    ## strings - branch name attribute / extensions
    UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
        "Uncommitted changes detected. Please clean the working tree before proceeding."
    )

    #endregion

    #region reset.py

    ## strings - success / error messages
    RESET_ERROR_MESSAGE = "Failed to reset the document."
    RESET_SUCCESS_MESSAGE = (
        "All uncommitted changes have been deleted. The document"
        " has been reset to the latest commit."
    )

    #endregion

    #region revert.py

    ## strings - error messages
    REVERT_COMMIT_MESSAGE_TEMPLATE = "Reverted document to commit '{commit_hash}'."

    ## strings - success / template messages
    REVERT_SUCCESS_MESSAGE_TEMPLATE = (
        "Document successfully reverted to commit"
        " '{commit_hash}' on commit '{new_commit_hash}'."
    )
    SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
        "Source file '{file_name}' does not exist."
    )

    #endregion

    #region sccs(sh)

    ## strings - extensions
    PYTHON_EXTENSION = ".py"

    ## strings - error messages
    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = (
        f"Unknown command: {{entered_command}}."
        f" Please use {COMMA_SPACE.join(COMMANDS_LIST)}"
        f" along with required arguments."
    )

    #endregion

    #region status.py

    ## strings - status messages
    NO_UNCOMMITTED_CHANGES = "Status Report: No uncommitted changes detected."
    UNCOMMITTED_CHANGES_FOUND = "Status Report: Uncommitted changes detected."

    #endregion

    #region switch.py

    ## strings - success messages
    SWITCH_SUCCESS_MESSAGE_TEMPLATE = "Successfully switched to branch '{branch_name}'."

    #endregion


# --- Module-level post-class setup ---
# These depend on COMMANDS_LIST / COMMAND_DESCRIPTIONS, which are not bound to the
# class name during class-body execution, so they are assigned here once at import.

SCCSConstants.HELP_MESSAGES = (
    "SCCS Help",
    "Available commands:",
) + tuple(
    f"  {SCCSConstants.SCCS_COMMAND_PREFIX}{i}"
    f" - {SCCSConstants.COMMAND_DESCRIPTIONS[i]}"
    for i in SCCSConstants.COMMANDS_LIST
)

_missing_commands = [
    cmd for cmd in SCCSConstants.COMMANDS_LIST
    if cmd not in SCCSConstants.COMMAND_DESCRIPTIONS
]
if _missing_commands:
    raise ValueError(
        f"COMMAND_DESCRIPTIONS is missing entries for:"
        f" {SCCSConstants.COMMA_SPACE.join(_missing_commands)}"
    )


class ErrorWrappers:
    EXPECTED_ERROR_TEMPLATE = "An error occurred:{e}"
    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred:{type_name}: {e}"
