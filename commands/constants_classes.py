#!/usr/bin/env python3
"""Constants and classes for SCCS commands."""

import datetime
from functools import cached_property


class SCCSConstants:
    def __init__(self):

        #region Shared Constants (referenced by 2+ command modules)

        #region Shared - Strings (messages, templates, field names, values, separators, attributes, resources, endpoints)

        self.SINGLE_QUOTE_COMMA_SPACE_SINGLE_QUOTE = ', '
        self.HISTORY_DICT_KEY = "history"
        self.BRANCH_NAME_FIELD_NAME = "branch name"
        self.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' is missing from repository metadata."
        self.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE = "Failed to {action} branch."
        self.BUFFER_SEEK_ERROR_MESSAGE = "Failed to reset buffer position."
        self.COMMIT_FILE_FIELD_NAME = "commit file hash"
        self.CONTENT_TYPE_ZIP = "application/zip"
        self.CREATE_SUBCOMMAND = "create"
        self.DELETE_SUBCOMMAND = "delete"
        self.DOCX_EXTENSION = ".docx"
        self.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = "{field} cannot be empty. Please provide a valid {field}."
        self.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
            "The entered file '{file_path}' does not exist. Please provide a valid file path to an existing file."
        )
        self.POST_FILE_FIELD_NAME = "file"
        self.PATH_SEPARATOR = "/"
        self.HTTP_POST_REQUEST_ERROR_MESSAGE_TEMPLATE = "Failed to post repository to {url}."
        self.INVALID_PATH_ENDING_ERROR_MESSAGE = "API URL must end with '/repos/<repo_name>'."
        self.INVALID_URL_ERROR_MESSAGE = (
            "Invalid remote URL provided. The URL must start with 'http://' or 'https://',"
            "and use the format 'http(s)://<host>/<base-path>'. Base path is optional."
        )
        self.REQUIRED_PATH_ENDING_TEMPLATE = "/repos/{repo_name}"
        self.REPOSITORY_NAME_FIELD_NAME = "repository name"
        self.RGLOB_ALL_FILES_PATTERN = "*"
        self.STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}"
        self.UNZIP_FAILED_ERROR_MESSAGE = (
            "Failed to unzip repository file. Please try again or ensure the zip is valid."
        )
        self.ZIP_EXTENSION = ".zip"
        self.ZIPPING_FILE_ERROR_MESSAGE = "Failed to zip current working directory."
        self.MAIN_BRANCH_NAME = "main"
        self.PROGRAM_START_TIME = self._program_start_time

        ## cross-file constants (referenced by 2+ command modules)
        self.SCCS_COMMAND_PREFIX = "sccs"
        self.COMMA_SPACE = ", "

        #endregion

        #region Shared - Numbers

        self.COMMIT_HASH_DISPLAY_LENGTH = 10
        self.HTTP_TIMEOUT_SECONDS = 60
        self.MAX_FILE_READ_SIZE = 64 * 1024

        #endregion

        #region Shared - Paths (directories)

        self.BRANCHES_DIR = "branches"
        self.COMMIT_FILE_HASH_DIR = "commit_file_hash"
        self.COMMIT_MESSAGES_DIR = "commit_messages"
        self.CONFIG_DIR = "config"
        self.CURRENT_BRANCH_DIR = "current_branch"
        self.DOCX_DIR = "docx"
        self.HISTORY_DIR = "history"
        self.HTML_DIR = "html"
        self.OBJECTS_DIR = "objects"
        self.SCCS_DIR = ".sccs"
        self.VIEW_HTML_DIR = "view_html"

        #endregion

        #region Shared - Paths (files)

        self.COMMIT_FILE_HASH_JSON_FILE = "commit_file_hash.json"
        self.COMMIT_MESSAGES_JSON_FILE = "commit_messages.json"
        self.CONFIG_JSON_FILE = "config.json"
        self.CURRENT_BRANCH_JSON_FILE = "current_branch.json"
        self.HISTORY_JSON_FILE = "history.json"

        #endregion

        #region Shared - Configuration Values (keys, schemes, dict keys)

        self.REMOTE_KEY = "remote"
        self.NAME_KEY = "name"
        self.EMAIL_KEY = "email"
        self.ACCEPTED_CONFIG_KEYS = (self.REMOTE_KEY, self.NAME_KEY, self.EMAIL_KEY)
        self.ACCEPTED_SCHEMES = ("http", "https")

        self.INVALID_KEY_ERROR_MESSAGE = (
            f"Invalid configuration key provided. Accepted keys are: {self.SINGLE_QUOTE_COMMA_SPACE_SINGLE_QUOTE.join(self.ACCEPTED_CONFIG_KEYS)}."
        )

        self.AUTHOR_DICT_KEY = "author"
        self.BRANCHES_DICT_KEY = "branches"
        self.COMMIT_ORDER_DICT_KEY = "commit_order"
        self.CURRENT_BRANCH_DICT_KEY = "current_branch"
        self.LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
        self.LOG_DICT_KEY = "log"
        self.MESSAGE_DICT_KEY = "message"
        self.TIMESTAMP_DICT_KEY = "timestamp"
        self.UPDATED_BRANCHES_DICT_KEY = "updated_branches"
        self.HTTP_OBJECTS_DICT_KEY = "objects"

        #endregion

        #region Shared - File I/O (modes, encoding, newline)


        #endregion

        #region Shared - HTML

        self.DEFAULT_HTML_STYLES = """
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

        #endregion

        #region Shared - Lists

        self.COMMANDS_LIST = [
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
        ]

        #endregion

        #region Shared - Dicts

        self.COMMAND_DESCRIPTIONS = {
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

        #region branch.py

        ## strings - subcommands / templates / values
        self.WALK_ROOT = "."
        self.COMMIT_AUTHOR_TEMPLATE = "{name} <{email}>"
        self.LIST_SUBCOMMAND = "list"
        self.ACCEPTED_SUBCOMMANDS = ("create", "delete", "list")

        ## strings - validation / argument errors
        self.INVALID_SUBCOMMAND_ERROR_MESSAGE = "Invalid subcommand provided. Accepted subcommands are: create, delete, list."

        ## strings - branch existence / deletion errors
        self.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' already exists."
        self.CURRENT_BRANCH_DELETION_ERROR_MESSAGE = "Cannot delete the current branch. Switch branches first."

        ## strings - success messages
        self.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' created from '{current_branch_name}' successfully."
        self.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' deleted successfully."

        ## strings - rollback / update errors
        self.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to rollback metadata after failure for branch '{branch_name}'."

        ## strings - listing messages
        self.BRANCHES_DIR_LIST_HEADER = "Branches:"
        self.CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
        self.OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"

        ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.SUBCOMMAND_FIELD_NAME = "subcommand"

        #endregion

        #region clone.py

        ## strings - endpoints and timeouts
        self.CLONE_ENDPOINT = "/clone/"

        ## strings - error messages
        self.INVALID_ENDING_ERROR_MESSAGE = (
            "Invalid remote URL provided. Please provide a valid URL ending with "
            "'/clone/'."
        )
        self.HTTP_REQUEST_ERROR_MESSAGE = "Failed to request repository from the remote url."

        ## strings - status / success messages
        self.CLONE_SUCCESS_MESSAGE = "Repository cloned successfully."

        ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.URL_FIELD_NAME = "URL"

        #endregion

        #region commit.py

        ## strings - success / error messages
        self.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = "Commit {sha_hash} created successfully."
        self.COMMIT_FAILURE_ERROR_MESSAGE = "Failed to commit changes."

        ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.COMMIT_MESSAGE_FIELD_NAME = "commit message"

        #endregion

        #region config.py

        ## strings - repos url part
        self.REPOS_PATH_SEGMENT = "repos"

        ## strings - error messages
        self.INVALID_REPO_NAME_ERROR_MESSAGE = (
            "Invalid repository name. Please ensure the repository is properly "
            "initialized with a valid name."
        )

        ## strings - success messages
        self.CONFIG_SUCCESS_MESSAGE_TEMPLATE = "Configuration '{key}' set to '{value}' successfully."

        #endregion

        #region diff.py

        ## strings - HTML attributes
        self.STYLE_TAG_NAME = "style"
        self.DATA_NUMBER_HTML_ATTRIBUTE = "data-number"
        self.CLASS_HTML_ATTRIBUTE = "class"
        self.DELETED_HTML_ATTRIBUTE_VALUE = "deleted"
        self.INSERTED_HTML_ATTRIBUTE_VALUE = "inserted"

        ## strings - parser and tags
        self.HTML_PARSER = "html.parser"
        self.TAGS_TO_UNWRAP = ("b", "i", "u", "strong", "em", "style", "table", "tr", "td", "ol", "ul")

        ## strings - opcodes
        self.REPLACE_OPCODE = "replace"
        self.INSERT_OPCODE = "insert"
        self.DELETE_OPCODE = "delete"

        ## strings - success messages
        self.DIFF_SUCCESS_MESSAGE = "Commit diff successfully created."

        #endregion

        #region help.py

        ## lists
        self.HELP_MESSAGES = [
            "SCCS Help",
            "Available commands:"
        ] + [
            f"  {self.SCCS_COMMAND_PREFIX}{i} - {self.COMMAND_DESCRIPTIONS[i]}" for i in self.COMMANDS_LIST
        ]

        #endregion

        #region init.py

        ## strings - hash segments
        self.EMPTY_STRING = ""
        self.SPACE = " "
        self.HTML_BOILERPLATE_TEMPLATE = "<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head><body><div class='center'><div id='target'>{html}</div></div></body></html>"
        self.HEX_DIGITS = "0123456789abcdef"
        self.FULL_COMMIT_HASH_LENGTH = 64
        self.HTML_EXTENSION = ".html"
        self.INITIAL_VERSION_COMMIT_MESSAGE = "initial_version"

        ## strings - runtime defaults
        self.INITIAL_COMMIT_MESSAGE = "initial commit (This is a default commit message for initial version)"

        ## strings - templates and prompts
        self.INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "

        ## strings - error / status messages
        self.ALREADY_INITIALIZED_ERROR_MESSAGE = "This file has already been initialized with SCCS."
        self.INVALID_FILE_TYPE_ERROR_MESSAGE = "File is not a .docx file. Please provide a valid .docx file."
        self.INIT_SUCCESS_MESSAGE = "SCCS initialization complete."

        ## strings - format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.DOCUMENT_PATH_FIELD_NAME = "document path"

        ## numbers
        self.LOG_SEPARATOR_LENGTH = 30

        ## dicts
        self.DEFAULT_BRANCH_DATA = {
            self.CURRENT_BRANCH_DICT_KEY: self.MAIN_BRANCH_NAME,
            self.BRANCHES_DICT_KEY: [self.MAIN_BRANCH_NAME],
        }

        ## dict keys
        self.INITIAL_COMMIT_DICT_KEY = "initial_commit"
        self.INITIAL_COMMIT_NUMBER_DICT_KEY = "1"

        #endregion

        #region log.py

        ## strings - display format constants
        self.LOG_SEPARATOR = "-" * 30
        self.LOG_COMMIT_FILE_LABEL = "Commit File: "
        self.LOG_AUTHOR_LABEL = "Author: "
        self.LOG_DATE_LABEL = "Date: "
        self.LOG_MESSAGE_LABEL = "Message: "

        #endregion

        #region merge.py

        ## strings - error messages
        self.CURRENT_BRANCH_MERGE_ERROR_MESSAGE = "Cannot merge the current branch into itself."

        ## strings - success / template messages
        self.MERGE_COMMIT_MESSAGE_TEMPLATE = "Merged branch '{branch}' into '{current_branch}'."
        self.MERGE_SUCCESS_MESSAGE_TEMPLATE = "Successfully merged branch '{branch}' into branch '{current_branch}'."

        #endregion

        #region open.py

        ## strings - output filename template
        self.OPEN_OUTPUT_FILE_NAME_TEMPLATE = "Opened_DOCX_Commit_{commit_hash}"

        ## strings - success messages
        self.OPEN_SUCCESS_MESSAGE_TEMPLATE = "Commit '{commit_hash}' has been successfully opened in {output_file}. It is safe to delete this file. No changes will be lost unless {output_file} is modified after this point."

        #endregion

        #region publish.py

        ## strings - error messages
        self.BUFFER_CREATION_FAILED_ERROR_MESSAGE = "Failed to create a buffer for the zipped repository. Please try again."

        ## strings - content type / endpoints / field names
        self.CONTENT_TYPE_JSON = "application/json"
        self.PUBLISH_ENDPOINT_TEMPLATE = "{base_url}/publish"
        self.POST_DATA_FIELD_NAME = "data"

        ## strings - success messages
        self.PUBLISH_SUCCESS_MESSAGE_TEMPLATE = "Repository published successfully to {url}."

        #endregion

        #region pull.py

        ## strings - endpoints / success messages
        self.PULL_ENDPOINT_TEMPLATE = "{base_url}/pull"
        self.PULL_SUCCESS_MESSAGE_TEMPLATE = "Repository pulled successfully from {url}."

        #endregion

        #region push.py

        ## strings - extensions / dir templates
        self.JSON_EXTENSION = ".json"
        self.TMP_DIR_TEMPLATE = "tmp_{repo_name}"

        ## strings - endpoints
        self.PUSH_ENDPOINT_TEMPLATE = "{base_url}/push"

        ## strings - error messages
        self.PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to push to repository {url}."
        self.CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE = "Push successful, but failed to clear updated branches list in current " "branch file."

        ## strings - success messages
        self.PUSH_SUCCESS_MESSAGE_TEMPLATE = "Repository pushed successfully to {url}."

        #endregion

        #region repository_layout.py

        ## strings - error / status messages
        self.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE = (
            "Target branch not set. Please chain this method call with a branch "
            "method before calling history_path(). For example,"
            "'repo_layout.main_branch().foo()'."
        )
        self.INVALID_COMMIT_HASH_ERROR_MESSAGE = (
            "Invalid commit file name. Please provide a shortened, 10 character commit "
            "hash or the full 64 character commit hash as the commit identifier."
        )
        self.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE = (
            "Multiple commit files found matching '{commit}'. Please provide a full, "
            "64 character commit hash."
        )
        self.INVALID_COMMIT_HISTORY_DIR_DATA_ERROR_MESSAGE = (
            "Invalid commit history data. Please ensure that the commit data has not"
            "been manually modified."
        )
        self.INVALID_BRANCH_DATA_ERROR_MESSAGE = (
            "Invalid branch data. Please ensure that the branch data has not been manually"
            "modified and the targeted branch exists."
        )
        self.UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
            "Uncommitted changes detected. Please clean the working tree before proceeding."
        )
        self.NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = (
            "No uncommitted changes detected. Uncommitted changes are required before committing."
        )

        ## strings - diff output filename
        self.DIFF_OUTPUT_HTML_FILE = "diff.html"

        ## strings - resource errors
        self.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = "Resource '{resource_name}' is missing from the repository directory."

        ## strings - branch name attribute / extensions
        self.BRANCH_NAME_ATTRIBUTE = "branch_name"
        self.TMP_EXTENSION = ".tmp"

        #endregion

        #region reset.py

        ## strings - success / error messages
        self.RESET_SUCCESS_MESSAGE = "All uncommitted changes have been deleted. The document has been reset to the latest commit."
        self.RESET_ERROR_MESSAGE = "Failed to reset the document."

        #endregion

        #region revert.py

        ## strings - error messages
        self.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = "Source file '{file_name}' does not exist."

        ## strings - success / template messages
        self.REVERT_SUCCESS_MESSAGE_TEMPLATE = "Document successfully reverted to commit '{commit_hash}' on commit '{new_commit_hash}'."
        self.REVERT_COMMIT_MESSAGE_TEMPLATE = "Reverted document to commit '{commit_hash}'."

        #endregion

        #region sccs(sh)

        ## strings - extensions
        self.PYTHON_EXTENSION = ".py"

        ## strings - error messages
        self.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = f"Unknown command: {{entered_command}}. Please use {self.COMMA_SPACE.join(self.COMMANDS_LIST)} along with required arguments."

        missing_commands = [cmd for cmd in self.COMMANDS_LIST if cmd not in self.COMMAND_DESCRIPTIONS]
        if missing_commands:
            raise ValueError(
                f"COMMAND_DESCRIPTIONS is missing entries for: {', '.join(missing_commands)}"
            )

        #endregion

        #region status.py

        ## strings - status messages
        self.UNCOMMITTED_CHANGES_FOUND = "Status Report: Uncommitted changes detected."
        self.NO_UNCOMMITTED_CHANGES = "Status Report: No uncommitted changes detected."

        #endregion

        #region switch.py

        ## strings - success messages
        self.SWITCH_SUCCESS_MESSAGE_TEMPLATE = "Successfully switched to branch '{branch_name}'."

        #endregion


    @cached_property
    def _program_start_time(self) -> str:
        """Return the program start time in a human-readable format."""
        return datetime.datetime.now().isoformat()


class ErrorWrappers:
    def __init__(self):
        self.EXPECTED_ERROR_TEMPLATE = "An error occurred:{e}"
        self.UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred:{type_name}: {e}"
