#!/usr/bin/env python3
"""Constants and classes for SCCS commands."""

import datetime


class SCCSConstants:
    def __init__(self):
        # Config.py

        self.REPOS = "repos"
        self.REMOTE = "remote"
        self.NAME = "name"
        self.EMAIL = "email"
        self.SLASH = "/"

        self.ACCEPTED_KEYS = (self.REMOTE, self.NAME, self.EMAIL)
        self.ACCEPTED_SCHEMES = ("http", "https")
        
        self.EMPTY_CONFIG_VALUE_ERROR_MESSAGE = (
            "Configuration value for the given key cannot be empty. Please provide a valid"
            " value."
        )
        self.INVALID_URL_ERROR_MESSAGE = (
            "Invalid remote URL provided. The URL must start with 'http://' or 'https://',"
            "and use the format 'http(s)://<host>/<base-path>'. Base path is optional."
        )
        self.INVALID_KEY_ERROR_MESSAGE = (
            "Invalid configuration key provided. Accepted keys are: {keys}."
        )
        self.INVALID_REPO_NAME_ERROR_MESSAGE = (
            "Invalid repository name. Repository names cannot be empty or contain only"
            " whitespace. "
        )
        self.EMPTY_REPO_NAME_ERROR_MESSAGE = (
            "Repository name cannot be empty. Please ensure the repository is properly "
            "initialized with a valid name."
        )

        self.SUCCESS_MESSAGE_TEMPLATE = "Configuration '{key}' set to '{value}' successfully.\n"

        # Commit.py

        self.EMPTY_COMMIT_MESSAGE_ERROR = "Commit message cannot be empty. Please provide a valid commit message."
        self.COMMIT_SCCS_SUCCESS_MESSAGE_TEMPLATE = "Commit {sha_hash} created successfully.\n"
        self.COMMIT_FAILURE_ERROR_MESSAGE = "Failed to commit changes."

        # Clone.py

        self.CLONE_ENDPOINT = "clone"
        self.HTTP_TIMEOUT_SECONDS = 60
        
        self.INVALID_SCHEME_ERROR_MESSAGE = (
            "Invalid remote URL provided. Please provide a valid URL starting with 'http://'"
            " or 'https://'."
        )
        self.INVALID_ENDING_ERROR_MESSAGE = (
            "Invalid remote URL provided. Please provide a valid URL ending with "
            f"'{self.SLASH}{self.CLONE_ENDPOINT}{self.SLASH}'."
        )
        self.EMPTY_URL_ERROR_MESSAGE = (
            "No URL entered. Please provide a valid URL to clone the repository from."
            )
        self.HTTP_REQUEST_ERROR_MESSAGE_TEMPLATE = "Failed to request repository from {url}"
        self.NO_REPO_NAME_ERROR_MESSAGE = f"URL must include a repository name before '{self.SLASH}{self.CLONE_ENDPOINT}{self.SLASH}'."
        self.UNZIP_FAILED_ERROR_MESSAGE = (
            "Failed to unzip repository file. Please try again or ensure the zip is valid."
        )

        self.STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}\n"
        self.SUCCESS_MESSAGE = "Repository cloned successfully.\n"

        # Branch.py

        # subcommands
        self.CREATE_SUBCOMMAND = "create"
        self.DELETE_SUBCOMMAND = "delete"
        self.LIST_SUBCOMMAND = "list"

        # validation / argument errors
        self.NO_SUBCOMMAND_ERROR_MESSAGE = "No subcommand provided. Please specify one of: create, delete, list."
        self.INVALID_SUBCOMMAND_ERROR_MESSAGE_TEMPLATE = "Invalid subcommand '{subcommand}' provided."
        self.NO_BRANCH_NAME_ERROR_MESSAGE = "No branch name provided. Please specify a branch name."

        # branch existence / deletion errors
        self.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' already exists."
        self.CURRENT_BRANCH_DELETION_ERROR_MESSAGE = "Cannot delete the current branch. Switch branches first."
        self.BRANCH_MISSING_FROM_METADATA_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' is missing from repository metadata."

        # success messages
        self.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' created from '{current_branch_name}' successfully.\n"
        self.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' deleted successfully.\n"

        # rollback / update errors
        self.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to rollback metadata after failure for branch '{branch_name}'."

        # listing messages
        self.BRANCHES_MESSAGE = "Branches:"
        self.CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
        self.OTHER_BRANCH_MESSAGE_TEMPLATE = "  {branch_name}"

        # Init.py

        # filesystem names and structure
        self.SCCS = ".sccs"
        self.OBJECTS = "objects"
        self.BRANCHES = "branches"
        self.COMMIT_MESSAGES = "commit_messages"
        self.CONFIG = "config"
        self.CURRENT_BRANCH = "current_branch"
        self.MAIN_BRANCH = "main"
        self.HISTORY_JSON = "history.json"
        self.COMMIT_MESSAGES_JSON = "commit_messages.json"
        self.DEFAULT_BRANCH_DATA = {"current_branch": "main", "branches": ["main"]}
        self.COMMIT_FILE_HASH = "commit_file_hash"
        self.CONFIG_JSON = "config.json"
        self.COMMIT_FILE_HASH_JSON = "commit_file_hash.json"
        self.CURRENT_BRANCH_JSON = "current_branch.json"
        self.MAX_FILE_READ_SIZE = 64 * 1024
        self.INITIAL_VERSION_HASH_SEGMENT = "initial_version"

        # formats and types
        self.DOCX = "docx"
        self.DOCX_EXTENSION = ".docx"
        self.HTML = "html"
        self.VIEW_HTML = "view_html"
        self.HISTORY = "history"

        # templates and prompts
        self.INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "
        self.INVALID_CONFIG_VALUE_ERROR_MESSAGE_TEMPLATE = "{config_key} cannot be empty."

        # runtime & defaults

        self.INITIAL_COMMIT_MESSAGE = "initial commit (This is a default commit message for initial version)"

        # error / status messages
        self.NO_FILE_PROVIDED_ERROR_MESSAGE = "No file path provided. Please provide the path to the .docx file you want to initialize with SCCS."
        self.ALREADY_INITIALIZED_ERROR_MESSAGE = "This file has already been initialized with SCCS."
        self.INVALID_FILE_TYPE_ERROR_MESSAGE = "File is not a .docx file. Please provide a valid .docx file."
        self.FILE_DOES_NOT_EXIST_ERROR_MESSAGE = "File does not exist. Please provide a valid file path to an existing .docx file."
        self.SCCS_SUCCESS_MESSAGE = "SCCS initialization complete.\n"   

        # repository_layout.py
    
        # filesystem names and structure

        # formats and types

        # templates and prompts
        
        # runtime & defaults

        # error / status messages
        self.TARGET_BRANCH_NOT_SET_ERROR_MESSAGE = (
            "Target branch not set. Please chain this method call with a branch "
            "method before calling history_path(). For example,"
            "'repo_layout.main_branch().foo()'."
        )
        self.NO_COMMIT_FILE_PROVIDED_ERROR_MESSAGE = (
            "No commit file provided. Please provide a valid commit file to open."
        )
        self.INVALID_COMMIT_HASH_ERROR_MESSAGE = (
            "Invalid commit file name. Please provide a shortened, 10 character commit "
            "hash or the full 64 character commit hash as the commit identifier."
        )
        self.COMMIT_FILE_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = (
            "Commit file '{commit_file}' not found. Please provide a valid commit file."
        )
        self.MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE = (
            "Multiple commit files found matching '{commit}'. Please provide a full, "
            "64 character commit hash."
        )
        self.INVALID_KEY_ERROR_MESSAGE_TEMPLATE = (
            "Invalid configuration key '{key}'. Accepted keys are 'remote', 'name', and 'email'."
        )
        self.INVALID_COMMIT_FILE_NAME_ERROR_MESSAGE = (
            "Invalid commit file name. Please provide a shortened, 10 character commit "
            "hash or the full 64 character commit hash as the commit identifier."
        )
        self.NONEXISTENT_COMMIT_FILE_ERROR_MESSAGE_TEMPLATE = (
            "Commit file '{commit_file}' does not exist. Please provide a valid commit file."
        )
        self.INVALID_COMMIT_HISTORY_DATA_ERROR_MESSAGE = (
            "Invalid commit history data. Please ensure that the commit data has not"
            "been manually modified."
        )
        self.BRANCH_CREATION_ERROR_MESSAGE = ("Failed to create branch." )
        self.INVALID_BRANCH_DATA_ERROR_MESSAGE = (
            "Invalid branch data. Please ensure that the branch data has not been manually"
            "modified and the the targeted branch exists."
        )
        self.BRANCH_DELETION_ERROR_MESSAGE = ("Failed to delete branch." )
        self.BRANCH_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
            "Branch '{branch_name}' does not exist. Please provide a valid branch name."
        )
        self.MISSING_DIRECTORY_ERROR_MESSAGE_TEMPLATE = (
            "Missing directory '{directory_name}' in repository layout. Please ensure the "
            "directory exists and is properly configured."
        )
        self.MISSING_FILE_ERROR_MESSAGE_TEMPLATE = (
            "Missing file '{file_name}' in repository layout. Please ensure the "
            "file exists and is properly configured."
        )
        self.UNCOMMITTED_CHANGES_ERROR_MESSAGE = (
            "Uncommitted changes detected. Please clean the working tree before proceeding."
        )
        self.NO_UNCOMMITTED_CHANGES_ERROR_MESSAGE = (
            "No uncommitted changes detected. Uncommitted changes are required before committing."
        )

        # timestamp
        # **Important**: This is set at import time not at runtime, so it may be slightly different from the actual time the command is run

        self.PROGRAM_START_TIME = datetime.datetime.now()
        

class ErrorWrappers:
    def __init__(self):
        self.EXPECTED_ERROR_TEMPLATE = "An error occurred:\n{e}\n" 
        self.UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred:\n{type_name}: {e}\n"
        