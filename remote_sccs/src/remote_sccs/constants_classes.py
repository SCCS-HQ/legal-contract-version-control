import uuid

class RemoteErrorWrappers:
    """
    A class to hold the templates used to wrap expected and unexpected errors raised
    while running a command.
    """

    UNEXPECTED_ERROR_TEMPLATE = "An unexpected error occurred: {type_name}: {e}"

class RemoteSCCSConstants:
    UNEXPECTED_ERROR_EXIT_CODE = 2
    COMMAND_FIELD_NAME = "command"
    SERVE_COMMAND_NAME = "serve"
    BRANCHES_DIRECTORY = "branches"
    BYTES_PER_MEGABYTE = 1024 * 1024
    CLONE_ENDPOINT_TEMPLATE = "/repos/{repository_name}/clone"
    CONTENT_DISPOSITION_HEADER_TITLE = "Content-Disposition"
    CONTENT_DISPOSITION_HEADER_TEMPLATE = "attachment;filename={repository_name}.zip"
    CONTENT_DISPOSITION_HEADER_SPACED_TEMPLATE = (
        "attachment; filename={repository_name}.zip"
    )
    CURRENT_BRANCH_DICT_KEY = "current_branch"
    DOUBLE_PERIOD = ".."
    EASTER_EGG_MESSAGE = "Boo!"
    FILE_PUBLISHED_MESSAGE = "File published successfully"
    FILE_START_POSITION = 0
    FILE_TOO_LARGE_ERROR_MESSAGE_TEMPLATE = "File {filename} is too large"
    HTTP_BAD_REQUEST_STATUS_CODE = 400
    HTTP_NOT_FOUND_STATUS_CODE = 404
    INVALID_JSON_ERROR_MESSAGE = "Invalid JSON data"
    INVALID_REPOSITORY_NAME_ERROR_MESSAGE = "Invalid repository name"
    INVALID_ZIP_PATH_ERROR_MESSAGE = "Invalid file path in zip"
    NETWORK_IP = "0.0.0.0"
    LOCAL_UNKNOWN_OBJECTS_ERROR_MESSAGE = (
        "Local repository has objects that the remote does not have. Run 'sccs push"
        "' to upload these objects before pulling."
    )
    MAX_FILES_IN_ZIP = 1000
    MAX_INDIVIDUAL_FILE_SIZE = 10 * BYTES_PER_MEGABYTE
    MAX_TOTAL_UPLOAD_SIZE = 100 * BYTES_PER_MEGABYTE
    MESSAGES_DICT_KEY = "message"
    METADATA_JSON = "metadata.json"
    NEWLINE = "\n"
    OBJECTS_DICT_KEY = "objects"
    OBJECTS_DIRECTORY = "objects"
    OBJECTS_NOT_FOUND_ERROR_MESSAGE = "Repository objects not found"
    OLD_ROOT_TEMPLATE = f"{{repository_name}}.old-{uuid.uuid4().hex}"
    PUBLISH_ENDPOINT_TEMPLATE = "/repos/{repository_name}/publish"
    PULL_ENDPOINT_TEMPLATE = "/repos/{repository_name}/pull"
    PUSH_ENDPOINT_TEMPLATE = "/repos/{repository_name}/push"
    PUSH_SUCCESS_MESSAGE = "changes pushed successfully"
    REMOTE_KEY = "remote"
    REMOTE_SCCS = "remote_sccs"
    REMOTE_SCCS_DESCRIPTION = "Remote API for Self-Hosting of SCCS"
    REMOTE_URL_REQUIRED_ERROR_MESSAGE = "Remote URL is required"
    REPOSITORIES_BASE_DIRECTORY = "./repos"
    REPOSITORY_EXISTS_ERROR_MESSAGE = "Repository already exists"
    REPOSITORY_NAME_MISMATCH_ERROR_MESSAGE = "Repository name does not match file name"
    REPOSITORY_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = "Repository not found: {repository_name}"
    REPOSITORY_URL_DICT_KEY = "repository_url"
    RGLOB_ALL_FILES_PATTERN = "*"
    REPOS_MOUNT_ENDPOINT = "/repos"
    ROOT_ENDPOINT = "/"
    SCCS_DIRECTORY = ".sccs"
    SINGLE_PERIOD = "."
    STATIC_FILES_NAME = "repos"
    TEMPORARY_DIRECTORY_PREFIX = "sccs_temp_"
    TOO_MANY_FILES_ERROR_MESSAGE = "Too many files in the uploaded zip"
    UPDATED_BRANCHES_DICT_KEY = "updated_branches"
    UPLOAD_TOO_LARGE_ERROR_MESSAGE = "Uploaded file is too large"
    UTF_8 = "utf-8"
    CONTENT_TYPE_ZIP = "application/zip"
