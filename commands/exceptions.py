#!/usr/bin/env python3
"""Module for SCCS exception classes."""


class SCCSException(Exception):
    """Base class for SCCS exceptions."""

    pass


# Branch Exceptions


class InvalidBranchNameError(SCCSException):
    """Raised when a branch name is invalid."""

    pass


class BranchMissingFromMetadataError(SCCSException):
    """Raised when a branch is missing from the metadata."""

    pass


class BranchNotFoundError(SCCSException):
    """Raised when a branch is not found."""

    pass


class ConfigurationError(SCCSException):
    """Raised when there is an error in the SCCS configuration."""

    pass


class BranchCreationError(SCCSException):
    """Raised when there is an error creating a new branch."""

    pass


class BranchDeletionError(SCCSException):
    """Raised when there is an error deleting a branch."""

    pass


class BranchAlreadyExistsError(SCCSException):
    """Raised when a branch already exists."""

    pass


# File Operation Exceptions


class FileCopyError(SCCSException):
    """Raised when there is an error copying a file."""

    pass


class FileWriteError(SCCSException):
    """Raised when there is an error writing to a file."""

    pass


class FileOpenError(SCCSException):
    """Raised when there is an error opening a file."""

    pass


class UpdatingMetadataError(SCCSException):
    """Raised when there is an error updating metadata files."""

    pass


class TemporaryFileError(SCCSException):
    """Raised when there is an error creating or replacing a temporary file."""

    pass


# Invalid Command Call Exceptions


class InvalidArgumentError(SCCSException):
    """Raised when an invalid argument is provided to a command."""

    pass


class InvalidSubcommandError(SCCSException):
    """Raised when an invalid subcommand is provided to a command."""

    pass


class UnknownCommandError(SCCSException):
    """Raised when an unknown command is provided."""

    pass


class InvalidLayoutError(SCCSException):
    """Raised when the SCCS directory layout is invalid or missing."""

    pass


class SCCSNotInitializedError(SCCSException):
    """Raised when SCCS has not been initialized in the current directory."""

    pass


class AlreadyInitializedError(SCCSException):
    """Raised when the document has already been initialized with SCCS."""

    pass


class InvalidFileTypeError(SCCSException):
    """Raised when a file of an invalid type is provided."""

    pass


# Not Found Exceptions


class DocumentNotFoundError(SCCSException):
    """Raised when a document is not found."""

    pass


class CommitNotFoundError(SCCSException):
    """Raised when a commit object is not found."""

    pass


# Conversion Exceptions


class DocumentHashingError(SCCSException):
    """Raised when there is an error hashing a document."""

    pass


class ConvertingDocumentToHTMLError(SCCSException):
    """Raised when there is an error converting a document to HTML."""

    pass


# Metadata Exceptions


class InvalidMetadataError(SCCSException):
    """Raised when metadata files are corrupted or missing required keys."""

    pass


# Uncommitted changes Exceptions


class UncommittedChangesError(SCCSException):
    """Raised when there are uncommitted changes that prevent an action."""

    pass


# Input Exceptions


class InvalidInputError(SCCSException):
    """Raised when an invalid input is provided."""

    pass


class EmptyCommitMessageError(SCCSException):
    """Raised when an empty commit message is provided."""

    pass


# Module Exceptions


class FileImportedAsModuleError(SCCSException):
    """Raised when a script is imported as a module but is intended to be run only as a
    standalone script."""

    pass
