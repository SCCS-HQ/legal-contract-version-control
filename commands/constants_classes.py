#!/usr/bin/env python3
"""Constants and classes for SCCS commands."""

import datetime
from functools import cached_property
import os


class SCCSConstants:
    def __init__(self):
        # Config.py

        self.REPOS = "repos"
        self.REMOTE = "remote"
        self.NAME = "name"
        self.EMAIL = "email"

        self.ACCEPTED_KEYS = (self.REMOTE, self.NAME, self.EMAIL)
        self.ACCEPTED_SCHEMES = ("http", "https")
        
        self.INVALID_URL_ERROR_MESSAGE = (
            "Invalid remote URL provided. The URL must start with 'http://' or 'https://',"
            "and use the format 'http(s)://<host>/<base-path>'. Base path is optional."
        )
        self.INVALID_KEY_ERROR_MESSAGE = (
            "Invalid configuration key provided. Accepted keys are: 'name', 'email', and 'remote'."
        )
        self.INVALID_REPO_NAME_ERROR_MESSAGE = (
            "Invalid repository name. Please ensure the repository is properly "
            "initialized with a valid name."
        )
        self.CONFIG_DIR_SUCCESS_MESSAGE_TEMPLATE = "Configuration '{key}' set to '{value}' successfully.\n"

        # Commit.py

        self.COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = "Commit {sha_hash} created successfully.\n"
        self.COMMIT_FAILURE_ERROR_MESSAGE = "Failed to commit changes."

        # Clone.py

        self.CLONE_ENDPOINT = "clone"
        self.HTTP_TIMEOUT_SECONDS = 60
        self.INVALID_ENDING_ERROR_MESSAGE = (
            "Invalid remote URL provided. Please provide a valid URL ending with "
            "'/clone/'."
        )
        self.HTTP_REQUEST_ERROR_MESSAGE = "Failed to request repository from the remote url."
        self.UNZIP_FAILED_ERROR_MESSAGE = (
            "Failed to unzip repository file. Please try again or ensure the zip is valid."
        )

        self.STATUS_CODE_MESSAGE = "Status Code:\n"
        self.CLONE_SUCCESS_MESSAGE = "Repository cloned successfully.\n"

        # Branch.py

        # subcommands
        self.CREATE_SUBCOMMAND = "create"
        self.DELETE_SUBCOMMAND = "delete"
        self.LIST_SUBCOMMAND = "list"

        # validation / argument errors
        self.INVALID_SUBCOMMAND_ERROR_MESSAGE = "Invalid subcommand provided. Accepted subcommands are: create, delete, list."

        # branch existence / deletion errors
        self.BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' already exists."
        self.CURRENT_BRANCH_DIR_DELETION_ERROR_MESSAGE = "Cannot delete the current branch. Switch branches first."
        self.BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' is missing from repository metadata."

        # success messages
        self.BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' created from '{current_branch_name}' successfully.\n"
        self.BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = "Branch '{branch_name}' deleted successfully.\n"

        # rollback / update errors
        self.ROLLBACK_METADATA_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to rollback metadata after failure for branch '{branch_name}'."

        # listing messages
        self.BRANCHES_DIR_LIST_HEADER = "Branches:"
        self.CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
        self.OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"

        # Init.py

        # filesystem names and structure
        self.SCCS = ".sccs"
        self.OBJECTS_DIR = "objects"
        self.BRANCHES_DIR = "branches"
        self.COMMIT_MESSAGES_DIR = "commit_messages"
        self.CONFIG_DIR = "config"
        self.CURRENT_BRANCH_DIR = "current_branch"
        self.MAIN_BRANCH = "main"
        self.HISTORY_DIR_JSON_FILE = "history.json"
        self.COMMIT_MESSAGES_DIR_JSON_FILE = "commit_messages.json"
        self.DEFAULT_BRANCH_DATA = {
            self.CURRENT_BRANCH_DIR: self.MAIN_BRANCH,
            self.BRANCHES_DIR: [self.MAIN_BRANCH],
        }
        self.COMMIT_FILE_HASH_DIR = "commit_file_hash"
        self.CONFIG_DIR_JSON_FILE = "config.json"
        self.COMMIT_FILE_HASH_DIR_JSON_FILE = "commit_file_hash.json"
        self.CURRENT_BRANCH_DIR_JSON_FILE = "current_branch.json"
        self.MAX_FILE_READ_SIZE = 64 * 1024
        self.INITIAL_VERSION_HASH_SEGMENT = "initial_version"

        # formats and types
        self.DOCX_DIR = "docx"
        self.DOCX_EXTENSION = ".docx"
        self.HTML_DIR = "html"
        self.VIEW_HTML_DIR = "view_html"
        self.HISTORY_DIR = "history"

        # templates and prompts
        self.INPUT_CONFIG_DIR_VALUE_TEMPLATE = "Enter your {config_key}: "

        # runtime & defaults

        self.INITIAL_COMMIT_MESSAGE = "initial commit (This is a default commit message for initial version)"

        # error / status messages
        self.ALREADY_INITIALIZED_ERROR_MESSAGE = "This file has already been initialized with SCCS."
        self.INVALID_FILE_TYPE_ERROR_MESSAGE = "File is not a .docx file. Please provide a valid .docx file."
        self.INIT_SUCCESS_MESSAGE = "SCCS initialization complete.\n"   

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

        # timestamp
        # **Important**: This is set at import time not at runtime, so it may be slightly different from the actual time the command is run

        
        # shared

        self.EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = ("{field} cannot be empty. Please provide a valid {field}.")
        self.ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = (
            "The entered file '{file_path}' does not exist. Please provide a valid file path to an existing file."
        )
        self.BRANCH_OPERATION_FAILED_ERROR_MESSAGE_TEMPLATE = ("Failed to {action} branch.")
        self.MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = ("Resource '{resource_name}' is missing from the repository directory.")


    @cached_property
    def PROGRAM_START_TIME(self) -> str:
        """Return the program start time in a human-readable format."""
        return datetime.datetime.now()


class ErrorWrappers:
    def __init__(self):
        self.EXPECTED_ERROR_TEMPLATE = "An error occurred:\n{e}\n" 
        self.UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred:\n{type_name}: {e}\n"
        