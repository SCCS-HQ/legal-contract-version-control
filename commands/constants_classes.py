#!/usr/bin/env python3
"""Constants and classes for SCCS commands."""

import datetime
from functools import cached_property


class SCCSConstants:
    def __init__(self):
        #region branch.py

        ## subcommands
        self.LIST_SUBCOMMAND = "list"

        self.ACCEPTED_SUBCOMMANDS = ("create", "delete", "list")

        ## validation / argument errors
        self.INVALID_SUBCOMMAND_ERROR_MESSAGE = "Invalid subcommand provided. Accepted subcommands are: create, delete, list."

        ## branch existence / deletion errors
        self.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' already exists."
        self.CURRENT_BRANCH_DIR_DELETION_ERROR_MESSAGE = "Cannot delete the current branch. Switch branches first."

        ## success messages
        self.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' created from '{current_branch_name}' successfully.\n"
        self.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' deleted successfully.\n"

        ## rollback / update errors
        self.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to rollback metadata after failure for branch '{branch_name}'."

        ## listing messages
        self.BRANCHES_DIR_LIST_HEADER = "Branches:"
        self.CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
        self.OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"

        ## format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.SUBCOMMAND_FIELD_NAME = "subcommand"

        #endregion

        #region clone.py

        ## endpoints and timeouts
        self.CLONE_ENDPOINT = "clone"
        self.HTTP_TIMEOUT_SECONDS = 60

        ## error messages
        self.INVALID_ENDING_ERROR_MESSAGE = (
            "Invalid remote URL provided. Please provide a valid URL ending with "
            "'/clone/'."
        )
        self.HTTP_REQUEST_ERROR_MESSAGE = "Failed to request repository from the remote url."
        self.UNZIP_FAILED_ERROR_MESSAGE = (
            "Failed to unzip repository file. Please try again or ensure the zip is valid."
        )

        ## status / success messages
        self.STATUS_CODE_MESSAGE = "Status Code:\n"
        self.CLONE_SUCCESS_MESSAGE = "Repository cloned successfully.\n"

        ## format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.URL_FIELD_NAME = "URL"
        self.REPOSITORY_NAME_FIELD_NAME = "repository name"

        #endregion

        #region commit.py

        ## success / error messages
        self.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = "Commit {sha_hash} created successfully.\n"
        self.COMMIT_FAILURE_ERROR_MESSAGE = "Failed to commit changes."

        ## format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.COMMIT_MESSAGE_FIELD_NAME = "commit message"

        ## commit hash display length (used by commit.py, log.py)
        self.COMMIT_HASH_DISPLAY_LENGTH = 10

        #endregion

        #region config.py

        ## configuration keys
        self.REMOTE_KEY = "remote"

        # repos url part
        self.REPOS = "repos"

        ## error messages
        self.INVALID_REPO_NAME_ERROR_MESSAGE = (
            "Invalid repository name. Please ensure the repository is properly "
            "initialized with a valid name."
        )

        ## success messages
        self.CONFIG_SUCCESS_MESSAGE_TEMPLATE = "Configuration '{key}' set to '{value}' successfully.\n"

        #endregion

        #region diff.py

        ## HTML attributes
        self.STYLE_HTML_ATTRIBUTE = "style"
        self.DATA_NUMBER_HTML_ATTRIBUTE = "data-number"
        self.CLASS_HTML_ATTRIBUTE = "class"
        self.DELETED_HTML_ATTRIBUTE_VALUE = "deleted"
        self.INSERTED_HTML_ATTRIBUTE_VALUE = "inserted"

        ## parser and tags
        self.HTML_PARSER = "html.parser"
        self.TAGS_TO_UNWRAP = ("b", "i", "u", "strong", "em", "style", "table", "tr", "td", "ol", "ul")

        ## opcodes
        self.REPLACE_OPCODE = "replace"
        self.INSERT_OPCODE = "insert"
        self.DELETE_OPCODE = "delete"

        ## success messages
        self.DIFF_SUCCESS_MESSAGE = "Commit diff successfully created.\n"

        #endregion

        #region help.py

        self.HELP_MESSAGES = [
            "SCCS Help",
            "Available commands:",
            "  sccs branch - Create a new branch, delete, or list branches.",
            "  sccs clone - Clone a hosted SCCS repository with a URL.",
            "  sccs commit - Commit changes to the repository.",
            "  sccs config - Configure a repository's data value (remote, name, email)",
            "  sccs diff - Show differences between the current document and a past commit.",
            "  sccs help - Print this help message.",
            "  sccs init - Initialize a new SCCS repository.",
            "  sccs log - Print a list of past commits for the current branch.",
            "  sccs open - Open a commit file and update the current document.",
            "  sccs publish - Publish a local repository to a hosting service.",
            "  sccs pull - Pull changes from a remote repository and merge them into the local "
            "repository.",
            "  sccs push - Push changes from the local repository to a remote repository.",
            "  sccs revert - Revert the current document to the specified commit.",
            "  sccs reset - Delete all uncommitted changes.",
            "  sccs switch - Switch between document branches.",
            "  sccs status - Check the status of the current document for uncommitted changes.",
            "  sccs merge - Merge the entered branch into the current branch.",
        ]

        #endregion

        #region init.py

        ## hash segments
        self.INITIAL_VERSION_HASH_SEGMENT = "initial_version"

        ## runtime defaults
        self.INITIAL_COMMIT_MESSAGE = "initial commit (This is a default commit message for initial version)"

        ## templates and prompts
        self.INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "

        ## filesystem names and structure
        self.MAIN_BRANCH_DIR = "main"

        ## default branch data
        self.DEFAULT_BRANCH_DATA = {
            self.CURRENT_BRANCH_DICT_KEY: self.MAIN_BRANCH_ATTRIBUTE,
            self.BRANCHES_DICT_KEY: [self.MAIN_BRANCH_ATTRIBUTE],
        }

        ## error / status messages
        self.ALREADY_INITIALIZED_ERROR_MESSAGE = "This file has already been initialized with SCCS."
        self.INVALID_FILE_TYPE_ERROR_MESSAGE = "File is not a .docx file. Please provide a valid .docx file."
        self.INIT_SUCCESS_MESSAGE = "SCCS initialization complete.\n"

        ## history data dict keys
        self.INITIAL_COMMIT_DICT_KEY = "initial_commit"
        self.INITIAL_COMMIT_NUMBER = "1"

        ## format field names (for EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE)
        self.DOCUMENT_PATH_FIELD_NAME = "document path"

        #endregion

        #region log.py

        self.LOG_DICT_KEY = "log"
        self.AUTHOR_DICT_KEY = "author"
        self.TIMESTAMP_DICT_KEY = "timestamp"
        self.MESSAGE_DICT_KEY = "message"

        ## display format constants
        self.LOG_SEPARATOR = "------------------------------"
        self.LOG_COMMIT_FILE_LABEL = "Commit File: "
        self.LOG_AUTHOR_LABEL = "Author: "
        self.LOG_DATE_LABEL = "Date: "
        self.LOG_MESSAGE_LABEL = "Message: "

        #endregion

        #region merge.py

        self.CURRENT_BRANCH_MERGE_ERROR_MESSAGE = "Cannot merge the current branch into itself."
        

        self.MERGE_COMMIT_MESSAGE_TEMPLATE = "Merged branch '{branch}' into '{current_branch}'."

        self.MERGE_SUCCESS_MESSAGE_TEMPLATE = "Successfully merged branch '{branch}' into branch '{current_branch}'."

        #endregion        

        #region open.py

        self.OPEN_OUTPUT_FILE_NAME_TEMPLATE = "Opened_DOCX_Commit_{commit_hash}.docx"

        self.OPEN_SUCCESS_MESSAGE_TEMPLATE = "Commit '{commit_hash}' has been successfully opened in {output_file}.\nIt is safe to delete this file. No changes will be lost unless {output_file} is modified after this point. "

        #endregion

        #region publish.py

        self.BUFFER_CREATION_FAILED_ERROR_MESSAGE = "Failed to create a buffer for the zipped repository. Please try again."
        self.ZIPPING_FILE_ERROR_MESSAGE = "Failed to zip current working directory"
        self.BUFFER_RESET_ERROR_MESSAGE = "Failed to reset buffer position"
        self.HTTP_POST_REQUEST_ERROR_MESSAGE = "Failed to post repository to {url}"
        self.REQUIRED_PATH_ENDING_TEMPLATE = "/repos/{repo_name}"
        self.INVALID_PATH_ENDING_ERROR_MESSAGE = "API URL must end with '/repos/<repo_name>'"
        self.FILE_RESOURCE = "file"
        self.DATA_RESOURCE = "data"
        self.ZIP_EXTENSION = ".zip"
        self.REMOTE_KEY = "remote"
        self.CONTENT_TYPE_ZIP = "application/zip"
        self.CONTENT_TYPE_JSON = "application/json"
        self.PUBLISH_ENDPOINT_TEMPLATE = "{base_url}/publish"
        self.URL_PARTS_SEPARATOR = "/"
        self.STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}\n"
        self.PUBLISH_SUCCESS_MESSAGE_TEMPLATE = "Repository published successfully to {url}\n"
        

        #endregion

        #region pull.py

        self.RGLOB_ALL_FILES_PATTERN = "*"
        self.HTTP_OBJECTS_DATA_KEY = "objects"
        self.REMOTE_KEY = "remote"
        self.PULL_ENDPOINT_TEMPLATE = "{base_url}/pull"
        self.PULL_SUCCESS_MESSAGE_TEMPLATE = "Repository pulled successfully from {url}\n"


        #endregion

        #region push.py

        self.JSON_EXTENSION = ".json"
        self.UPDATED_BRANCHES_DICT_KEY = "updated_branches"
        self.TMP_DIR_TEMPLATE = "tmp_{repo_name}"
        self.INVALID_URL_SCHEME_ERROR_MESSAGE = "API URL must end with '/repos/<repo_name>'"
        self.PUSH_ENDPOINT_TEMPLATE = "{base_url}/push"
        self.PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to push to repository {url}"
        self.CLEAR_UPDATED_BRANCHES_ERROR_MESSAGE = "Push successful, but failed to clear updated branches list in current " "branch file."
        self.PUSH_SUCCESS_MESSAGE_TEMPLATE = "Repository pushed successfully to {url}\n"

        #endregion

        #region repository_layout.py

        ## error / status messages
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

        ## diff output filename
        self.DIFF_OUTPUT_HTML_FILE = "diff.html"

        ## resource errors
        self.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = "Resource '{resource_name}' is missing from the repository directory."

        ## resource names
        self.BRANCH_NAME_FIELD_NAME = "branch name"
        self.COMMIT_FILE_FIELD_NAME = "commit file hash"

        ## branch name attribute
        self.BRANCH_NAME_REPOSITORY_LAYOUT_ATTRIBUTE = "branch_name"
        self.LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
        self.UPDATED_BRANCHES_DICT_KEY = "updated_branches"
        self.TMP_EXTENSION = ".tmp"
        self.COMMIT_ORDER_DICT_KEY = "commit_order"

        #endregion

        #region reset.py
        
        self.RESET_SUCCESS_MESSAGE = "All uncommitted changes have been deleted. The document has been reset to the latest commit.\n"
        self.RESET_ERROR_MESSAGE = "Failed to reset the document."

        #endregion

        #region revert.py

        self.SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = "Source file '{file_name}' does not exist."
        self.REVERT_SUCCESS_MESSAGE_TEMPLATE = "Document successfully reverted to commit '{commit_hash}' on commit '{new_commit_hash}'.\n"
        self.REVERT_COMMIT_MESSAGE_TEMPLATE = "Reverted document to commit '{commit_hash}'."

        #endregion

        #region Shared (referenced by 2+ command modules)

        self.DEFAULT_HTML_STYLES = ("<style>\n* {\nfont-family: Arial, Helvetica, sans-serif;\n}\n\n"".inserted {\nbackground-color: #d4fcbc;\ndisplay: block;\nwidth: fit-content;\n}\n""\n"".deleted {\nbackground-color: #fbb6c2;\ndisplay: block;\nwidth: fit-content;\n}\n""\n"".center {\ndisplay: flex;\njustify-content: center;\n}\n</style>")

        ## filesystem names and structure (used by init.py, repository_layout.py)
        self.SCCS_DIR = ".sccs"
        self.OBJECTS_DIR = "objects"
        self.BRANCHES_DIR = "branches"
        self.COMMIT_MESSAGES_DIR = "commit_messages"
        self.CONFIG_DIR = "config"
        self.CURRENT_BRANCH_DIR = "current_branch"
        self.HISTORY_JSON_FILE = "history.json"
        self.COMMIT_MESSAGES_JSON_FILE = "commit_messages.json"
        self.COMMIT_FILE_HASH_DIR = "commit_file_hash"
        self.CONFIG_JSON_FILE = "config.json"
        self.COMMIT_FILE_HASH_JSON_FILE = "commit_file_hash.json"
        self.CURRENT_BRANCH_JSON_FILE = "current_branch.json"

        ## formats and types (used by init.py, repository_layout.py)
        self.DOCX_DIR = "docx"
        self.DOCX_EXTENSION = ".docx"
        self.HTML_DIR = "html"
        self.VIEW_HTML_DIR = "view_html"
        self.HISTORY_DIR = "history"
        self.HASH_PARTS_SEPARATOR = "/"

        ## runtime limits (used by init.py, repository_layout.py)
        self.MAX_FILE_READ_SIZE = 64 * 1024

        ## file-system metadata keys (used by init.py, repository_layout.py)
        self.BRANCHES_DICT_KEY = "branches"
        self.CURRENT_BRANCH_DICT_KEY = "current_branch"
        self.HISTORY_DICT_KEY = "history"
        self.LATEST_COMMIT_DICT_KEY = "latest_commit"

        ## default branch name (used by branch.py, init.py, repository_layout.py)
        self.MAIN_BRANCH_ATTRIBUTE = "main"

        ## user config keys (used by config.py, init.py, repository_layout.py)
        self.NAME_KEY = "name"
        self.EMAIL_KEY = "email"

        ## accepted config keys validator (used by config.py, repository_layout.py)
        self.ACCEPTED_KEYS = (self.REMOTE_KEY, self.NAME_KEY, self.EMAIL_KEY)

        ## config validation error messages (used by config.py, repository_layout.py)
        self.INVALID_KEY_ERROR_MESSAGE = (
            "Invalid configuration key provided. Accepted keys are: 'name', 'email', and 'remote'."
        )

        ## branch subcommands (used by branch.py, repository_layout.py)
        self.CREATE_SUBCOMMAND = "create"
        self.DELETE_SUBCOMMAND = "delete"

        ## branch operation errors (used by branch.py, repository_layout.py)
        self.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE = "Failed to {action} branch."

        ## accepted URL schemes (used by clone.py, config.py)
        self.ACCEPTED_SCHEMES = ("http", "https")

        ## URL validation error message (used by clone.py, config.py)
        self.INVALID_URL_ERROR_MESSAGE = (
            "Invalid remote URL provided. The URL must start with 'http://' or 'https://',"
            "and use the format 'http(s)://<host>/<base-path>'. Base path is optional."
        )

        ## error message templates (used by branch.py, clone.py, commit.py, config.py, init.py, repository_layout.py)
        self.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = "{field} cannot be empty. Please provide a valid {field}."

        ## file existence error (used by init.py, repository_layout.py)
        self.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
            "The entered file '{file_path}' does not exist. Please provide a valid file path to an existing file."
        )

        ## branch lookup error (used by branch.py, repository_layout.py)
        self.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' is missing from repository metadata."

        ## program start time getter (used by init.py, repository_layout.py)
        self.PROGRAM_START_TIME = self._program_start_time

        ## file I/O modes (used by init.py, clone.py, repository_layout.py)
        self.FILE_WRITE_MODE = "w"
        self.FILE_READ_BINARY_MODE = "rb"
        self.ZIP_READ_MODE = "r"

        ## file I/O encoding and newline (used by init.py, repository_layout.py)
        self.FILE_ENCODING_UTF8 = "utf-8"
        self.FILE_NEWLINE = "\n"

        #endregion


    @cached_property
    def _program_start_time(self) -> str:
        """Return the program start time in a human-readable format."""
        return datetime.datetime.now().isoformat()


class ErrorWrappers:
    def __init__(self):
        self.EXPECTED_ERROR_TEMPLATE = "An error occurred:\n{e}\n"

    @cached_property
    def _program_start_time(self) -> str:
        """Return the program start time in a human-readable format."""
        return datetime.datetime.now().isoformat()


class ErrorWrappers:
    def __init__(self):
        self.EXPECTED_ERROR_TEMPLATE = "An error occurred:\n{e}\n"
        self.UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred:\n{type_name}: {e}\n"