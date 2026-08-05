#!/usr/bin/env python3


class SCCSException(Exception):

    default_message = "An SCCS error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.default_message if message is None else message)


# Branch Exceptions


class BranchNotSetError(SCCSException):

    default_message = "Branch not set in RepositoryLayout."


class InvalidBranchNameError(SCCSException):

    default_message = "Branch name is invalid."


class BranchMissingFromMetadataError(SCCSException):

    default_message = "Branch is missing from metadata."


class BranchNotFoundError(SCCSException):

    default_message = "Branch not found."


class ConfigurationError(SCCSException):

    default_message = "SCCS configuration is invalid."


class BranchCreationError(SCCSException):

    default_message = "Could not create branch."


class BranchDeletionError(SCCSException):

    default_message = "Could not delete branch."


class BranchAlreadyExistsError(SCCSException):

    default_message = "Branch already exists."


# File Operation Exceptions


class FileCopyError(SCCSException):

    default_message = "Could not copy file."


class FileWriteError(SCCSException):

    default_message = "Could not write file."


class FileOpenError(SCCSException):

    default_message = "Could not open file."


class FileDeleteError(SCCSException):

    default_message = "Could not delete file."


class FileCreateError(SCCSException):

    default_message = "Could not create file."


class FileDoesNotExistError(SCCSException):

    default_message = "File does not exist."


# Metadata Exceptions


class UpdatingMetadataError(SCCSException):

    default_message = "Could not update metadata."


class TemporaryFileError(SCCSException):

    default_message = "Could not create or replace temporary file."


# Invalid Command Call Exceptions


class InvalidArgumentError(SCCSException):

    default_message = "Invalid command argument."


class EmptyArgumentError(SCCSException):

    default_message = "Argument cannot be empty."


class InvalidSubcommandError(SCCSException):

    default_message = "Invalid subcommand."


class UnknownCommandError(SCCSException):

    default_message = "Unknown command."


class InvalidLayoutError(SCCSException):

    default_message = "SCCS directory layout is invalid or incomplete."


class SCCSNotInitializedError(SCCSException):

    default_message = "SCCS has not been initialized in the current directory."


class AlreadyInitializedError(SCCSException):

    default_message = "Document has already been initialized with SCCS."


class InvalidFileTypeError(SCCSException):

    default_message = "Invalid file type."


# Not Found Exceptions


class DocumentNotFoundError(SCCSException):

    default_message = "Document not found."


class CommitNotFoundError(SCCSException):

    default_message = "Commit object not found."


# Conversion Exceptions


class DocumentHashingError(SCCSException):

    default_message = "Could not hash document."


class ConvertingDocumentToHTMLError(SCCSException):

    default_message = "Could not convert document to HTML."


# Metadata Exceptions


class InvalidMetadataError(SCCSException):

    default_message = "Metadata is corrupted or missing required keys."


# Uncommitted changes Exceptions


class UncommittedChangesError(SCCSException):

    default_message = "Uncommitted changes prevent this action."


class NoUncommittedChangesError(SCCSException):

    default_message = "No uncommitted changes found."


# Input Exceptions


class InvalidInputError(SCCSException):

    default_message = "Invalid input."


# Module Exceptions


class FileImportedAsModuleError(SCCSException):

    default_message = "This file cannot be imported as a module."


# Zipping Exceptions


class ZippingFileError(SCCSException):

    default_message = "Failed to zip file or directory."


# Buffer Exceptions


class BufferError(SCCSException):

    default_message = "An error occurred with the buffer."


# HTTP Request Exceptions


class HTTPPostRequestError(SCCSException):

    default_message = "Failed to make HTTP POST request."


class HTTPGetRequestError(SCCSException):

    default_message = "Failed to make HTTP GET request."


# API URL Exceptions


class InvalidAPIURLError(SCCSException):

    default_message = "The API URL is invalid."


# Push Exceptions


class MissingCommitObjectsError(SCCSException):

    default_message = (
        "The local repository is missing commit objects that are present in the remote "
        "repository. Run 'sccs pull' to download these objects"
    )
