class SCCSException(Exception):
    """Base class for SCCS exceptions."""
    pass

class InvalidLayoutError(SCCSException):
    """Raised when the SCCS directory layout is invalid or missing."""
    pass

class InvalidArgumentError(SCCSException):
    """Raised when an invalid argument is provided to a command."""
    pass

class InvalidSubcommandError(SCCSException):
    """Raised when an invalid subcommand is provided to a command."""
    pass

class BranchNotFoundError(SCCSException):
    """Raised when a branch is not found."""
    pass

class CommitNotFoundError(SCCSException):
    """Raised when a commit is not found."""
    pass

class DocumentNotFoundError(SCCSException):
    """Raised when a document is not found."""
    pass

class InvalidBranchNameError(SCCSException):
    """Raised when a branch name is invalid."""
    pass

class UncommittedChangesError(SCCSException):
    """Raised when there are uncommitted changes that prevent an action."""
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

class CommitError(SCCSException):
    """Raised when there is an error during the commit process."""
    pass

class FileOperationError(SCCSException):
    """Raised when a file or directory operation fails."""
    pass

class UpdatingMetadataError(SCCSException):
    """Raised when there is an error updating metadata files."""
    pass

class TemporaryFileError(SCCSException):
    """Raised when there is an error creating or replacing a temporary file."""
    pass

class InvalidFileTypeError(SCCSException):
    """Raised when a file of an invalid type is provided."""
    pass

class FileReadError(SCCSException):
    """Raised when there is an error reading a file."""
    pass

class InvalidInputError(SCCSException):
    """Raised when an invalid input is provided."""
    pass

class AlreadyInitializedError(SCCSException):
    """Raised when the document has already been initialized with SCCS."""
    pass

class FileCopyError(SCCSException):
    """Raised when there is an error copying a file."""
    pass

class FileWriteError(SCCSException):
    """Raised when there is an error writing to a file."""
    pass

class FileOpenError(SCCSException):
    """Raised when there is an error opening a file."""
    pass

class UnknownCommandError(SCCSException):
    """Raised when an unknown command is provided."""
    pass

class BranchAlreadyExistsError(SCCSException):
    """Raised when a branch already exists."""
    pass

class BranchDoesNotExistError(SCCSException):
    """Raised when a branch does not exist."""
    pass

class BranchMissingFromMetadata(SCCSException):
    """Raised when a branch is missing from the metadata."""
    pass

class InvalidMetadataError(SCCSException):
    """Raised when metadata files are corrupted or missing required keys."""
    pass

class UncommittedChangesError(SCCSException):
    """Raised when there are uncommitted changes on the current branch."""
    pass

class CommitNotFoundError(SCCSException):
    """Raised when a commit object is not found."""
    pass

class SCCSNotInitializedError(SCCSException):
    """Raised when SCCS has not been initialized in the current directory."""
    pass

class DocumentHashingError(SCCSException):
    """Raised when there is an error hashing a document."""
    pass

class ConvertingDocumentToHTMLError(SCCSException):
    """Raised when there is an error converting a document to HTML."""
    pass
