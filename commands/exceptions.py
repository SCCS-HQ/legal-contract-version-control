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
