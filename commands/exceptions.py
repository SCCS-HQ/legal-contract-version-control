#!/usr/bin/env python3
"""Module for SCCS exception classes."""


class SCCSException(Exception):
    """Base class for SCCS exceptions."""

    default_message = "An SCCS error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.default_message if message is None else message)


# Branch Exceptions


class InvalidBranchNameError(SCCSException):
    """Raised when a branch name is invalid."""

    default_message = "Branch name is invalid."


class BranchMissingFromMetadataError(SCCSException):
    """Raised when a branch is missing from the metadata."""

    default_message = "Branch is missing from metadata."


class BranchNotFoundError(SCCSException):
    """Raised when a branch is not found."""

    default_message = "Branch not found."


class ConfigurationError(SCCSException):
    """Raised when there is an error in the SCCS configuration."""

    default_message = "SCCS configuration is invalid."


class BranchCreationError(SCCSException):
    """Raised when there is an error creating a new branch."""

    default_message = "Could not create branch."


class BranchDeletionError(SCCSException):
    """Raised when there is an error deleting a branch."""

    default_message = "Could not delete branch."


class BranchAlreadyExistsError(SCCSException):
    """Raised when a branch already exists."""

    default_message = "Branch already exists."


# File Operation Exceptions


class FileCopyError(SCCSException):
    """Raised when there is an error copying a file."""

    default_message = "Could not copy file."


class FileWriteError(SCCSException):
    """Raised when there is an error writing to a file."""

    default_message = "Could not write file."


class FileOpenError(SCCSException):
    """Raised when there is an error opening a file."""

    default_message = "Could not open file."


class FileDeleteError(SCCSException):
    """Raised when there is an error deleting a file."""

    default_message = "Could not delete file."


class FileCreateError(SCCSException):
    """Raised when there is an error creating a file."""

    default_message = "Could not create file."
    

class FileDoesNotExistError(SCCSException):
    """Raised when a file does not exist."""

    default_message = "File does not exist."
# Metadata Exceptions


class UpdatingMetadataError(SCCSException):
    """Raised when there is an error updating metadata files."""

    default_message = "Could not update metadata."


class TemporaryFileError(SCCSException):
    """Raised when there is an error creating or replacing a temporary file."""

    default_message = "Could not create or replace temporary file."


# Invalid Command Call Exceptions


class InvalidArgumentError(SCCSException):
    """Raised when an invalid argument is provided to a command."""

    default_message = "Invalid command argument."


class InvalidSubcommandError(SCCSException):
    """Raised when an invalid subcommand is provided to a command."""

    default_message = "Invalid subcommand."


class UnknownCommandError(SCCSException):
    """Raised when an unknown command is provided."""

    default_message = "Unknown command."


class InvalidLayoutError(SCCSException):
    """Raised when the SCCS directory layout is invalid or missing."""

    default_message = "SCCS directory layout is invalid or incomplete."


class SCCSNotInitializedError(SCCSException):
    """Raised when SCCS has not been initialized in the current directory."""

    default_message = "SCCS has not been initialized in the current directory."


class AlreadyInitializedError(SCCSException):
    """Raised when the document has already been initialized with SCCS."""

    default_message = "Document has already been initialized with SCCS."


class InvalidFileTypeError(SCCSException):
    """Raised when a file of an invalid type is provided."""

    default_message = "Invalid file type."


# Not Found Exceptions


class DocumentNotFoundError(SCCSException):
    """Raised when a document is not found."""

    default_message = "Document not found."


class CommitNotFoundError(SCCSException):
    """Raised when a commit object is not found."""

    default_message = "Commit object not found."


# Conversion Exceptions


class DocumentHashingError(SCCSException):
    """Raised when there is an error hashing a document."""

    default_message = "Could not hash document."


class ConvertingDocumentToHTMLError(SCCSException):
    """Raised when there is an error converting a document to HTML."""

    default_message = "Could not convert document to HTML."


# Metadata Exceptions


class InvalidMetadataError(SCCSException):
    """Raised when metadata files are corrupted or missing required keys."""

    default_message = "Metadata is corrupted or missing required keys."


# Uncommitted changes Exceptions


class UncommittedChangesError(SCCSException):
    """Raised when there are uncommitted changes that prevent an action."""

    default_message = "Uncommitted changes prevent this action."


class NoUncommittedChangesError(SCCSException):
    """Raised when there are no uncommitted changes but an action requires them."""

    default_message = "No uncommitted changes found."


# Input Exceptions


class InvalidInputError(SCCSException):
    """Raised when an invalid input is provided."""

    default_message = "Invalid input."


class EmptyCommitMessageError(SCCSException):
    """Raised when an empty commit message is provided."""

    default_message = "Commit message cannot be empty."


# Module Exceptions


class FileImportedAsModuleError(SCCSException):
    """Raised when a script is imported as a module but is intended to be run only as a
    standalone script."""

    default_message = "This file cannot be imported as a module."


# Zipping Exceptions


class ZippingFileError(SCCSException):
    """Raised when there is an error zipping a directory or file."""

    default_message = "Failed to zip file or directory."


# Buffer Exceptions


class BufferError(SCCSException):
    """Raised when there is an error with a buffer."""

    default_message = "An error occurred with the buffer."


# HTTP Request Exceptions


class HTTPPostRequestError(SCCSException):
    """Raised when there is an error making an HTTP POST request."""

    default_message = "Failed to make HTTP POST request."


class HTTPGetRequestError(SCCSException):
    """Raised when there is an error making an HTTP GET request."""

    default_message = "Failed to make HTTP GET request."


# API URL Exceptions


class InvalidAPIURLError(SCCSException):
    """Raised when the API URL is invalid."""

    default_message = "The API URL is invalid."


# Push Exceptions


class MissingCommitObjectsError(SCCSException):
    """
    Raised when the local repository is missing commit objects that are present in the
    remote repository.
    """

    default_message = (
        "The local repository is missing commit objects that are present in the remote "
        "repository. Run 'sccs pull' to download these objects"
    )
