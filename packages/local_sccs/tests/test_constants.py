from types import MappingProxyType

class SCCSTestConstants:
    ACCEPTED_CONFIG_KEYS = ("remote", "name", "email")
    ACCEPTED_SCHEMES = ("http", "https")
    ACCEPTED_SUBCOMMANDS = ("create", "delete", "list")
    ALLOWED_NAME_AND_EMAIL_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._%+-"
    ALLOWED_REMOTE_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&"()*+,;=%'
    ALREADY_INIT_ERROR_MESSAGE = "This document has already been initialized with SCCS."
    ARGV_OBJECT_NAME = "argv"
    AUTHOR_DICT_KEY = "author"
    BRANCHES_DICT_KEY = "branches"
    BRANCHES_DIRECTORY_LIST_HEADER = "Branches:"
    BRANCH_ALREADY_EXISTS_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' already exists."
    BRANCH_COMMAND_NAME = "branch"
    BRANCH_CREATE_ARGUMENT_HELP = "The branch to create."
    BRANCH_CREATE_SUBCOMMAND = "create"
    BRANCH_CREATE_SUBCOMMAND_HELP = "Create a new branch."
    # the next constant are out of alphabetical order intentionally
    TEST_STRING = "test"
    BRANCH_CREATE_SUCCESS_MESSAGE = (
        f"Branch '{TEST_STRING}' created from 'main' successfully and "
        "is set to the current branch.\n"
    )
    BRANCH_CREATION_SUCCESS_MESSAGE_TEMPLATE = 'Branch "{branch_name}" created from "{current_branch_name}" successfully and is set to the current branch.'
    BRANCH_DELETE_ARGUMENT_HELP = "The branch to delete."
    BRANCH_DELETE_SUBCOMMAND = "delete"
    BRANCH_DELETE_SUBCOMMAND_HELP = "Delete an existing branch."
    BRANCH_DELETE_SUCCESS_MESSAGE = (
        f"Branch '{TEST_STRING}' deleted successfully.\n"
    )
    BRANCH_DELETION_SUCCESS_MESSAGE_TEMPLATE = 'Branch "{branch_name}" deleted successfully.'
    BRANCH_LIST_SUBCOMMAND = "list"
    BRANCH_LIST_SUBCOMMAND_HELP = "List all branches."
    BRANCH_MERGE_ARGUMENT_HELP = "The branch to merge into the current branch."
    BRANCH_NAME_ARGUMENT_NAME = "branch_name"
    BRANCH_NAME_FIELD_NAME = "branch name"
    BRANCH_NAME_MISSING_ERROR_MESSAGE = "Invalid subcommand or missing branch name."
    BRANCH_NOT_FOUND_ERROR_MESSAGE_TEMPLATE = "Branch '{branch_name}' is missing from repository metadata. If the branch does not exist, please create it."
    BRANCH_SWITCH_ARGUMENT_HELP = "The branch to switch to."
    BYTE_HASH_DICT_KEY = "byte_hash"
    CLASS_HTML_ATTRIBUTE = "class"
    CLONE_COMMAND_NAME = "clone"
    CLONE_DESTINATION_EXISTS_ERROR_MESSAGE = "A directory with the repository name already exists in the current directory."
    CLONE_ENDPOINT = "/clone"
    CLONE_SUCCESS_MESSAGE = "Repository cloned successfully.\n"
    COMMAND_DESCRIPTIONS = MappingProxyType({"branch": "Create a new branch, delete, or list branches.", "clone": "Clone a hosted SCCS repository with a URL.", "commit": "Commit changes to the repository.", "config": "Configure a repository's data value (remote, name, email)", "diff": "Show differences between the current document and a past commit.", "help": "Prints a help message listing the available commands and their descriptions.", "init": "Initialize a new SCCS repository.", "log": "Print a list of past commits for the current branch.", "merge": "Merge the entered branch into the current branch.", "open": "Open a commit file and update the current document.", "publish": "Publish a local repository to a hosting service.", "pull": "Pull changes from a remote repository and merge them into the local repository.", "push": "Push changes from the local repository to a remote repository.", "reset": "Delete all uncommitted changes.", "revert": "Revert the current document to the specified commit.", "status": "Check the status of the current document for uncommitted changes.", "switch": "Switch between document branches."})
    COMMAND_FIELD_NAME = "command"
    COMMA_SPACE = ", "
    COMMIT_AUTHOR_TEMPLATE = "{name} <{email}>"
    COMMIT_COMMAND_NAME = "commit"
    COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = (
        "Commit {commit_identifier} created successfully.\n"
    )
    COMMIT_IDENTIFIER_ARGUMENT_NAME = "commit_identifier"
    COMMIT_IDENTIFIER_DIFF_ARGUMENT_HELP = "The commit identifier to diff against."
    COMMIT_IDENTIFIER_DISPLAY_LENGTH = 10
    COMMIT_IDENTIFIER_FIELD_NAME = "commit byte hash"
    COMMIT_IDENTIFIER_OPEN_ARGUMENT_HELP = "The commit identifier to open."
    COMMIT_IDENTIFIER_REVERT_ARGUMENT_HELP = "The commit identifier to revert the document to."
    COMMIT_MESSAGES_DICT_KEY = "commit_messages"
    COMMIT_MESSAGE_ARGUMENT_HELP = "The message describing the commit."
    COMMIT_MESSAGE_ARGUMENT_NAME = "commit_message"
    COMMIT_MESSAGE_FIELD_NAME = "commit message"
    COMMIT_NUMBER_INCREMENT = 1
    COMMIT_ORDER_DICT_KEY = "commit_order"
    STAGED_REPOSITORY_ERROR_MESSAGE = "Failed to create or promote the staged repository. Please try again."
    CONFIG_COMMAND_NAME = "config"
    CONFIG_DICT_KEY = "config"
    CONFIG_KEY_ARGUMENT_HELP_TEMPLATE = "The configuration key to set. One of: {keys}."
    CONFIG_KEY_ARGUMENT_NAME = "key"
    CONFIG_SUCCESS_MESSAGE_TEMPLATE = (
        "Configuration '{key}' set to '{value}' successfully.\n"
    )
    CONFIG_VALUE_ARGUMENT_HELP = "The value to set the configuration key to."
    CONFIG_VALUE_ARGUMENT_NAME = "value"
    CONSTANTS_CLASSES_ADDED_OR_REMOVED_MESSAGE =(
        "{module_name} has been modified. Added: {added}, Removed: {removed}."
    )
    CONSTANTS_CLASSES_CHANGED_VALUE_MESSAGE = (
        "Constant: {module_name}.{constant_name}, Expected: {expected_value!r}, Actual:"
        " {actual_value!r}."
    )
    CONTENT_TYPE_ZIP = "application/zip"
    COPY_FROM_DIRECTORY = "copy_from"
    CREATE_SUBCOMMAND = "create"
    CURRENT_BRANCH_DELETION_ERROR_MESSAGE = "Cannot delete the current branch. Please switch to another branch first."
    CURRENT_BRANCH_DICT_KEY = "current_branch"
    CURRENT_BRANCH_MERGE_ERROR_MESSAGE = "Cannot merge the current branch into itself."
    CURRENT_BRANCH_MESSAGE_TEMPLATE = "* {branch_name} (current)"
    CWD_OBJECT_NAME = "cwd"
    DATA_DATA = "data"
    DATA_NUMBER_HTML_ATTRIBUTE = "data-number"
    DATA_REMOTE = "remote"
    DEBUG_FLAG = "--debug"
    DEBUG_FLAG_GENERAL = "debug"
    DEBUG_FLAG_SHORT = "-d"
    DEFAULT_BRANCH_DATA = MappingProxyType({"current_branch": "main", "branches": ["main"], "updated_branches": []})
    DEFAULT_HTML_STYLES = """
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
    DELETED_CONSTANT_ERROR_MESSAGE = (
        "{module_name} is missing constant: {constant_name}"
    )
    DELETED_HTML_ATTRIBUTE_VALUE = "deleted"
    DELETE_OPCODE = "delete"
    DELETE_SUBCOMMAND = "delete"
    DELETING_MAIN_ERROR_MESSAGE = "You cannot delete 'main'. Please try deleting another branch."
    DESTINATION_DIRECTORY = "destination"
    DIFF_COMMAND_NAME = "diff"
    DIFF_ERROR_MESSAGE = "Failed to generate diff output. Please try again."
    DIFF_HTML_FILE = "diff.html"
    DIFF_OUTPUT_HTML_FILE = "diff.html"
    DIFF_SUCCESS_MESSAGE = "Commit diff successfully created.\n"
    DOCUMENT_DIRECTORY = "docx"
    DOCUMENT_EXTENSION = ".docx"
    DOCUMENT_PATH_ARGUMENT_HELP = "The path to the document to initialize with SCCS."
    DOCUMENT_PATH_ARGUMENT_NAME = "document_path"
    DOUBLE_PERIOD = ".."
    EMAIL_KEY = "email"
    EMPTY_STRING = ""
    EMPTY_VALUE_ERROR_MESSAGE_TEMPLATE = "{field} cannot be empty. Please provide a valid {field}."
    ENTERED_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = "The entered file '{file_path}' does not exist. Please provide a valid file path to an existing file."
    EPOCH_ISO_DATETIME = "1970-01-01T00:00:00"
    ESCAPED_BACKSLASH = "\\"
    EXPECTED_ERROR_EXIT_CODE = 1
    FAILED_TO_GENERATE_DIFF_OUTPUT_MESSAGE = "Failed to generate diff output. Please try again."
    FILE_START_POSITION = 0
    FIRST_ELEMENT_INDEX = 0
    FLAG_DESCRIPTIONS = MappingProxyType({"debug": "Does not except Exception or SCCSException."})
    FULL_COMMIT_IDENTIFIER_LENGTH = 64
    HELP_COMMAND_NAME = "help"
    HELP_MESSAGES = ("SCCS Help", "Available commands:", "  sccs branch - Create a new branch, delete, or list branches.", "  sccs clone - Clone a hosted SCCS repository with a URL.", "  sccs commit - Commit changes to the repository.", "  sccs config - Configure a repository's data value (remote, name, email)", "  sccs diff - Show differences between the current document and a past commit.", "  sccs help - Prints a help message listing the available commands and their descriptions.", "  sccs init - Initialize a new SCCS repository.", "  sccs log - Print a list of past commits for the current branch.", "  sccs merge - Merge the entered branch into the current branch.", "  sccs open - Open a commit file and update the current document.", "  sccs publish - Publish a local repository to a hosting service.", "  sccs pull - Pull changes from a remote repository and merge them into the local repository.", "  sccs push - Push changes from the local repository to a remote repository.", "  sccs reset - Delete all uncommitted changes.", "  sccs revert - Revert the current document to the specified commit.", "  sccs status - Check the status of the current document for uncommitted changes.", "  sccs switch - Switch between document branches.", "Available flags:", "  --debug, -d - Does not except Exception or SCCSException.")
    HEX_DIGITS = "0123456789abcdef"
    HISTORY_DICT_KEY = "history"
    HTML_BOILERPLATE_TEMPLATE = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head><body>"
        "<div class='center'><div id='target'>{html}</div></div></body></html>"
    )
    HTML_DIRECTORY = "html"
    HTML_EXTENSION = ".html"
    HTML_PARSER = "html.parser"
    HTTP_OBJECTS_DICT_KEY = "objects"
    HTTP_REQUEST_ERROR_MESSAGE = "Failed to request repository from the remote URL. Please try again."
    HTTP_TIMEOUT_SECONDS = 60
    INCREMENT_ONE = 1
    INITIAL_CALL_COUNTER_VALUE = 0
    INITIAL_COMMIT_DICT_KEY = "initial_commit"
    INITIAL_COMMIT_NUMBER = 1
    INITIAL_COMMIT_NUMBER_DICT_KEY = "1"
    INITIAL_VERSION_COMMIT_MESSAGE = "initial_version"
    INIT_COMMAND_NAME = "init"
    INIT_COMMIT_MESSAGE = "Initial commit (This is a default commit message for the initial version)"
    INIT_COPY_ERROR_MESSAGE = "Failed to copy document or write HTML during initialization."
    INIT_CREATE_ERROR_MESSAGE = "Failed to create SCCS directory layout."
    INIT_SUCCESS_MESSAGE = "SCCS initialization complete."
    INLINE_TAGS = {
        "a", "b", "em", "i", "span", "strong", "u",
    }
    INPUT_CONFIG_VALUE_TEMPLATE = "Enter your {config_key}: "
    INSERTED_HTML_ATTRIBUTE_VALUE = "inserted"
    INSERT_OPCODE = "insert"
    INVALID_BRANCH_DATA_ERROR_MESSAGE = "Invalid branch data. Please ensure that the branch data has not been manually modified and the targeted branch exists."
    INVALID_BRANCH_NAME_ERROR_MESSAGE = "Invalid subcommand or missing branch name."
    INVALID_CHARACTER_IN_NAME_OR_EMAIL_ERROR_MESSAGE = "Invalid character in config value. Only letters, numbers, ., _, %, +, and - are allowed."
    INVALID_CHARACTER_IN_REMOTE_ERROR_MESSAGE = "Invalid character in URL. Only letters, numbers, and -._~:/?#[]@!$&'()*+,;=% are allowed."
    INVALID_COMMIT_HISTORY_DIRECTORY_DATA_ERROR_MESSAGE = "Invalid commit history data. Please ensure that the commit data has not been manually modified."
    INVALID_COMMIT_IDENTIFIER_ERROR_MESSAGE = "Invalid commit file name. Please provide a shortened, 10 character commit hash or the full 64 character commit hash as the commit identifier."
    INVALID_ENDING_ERROR_MESSAGE = "Invalid remote URL provided. Please provide a valid URL ending with '/clone'."
    INVALID_FILE_TYPE_ERROR_MESSAGE = "File is not a .docx file. Please provide a valid .docx file."
    INVALID_KEY_ERROR_MESSAGE = "Invalid configuration key provided. Please provide one of the valid keys: remote, name, email."
    INVALID_PATH_ENDING_ERROR_MESSAGE = 'API URL must end with "/repos/your-repo-name".'
    INVALID_REPOSITORY_NAME_ERROR_MESSAGE = "Invalid repository name. Please ensure the repository is properly initialized with a valid name."
    INVALID_SUBCOMMAND_ERROR_MESSAGE = "Invalid subcommand provided. Please provide one of the valid subcommands: create, delete, list."
    INVALID_URL_ERROR_MESSAGE = "Invalid remote URL provided. The URL must start with one of the following schemes: http, https, and use the format 'http(s)://<host>/<base-path>'. Base path is optional."
    JSON_INDENT = 4
    LAST_TAG_INDEX = -1
    LATEST_COMMIT_DICT_KEY = "latest_commit"
    LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
    LIST_SUBCOMMAND = "list"
    LOCAL_SCCS = "local_sccs"
    LOCAL_SCCS_DESCRIPTION = "Simple Contracts Communication System"
    LOG_AUTHOR_LABEL = "Author: "
    LOG_COMMAND_NAME = "log"
    LOG_COMMIT_FILE_LABEL = "Commit File: "
    LOG_DATE_LABEL = "Date: "
    LOG_DICT_KEY = "log"
    LOG_MESSAGE_LABEL = "Message: "
    LOG_SEPARATOR = "------------------------------"
    MAIN_BRANCH_NAME = "main"
    MAXIMUM_COMMIT_FILE_MATCHES = 1
    MERGE_COMMAND_NAME = "merge"
    MERGE_COMMIT_MESSAGE_TEMPLATE = 'Merged branch "{branch_name}" into "{current_branch}".'
    MERGE_DOCUMENT_COPY_ERROR_MESSAGE = "Failed to copy document during merge."
    MERGE_SUCCESS_MESSAGE_TEMPLATE = 'Successfully merged branch "{branch_name}" into branch "{current_branch}".'
    MESSAGE_DICT_KEY = "message"
    METADATA_JSON = "metadata.json"
    MINIMUM_ARGUMENTS = 2
    MINIMUM_PATH_PARTS = 2
    MISSING_REMOTE_OBJECTS_ERROR_MESSAGE = "The remote repository has extra commits that the local is missing. Please pull the latest changes before pushing."
    MISSING_RESOURCE_ERROR_MESSAGE_TEMPLATE = "Resource '{resource_name}' is missing from the repository directory."
    MULTIPLE_COMMIT_FILES_FOUND_ERROR_MESSAGE_TEMPLATE = "Multiple commit files found matching '{commit_identifier}'. Please provide a full, 64 character commit hash."
    NAME_KEY = "name"
    NEWLINE = "\n"
    NO_PATH_TEST_URL = "http://127.0.0.1:8000"
    NO_UNCOMMITTED_CHANGES = "Status Report: No uncommitted changes detected."
    NO_UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = "No uncommitted changes detected. Uncommitted changes are required before committing."
    OBJECTS_DIRECTORY = "objects"
    OLD_ROOT_TEMPLATE = "{repository_name}.old-dfad5993abfc41df9cae31a3b0c77070"
    ONE_CALL = 1
    OPEN_COMMAND_NAME = "open"
    OPEN_COPY_ERROR_MESSAGE = "Failed to copy commit file for open operation."
    OPEN_OUTPUT_FILE_NAME_TEMPLATE = "Opened_DOCX_Commit_{commit_identifier}"
    OPEN_SUCCESS_MESSAGE_TEMPLATE = 'Commit "{commit_identifier}" has been successfully opened in {output_file}. It is safe to delete this file. No changes will be lost unless {output_file} is modified after this point.'
    OTHER_BRANCH_LIST_TEMPLATE = "  {branch_name}"
    PATH_IS_ABSOLUTE_OR_CONTAINS_DOUBLE_PERIOD_ERROR_MESSAGE = "Invalid file path: {entry_path} in zip. Please ensure the path does not include '..' and is not an absolute path."
    PATH_SEPARATOR = "/"
    POST_FILE_FIELD_NAME = "file"
    PROGRAM_START_TIME = "2026-10-23T20:48:51.688278+00:00"
    PROGRAM_START_TIME_SCCS_CONSTANTS_ATTRIBUTE_NAME = "PROGRAM_START_TIME"
    PUBLISH_COMMAND_NAME = "publish"
    PUBLISH_ENDPOINT_TEMPLATE = "{base_url}/publish"
    PUBLISH_SUCCESS_MESSAGE_TEMPLATE = "Repository published successfully to {url}."
    PULL_COMMAND_NAME = "pull"
    PULL_ENDPOINT_TEMPLATE = "{base_url}/pull"
    PULL_SUCCESS_MESSAGE_TEMPLATE = "Repository pulled successfully from {url}."
    PUSH_COMMAND_NAME = "push"
    PUSH_ENDPOINT_TEMPLATE = "{base_url}/push"
    PUSH_FAILURE_ERROR_MESSAGE_TEMPLATE = "Failed to push to repository {url}."
    PUSH_HTTP_REQUEST_ERROR_MESSAGE = "The HTTP request failed while attempting to push the new changes. Please try again later or check your internet connection."
    PUSH_SUCCESS_MESSAGE_TEMPLATE = "Repository pushed successfully to {url}."
    PWD_ENVIRONMENT_VARIABLE = "PWD"
    REMOTE_KEY = "remote"
    RENAME_FUNCTION_NAME = "rename"
    REPLACE_OPCODE = "replace"
    REPOSITORIES_PATH_SEGMENT = "repos"
    REPOSITORY_NAME_FIELD_NAME = "repository name"
    REPOSITORY_NAME_PATH_INDEX = -2
    REQUIRED_PATH_ENDING_TEMPLATE = "/repos/{repo_name}"
    RESET_COMMAND_NAME = "reset"
    RESET_ERROR_MESSAGE = "Failed to reset the document. Please try again."
    RESET_SUCCESS_MESSAGE = "All uncommitted changes have been deleted. The document has been reset to the latest commit."
    REVERT_COMMAND_NAME = "revert"
    REVERT_COMMIT_MESSAGE_TEMPLATE = 'Reverted document to commit "{commit_identifier}".'
    REVERT_COPY_ERROR_MESSAGE = "Failed to revert document to selected commit. Please try again."
    REVERT_SUCCESS_MESSAGE_TEMPLATE = 'Document successfully reverted to commit "{commit_identifier}" on commit "{new_commit_identifier}".'
    RGLOB_ALL_FILES_PATTERN = "*"
    SCCS_DIRECTORY = ".sccs"
    SECOND_COMMIT_HASH = "f797d149c9887b91ebf065685775156ac33c29ccee0cb40b68f98d715114fe45"
    SECOND_COMMIT_NUMBER = 2
    SECOND_COMMIT_TEST_DOCUMENT_FILENAME = "second_commit_test_document.docx"
    SECOND_COMMIT_TEST_DOCUMENT_HTML = (
        "<p><strong>GENERAL CONTRACT AGREEMENT</strong></p>"
        "<p><em>This Agreement is entered into as of the date last signed below</em></p>"
        "<p><strong>PARTIES</strong></p>"
        "<table><tr><td>"
        "<p><strong>CLIENT / PARTY A</strong></p>"
        "<p>Full Legal Name: <strong>[Full Nae]</strong></p>"
        "<p>Address: <strong>[Street Address]</strong></p>"
        "<p>City, Province/State: <strong>[City, Province]</strong></p>"
        "<p>Email: <strong>[Email Address]</strong></p>"
        "<p>Phone: <strong>[Phone Number]</strong></p>"
        "</td><td>"
        "<p><strong>SERVICE PROVIDER / PARTY B</strong></p>"
        "<p>Full Legal Name: <strong>[Full Name]</strong></p>"
        "<p>Address: <strong>[Street Address]</strong></p>"
        "<p>City, Province/State: <strong>[City, Province]</strong></p>"
        "<p>Email: <strong>[Email Address]</strong></p>"
        "<p>Phone: <strong>[Phone Number]</strong></p>"
        "</td></tr></table>"
        "<h1><strong>1. Scope of Work</strong></h1>"
        "<p>Party B agrees to provide the following services to Party A "
        "(the &quot;Services&quot;):</p>"
        "<p><strong>[Describe the specific services, deliverables, and work to be "
        "performed in detail. Include any milestones, phases, or specifications.]"
        "</strong></p>"
        "<p>The Services shall be completed by: </p>"
        "<p><strong>Completion Date: [Date]</strong></p>"
        "<h1><strong>2. Compensation &amp; Payment Terms</strong></h1>"
        "<p>In consideration for the Services, Party A agrees to pay Party B "
        "as follows:</p>"
        "<p><strong>Total Amount: [$ Amount]</strong> CAD</p>"
        "<p><strong>Payment Schedule: [e.g., 50% upfront, 50% upon completion]"
        "</strong></p>"
        "<p><strong>Accepted Payment Methods: [e.g., e-transfer, cheque, wire]"
        "</strong></p>"
        "<p>Late payments shall accrue interest at a rate of [__]% per month "
        "on any outstanding balance. Party B reserves the right to suspend "
        "Services in the event of non-payment after [__] days written notice.</p>"
        "<h1><strong>3. Term &amp; Termination</strong></h1>"
        "<p><strong>Start Date: [Date]</strong></p>"
        "<p><strong>End Date: [Date or &quot;Upon Completion&quot;]</strong></p>"
        "<p>Either party may terminate this Agreement upon [__] days written "
        "notice to the other party. In the event of termination:</p>"
        "<ol>"
        "<li>Party A shall pay for all Services rendered up to the termination "
        "date.</li>"
        "<li>Any non-refundable deposits paid shall remain with Party B.</li>"
        "<li>Sections 5, 6, 7, and 8 shall survive termination.</li>"
        "</ol>"
        "<h1><strong>4. Intellectual Property</strong></h1>"
        "<p>Upon receipt of full payment, Party B assigns to Party A all rights, "
        "title, and interest in the deliverables produced under this Agreement, "
        "including any copyright, patent, or trade secret rights, except as "
        "follows:</p>"
        "<p><strong>[Describe any retained rights, pre-existing IP, or "
        "tools/frameworks Party B retains ownership of]</strong></p>"
        "<p>Party B retains the right to reference this project in their "
        "portfolio unless otherwise agreed in writing.</p>"
        "<h1><strong>5. Confidentiality</strong></h1>"
        "<p>Each party agrees to hold in strict confidence any proprietary or "
        "confidential information disclosed by the other party in connection "
        "with this Agreement (&quot;Confidential Information&quot;). "
        "Confidential Information shall not be disclosed to third parties "
        "without prior written consent, and shall be used solely for the "
        "purposes of this Agreement.</p>"
        "<p>This obligation shall survive the termination of this Agreement "
        "for a period of [__] years.</p>"
        "<h1><strong>6. Representations &amp; Warranties</strong></h1>"
        "<h2><strong>6.1 Party B Warrants That:</strong></h2>"
        "<ol>"
        "<li>The Services will be performed in a professional and workmanlike "
        "manner.</li>"
        "<li>Party B has the full right and authority to enter into this "
        "Agreement.</li>"
        "<li>The deliverables will not infringe upon the intellectual property "
        "rights of any third party.</li>"
        "</ol>"
        "<h2><strong>6.2 Party A Warrants That:</strong></h2>"
        "<ol>"
        "<li>Party A has the full authority to enter into this Agreement.</li>"
        "<li>All materials and information provided to Party B are accurate "
        "and lawfully obtained.</li>"
        "</ol>"
        "<h1><strong>7. Limitation of Liability</strong></h1>"
        "<p>IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, "
        "INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT "
        "OF OR IN CONNECTION WITH THIS AGREEMENT, EVEN IF ADVISED OF THE "
        "POSSIBILITY OF SUCH DAMAGES.</p>"
        "<p>Each party's total aggregate liability under this Agreement shall "
        "not exceed the total fees paid or payable under this Agreement in "
        "the [__] months immediately preceding the event giving rise to the "
        "claim.</p>"
        "<h1><strong>8. Dispute Resolution</strong></h1>"
        "<p><strong>Governing Law: </strong>This Agreement shall be governed "
        "by the laws of the Province of <strong>[Province]</strong>, Canada.</p>"
        "<p>In the event of any dispute, the parties agree to first attempt "
        "to resolve it through good-faith negotiation. If negotiation fails "
        "within 30 days, the parties agree to submit the dispute to binding "
        "arbitration in accordance with the rules of [Arbitration Body], "
        "before pursuing litigation.</p>"
        "<h1><strong>9. General Provisions</strong></h1>"
        "<h2><strong>9.1 Entire Agreement</strong></h2>"
        "<p>This Agreement constitutes the entire agreement between the parties "
        "with respect to the subject matter hereof and supersedes all prior "
        "discussions, negotiations, and agreements.</p>"
        "<h2><strong>9.2 Amendments</strong></h2>"
        "<p>This Agreement may only be amended in writing signed by both parties."
        "</p>"
        "<h2><strong>9.3 Severability</strong></h2>"
        "<p>If any provision of this Agreement is found to be unenforceable, "
        "the remaining provisions shall continue in full force and effect.</p>"
        "<h2><strong>9.4 Waiver</strong></h2>"
        "<p>Failure by either party to enforce any right under this Agreement "
        "shall not constitute a waiver of that right.</p>"
        "<h2><strong>9.5 Independent Contractors</strong></h2>"
        "<p>The parties are independent contractors. Nothing in this Agreement "
        "creates an employment, partnership, joint venture, or agency "
        "relationship between the parties.</p>"
        "<h2><strong>9.6 Notices</strong></h2>"
        "<p>All notices under this Agreement shall be in writing and delivered "
        "via email (with read receipt) or registered mail to the addresses "
        "set out above.</p>"
        "<h2><strong>9.7 Force Majeure</strong></h2>"
        "<p>Neither party shall be liable for delays or failures in performance "
        "resulting from causes beyond their reasonable control, including but "
        "not limited to acts of God, war, pandemic, government orders, or "
        "natural disasters.</p>"
        "<h1><strong>10. Signatures</strong></h1>"
        "<p>By signing below, each party agrees to be bound by the terms and "
        "conditions of this Agreement.</p>"
        "<table><tr><td>"
        "<p><strong>CLIENT / PARTY A</strong></p>"
        "<p> </p>"
        "<p><em>Signature</em></p>"
        "<p> </p>"
        "<p><em>Full Printed Name</em></p>"
        "<p> </p>"
        "<p><em>Title / Position (if applicable)</em></p>"
        "<p> </p>"
        "<p><em>Date Signed</em></p>"
        "</td><td></td><td>"
        "<p><strong>SERVICE PROVIDER / PARTY B</strong></p>"
        "<p> </p>"
        "<p><em>Signature</em></p>"
        "<p> </p>"
        "<p><em>Full Printed Name</em></p>"
        "<p> </p>"
        "<p><em>Title / Position (if applicable)</em></p>"
        "<p> </p>"
        "<p><em>Date Signed</em></p>"
        "</td></tr></table>"
        "<p><strong>WITNESS (optional)</strong></p>"
        "<table><tr><td>"
        "<p> </p>"
        "<p><em>Witness Signature</em></p>"
        "<p> </p>"
        "<p><em>Witness Full Name</em></p>"
        "<p> </p>"
        "<p><em>Date</em></p>"
        "</td><td></td><td>"
        "<p> </p>"
        "<p><em>Witness Signature</em></p>"
        "<p> </p>"
        "<p><em>Witness Full Name</em></p>"
        "<p> </p>"
        "<p><em>Date</em></p>"
        "</td></tr></table>"
        "<p><em>This is a general-purpose template. Consult a legal professional "
        "to ensure this Agreement meets your specific needs and jurisdiction."
        "</em></p>"
    )
    SECOND_COMMIT_TEST_HTML_HASH = "baf1da7b7dcc1f061fa35633b16adb4d374708c84c0ee38dbbea9f5eb8307be6"
    # the next constants are out of alphabetical order intentionally
    TEST_AUTHOR = f"{TEST_STRING} <{TEST_STRING}>"
    TEST_COMMIT_HASH = "ef4a6cd9a3fa5fd50c9f8ed03ea569671b3a41f6485d0446f891bda0ee2dd06f"
    TEST_DOCUMENT_HTML_HASH = "daf65bd44755eee379d835d36ce8eb15e6b8fecfdd7decc90822045c50c4164f"
    TIMESTAMP_DICT_KEY = "timestamp"
    UPDATED_BRANCHES_DICT_KEY = "updated_branches"
    SECOND_COMMIT_TEST_METADATA = {
        BRANCHES_DICT_KEY: {
            MAIN_BRANCH_NAME: {
                HISTORY_DICT_KEY: {
                    INITIAL_COMMIT_DICT_KEY: TEST_COMMIT_HASH,
                    LATEST_COMMIT_DICT_KEY: SECOND_COMMIT_HASH,
                    LATEST_COMMIT_NUMBER_DICT_KEY: SECOND_COMMIT_NUMBER,
                    COMMIT_ORDER_DICT_KEY: {
                        str(INITIAL_COMMIT_NUMBER): TEST_COMMIT_HASH,
                        str(SECOND_COMMIT_NUMBER): SECOND_COMMIT_HASH
                    }
                },
                LOG_DICT_KEY: {
                    TEST_COMMIT_HASH: {
                        TIMESTAMP_DICT_KEY: EPOCH_ISO_DATETIME,
                        AUTHOR_DICT_KEY: TEST_AUTHOR,
                        MESSAGE_DICT_KEY: INIT_COMMIT_MESSAGE
                    },
                    SECOND_COMMIT_HASH: {
                        TIMESTAMP_DICT_KEY: EPOCH_ISO_DATETIME,
                        AUTHOR_DICT_KEY: TEST_AUTHOR,
                        MESSAGE_DICT_KEY: TEST_STRING
                    }
                },
                BYTE_HASH_DICT_KEY: {
                    TEST_COMMIT_HASH: TEST_DOCUMENT_HTML_HASH,
                    SECOND_COMMIT_HASH: SECOND_COMMIT_TEST_HTML_HASH
                }
            }
        },
        COMMIT_MESSAGES_DICT_KEY: {
            TEST_COMMIT_HASH: INIT_COMMIT_MESSAGE,
            SECOND_COMMIT_HASH: TEST_STRING
        },
        CURRENT_BRANCH_DICT_KEY: {
            CURRENT_BRANCH_DICT_KEY: MAIN_BRANCH_NAME,
            BRANCHES_DICT_KEY: [
                MAIN_BRANCH_NAME
            ],
            UPDATED_BRANCHES_DICT_KEY: [
                MAIN_BRANCH_NAME
            ]
        },
        CONFIG_DICT_KEY: {
            NAME_KEY: TEST_STRING,
            EMAIL_KEY: TEST_STRING
        }
    }
    SECOND_ELEMENT_INDEX = 1
    SECOND_TEST_STRING = TEST_STRING + "2"
    SINGLE_PERIOD = "."
    SOURCE_FILE_DELETION_ERROR_WARNING_TEMPLATE = "Warning: could not remove source file {document_path}: {e}. The repository has been initialized."
    SOURCE_FILE_DOES_NOT_EXIST_ERROR_MESSAGE_TEMPLATE = 'Source file "{file_name}" does not exist.'
    SPACE = " "
    STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}\n"
    STATUS_CODE_ONE_HUNDRED = 100
    STATUS_CODE_TWO_HUNDRED = 200
    STATUS_COMMAND_NAME = "status"
    STORE_TRUE_ACTION = "store_true"
    STYLE_TAG_NAME = "style"
    SUBCOMMAND_FIELD_NAME = "subcommand"
    SWITCH_COMMAND_NAME = "switch"
    SWITCH_COMMIT_FILE_MISSING_ERROR_MESSAGE_TEMPLATE = 'Commit file missing for branch "{branch_name}".'
    SWITCH_COPY_ERROR_MESSAGE = "Failed to copy commit file during branch switch. Please try again."
    SWITCH_SUCCESS_MESSAGE_TEMPLATE = 'Successfully switched to branch "{branch_name}".'
    TAGS_TO_UNWRAP = ("b", "i", "u", "strong", "em", "style", "table", "tr", "td", "ol", "ul")
    TARGET_BRANCH_NOT_SET_ERROR_MESSAGE = "Target branch not set. Ensure the branch is set by using Repository*.target.set(foo)"
    TARGET_PATH_NOT_RELATIVE_TO_PARENT_DIRECTORY_ERROR_MESSAGE = "Invalid file path: {target_path} in zip. Please ensure that {target_path} is inside {destination_resolved}."
    TEMPORARY_DIRECTORY_PREFIX = "sccs_temp_"
    TEST_BRANCH_LIST_MESSAGE = f"Branches:\n  main\n* {TEST_STRING} (current)\n"
    TEST_DICTIONARY = {TEST_STRING: TEST_STRING}
    TEST_DIFF_HTML_1 = "<html><body><p>Hello <strong>bold</strong>, <em>italic</em>, and <u>underlined</u> text.</p></body></html>"
    TEST_DIFF_HTML_1_WITH_DATA_NUMBER = '<html data-number="0"><body data-number="1"><p data-number="2">Hello <strong data-number="3">bold</strong>, <em data-number="4">italic</em>, and <u data-number="5">underlined</u> text.</p></body></html>'
    TEST_DIFF_HTML_2 = "<html><body><h2>Testing <b>bold</b> and <i>italic</i> with <u>underline</u>.</h2></body></html>"
    TEST_DIFF_HTML_2_WITH_DATA_NUMBER = '<html data-number="0"><body data-number="1"><h2 data-number="2">Testing <b data-number="3">bold</b> and <i data-number="4">italic</i> with <u data-number="5">underline</u>.</h2></body></html>'
    TEST_DIFF_OUTPUT = """<!DOCTYPE html><html><head><meta charset='UTF-8'>
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
    </head><body><div class='center'><div id='target'>

<p>GENERAL CONTRACT AGREEMENT</p><p>This Agreement is entered into as of the date last signed below</p><p>PARTIES</p><p>CLIENT / PARTY A</p><p class="deleted">Full Legal Name: [Full Name]</p><p class="inserted">Full Legal Name: [Full Nae]</p><p>Address: [Street Address]</p><p>City, Province/State: [City, Province]</p><p>Email: [Email Address]</p><p>Phone: [Phone Number]</p><p>SERVICE PROVIDER / PARTY B</p><p>Full Legal Name: [Full Name]</p><p>Address: [Street Address]</p><p>City, Province/State: [City, Province]</p><p>Email: [Email Address]</p><p>Phone: [Phone Number]</p><h1>1. Scope of Work</h1><p>Party B agrees to provide the following services to Party A (the "Services"):</p><p>[Describe the specific services, deliverables, and work to be performed in detail. Include any milestones, phases, or specifications.]</p><p>The Services shall be completed by: </p><p>Completion Date: [Date]</p><h1>2. Compensation &amp; Payment Terms</h1><p>In consideration for the Services, Party A agrees to pay Party B as follows:</p><p>Total Amount: [$ Amount] CAD</p><p>Payment Schedule: [e.g., 50% upfront, 50% upon completion]</p><p>Accepted Payment Methods: [e.g., e-transfer, cheque, wire]</p><p>Late payments shall accrue interest at a rate of [__]% per month on any outstanding balance. Party B reserves the right to suspend Services in the event of non-payment after [__] days written notice.</p><h1>3. Term &amp; Termination</h1><p>Start Date: [Date]</p><p>End Date: [Date or "Upon Completion"]</p><p>Either party may terminate this Agreement upon [__] days written notice to the other party. In the event of termination:</p><li>Party A shall pay for all Services rendered up to the termination date.</li><li>Any non-refundable deposits paid shall remain with Party B.</li><li>Sections 5, 6, 7, and 8 shall survive termination.</li><h1>4. Intellectual Property</h1><p>Upon receipt of full payment, Party B assigns to Party A all rights, title, and interest in the deliverables produced under this Agreement, including any copyright, patent, or trade secret rights, except as follows:</p><p>[Describe any retained rights, pre-existing IP, or tools/frameworks Party B retains ownership of]</p><p>Party B retains the right to reference this project in their portfolio unless otherwise agreed in writing.</p><h1>5. Confidentiality</h1><p>Each party agrees to hold in strict confidence any proprietary or confidential information disclosed by the other party in connection with this Agreement ("Confidential Information"). Confidential Information shall not be disclosed to third parties without prior written consent, and shall be used solely for the purposes of this Agreement.</p><p>This obligation shall survive the termination of this Agreement for a period of [__] years.</p><h1>6. Representations &amp; Warranties</h1><h2>6.1 Party B Warrants That:</h2><li>The Services will be performed in a professional and workmanlike manner.</li><li>Party B has the full right and authority to enter into this Agreement.</li><li>The deliverables will not infringe upon the intellectual property rights of any third party.</li><h2>6.2 Party A Warrants That:</h2><li>Party A has the full authority to enter into this Agreement.</li><li>All materials and information provided to Party B are accurate and lawfully obtained.</li><h1>7. Limitation of Liability</h1><p>IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR IN CONNECTION WITH THIS AGREEMENT, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.</p><p>Each party's total aggregate liability under this Agreement shall not exceed the total fees paid or payable under this Agreement in the [__] months immediately preceding the event giving rise to the claim.</p><h1>8. Dispute Resolution</h1><p>Governing Law: This Agreement shall be governed by the laws of the Province of [Province], Canada.</p><p>In the event of any dispute, the parties agree to first attempt to resolve it through good-faith negotiation. If negotiation fails within 30 days, the parties agree to submit the dispute to binding arbitration in accordance with the rules of [Arbitration Body], before pursuing litigation.</p><h1>9. General Provisions</h1><h2>9.1 Entire Agreement</h2><p>This Agreement constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior discussions, negotiations, and agreements.</p><h2>9.2 Amendments</h2><p>This Agreement may only be amended in writing signed by both parties.</p><h2>9.3 Severability</h2><p>If any provision of this Agreement is found to be unenforceable, the remaining provisions shall continue in full force and effect.</p><h2>9.4 Waiver</h2><p>Failure by either party to enforce any right under this Agreement shall not constitute a waiver of that right.</p><h2>9.5 Independent Contractors</h2><p>The parties are independent contractors. Nothing in this Agreement creates an employment, partnership, joint venture, or agency relationship between the parties.</p><h2>9.6 Notices</h2><p>All notices under this Agreement shall be in writing and delivered via email (with read receipt) or registered mail to the addresses set out above.</p><h2>9.7 Force Majeure</h2><p>Neither party shall be liable for delays or failures in performance resulting from causes beyond their reasonable control, including but not limited to acts of God, war, pandemic, government orders, or natural disasters.</p><h1>10. Signatures</h1><p>By signing below, each party agrees to be bound by the terms and conditions of this Agreement.</p><p>CLIENT / PARTY A</p><p> </p><p>Signature</p><p> </p><p>Full Printed Name</p><p> </p><p>Title / Position (if applicable)</p><p> </p><p>Date Signed</p><p>SERVICE PROVIDER / PARTY B</p><p> </p><p>Signature</p><p> </p><p>Full Printed Name</p><p> </p><p>Title / Position (if applicable)</p><p> </p><p>Date Signed</p><p>WITNESS (optional)</p><p> </p><p>Witness Signature</p><p> </p><p>Witness Full Name</p><p> </p><p>Date</p><p> </p><p>Witness Signature</p><p> </p><p>Witness Full Name</p><p> </p><p>Date</p><p>This is a general-purpose template. Consult a legal professional to ensure this Agreement meets your specific needs and jurisdiction.</p></div></div></body></html>"""
    TEST_DOCUMENTS_DIRECTORY = "test_documents"
    TEST_DOCUMENT_FILENAME = "test_document.docx"
    TEST_DOCUMENT_HTML = (
        "<p><strong>GENERAL CONTRACT AGREEMENT</strong></p>"
        "<p><em>This Agreement is entered into as of the date last signed below</em></p>"
        "<p><strong>PARTIES</strong></p>"
        "<table><tr><td>"
        "<p><strong>CLIENT / PARTY A</strong></p>"
        "<p>Full Legal Name: <strong>[Full Name]</strong></p>"
        "<p>Address: <strong>[Street Address]</strong></p>"
        "<p>City, Province/State: <strong>[City, Province]</strong></p>"
        "<p>Email: <strong>[Email Address]</strong></p>"
        "<p>Phone: <strong>[Phone Number]</strong></p>"
        "</td><td>"
        "<p><strong>SERVICE PROVIDER / PARTY B</strong></p>"
        "<p>Full Legal Name: <strong>[Full Name]</strong></p>"
        "<p>Address: <strong>[Street Address]</strong></p>"
        "<p>City, Province/State: <strong>[City, Province]</strong></p>"
        "<p>Email: <strong>[Email Address]</strong></p>"
        "<p>Phone: <strong>[Phone Number]</strong></p>"
        "</td></tr></table>"
        "<h1><strong>1. Scope of Work</strong></h1>"
        "<p>Party B agrees to provide the following services to Party A "
        "(the &quot;Services&quot;):</p>"
        "<p><strong>[Describe the specific services, deliverables, and work to be "
        "performed in detail. Include any milestones, phases, or specifications.]"
        "</strong></p>"
        "<p>The Services shall be completed by: </p>"
        "<p><strong>Completion Date: [Date]</strong></p>"
        "<h1><strong>2. Compensation &amp; Payment Terms</strong></h1>"
        "<p>In consideration for the Services, Party A agrees to pay Party B "
        "as follows:</p>"
        "<p><strong>Total Amount: [$ Amount]</strong> CAD</p>"
        "<p><strong>Payment Schedule: [e.g., 50% upfront, 50% upon completion]"
        "</strong></p>"
        "<p><strong>Accepted Payment Methods: [e.g., e-transfer, cheque, wire]"
        "</strong></p>"
        "<p>Late payments shall accrue interest at a rate of [__]% per month "
        "on any outstanding balance. Party B reserves the right to suspend "
        "Services in the event of non-payment after [__] days written notice.</p>"
        "<h1><strong>3. Term &amp; Termination</strong></h1>"
        "<p><strong>Start Date: [Date]</strong></p>"
        "<p><strong>End Date: [Date or &quot;Upon Completion&quot;]</strong></p>"
        "<p>Either party may terminate this Agreement upon [__] days written "
        "notice to the other party. In the event of termination:</p>"
        "<ol>"
        "<li>Party A shall pay for all Services rendered up to the termination "
        "date.</li>"
        "<li>Any non-refundable deposits paid shall remain with Party B.</li>"
        "<li>Sections 5, 6, 7, and 8 shall survive termination.</li>"
        "</ol>"
        "<h1><strong>4. Intellectual Property</strong></h1>"
        "<p>Upon receipt of full payment, Party B assigns to Party A all rights, "
        "title, and interest in the deliverables produced under this Agreement, "
        "including any copyright, patent, or trade secret rights, except as "
        "follows:</p>"
        "<p><strong>[Describe any retained rights, pre-existing IP, or "
        "tools/frameworks Party B retains ownership of]</strong></p>"
        "<p>Party B retains the right to reference this project in their "
        "portfolio unless otherwise agreed in writing.</p>"
        "<h1><strong>5. Confidentiality</strong></h1>"
        "<p>Each party agrees to hold in strict confidence any proprietary or "
        "confidential information disclosed by the other party in connection "
        "with this Agreement (&quot;Confidential Information&quot;). "
        "Confidential Information shall not be disclosed to third parties "
        "without prior written consent, and shall be used solely for the "
        "purposes of this Agreement.</p>"
        "<p>This obligation shall survive the termination of this Agreement "
        "for a period of [__] years.</p>"
        "<h1><strong>6. Representations &amp; Warranties</strong></h1>"
        "<h2><strong>6.1 Party B Warrants That:</strong></h2>"
        "<ol>"
        "<li>The Services will be performed in a professional and workmanlike "
        "manner.</li>"
        "<li>Party B has the full right and authority to enter into this "
        "Agreement.</li>"
        "<li>The deliverables will not infringe upon the intellectual property "
        "rights of any third party.</li>"
        "</ol>"
        "<h2><strong>6.2 Party A Warrants That:</strong></h2>"
        "<ol>"
        "<li>Party A has the full authority to enter into this Agreement.</li>"
        "<li>All materials and information provided to Party B are accurate "
        "and lawfully obtained.</li>"
        "</ol>"
        "<h1><strong>7. Limitation of Liability</strong></h1>"
        "<p>IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, "
        "INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT "
        "OF OR IN CONNECTION WITH THIS AGREEMENT, EVEN IF ADVISED OF THE "
        "POSSIBILITY OF SUCH DAMAGES.</p>"
        "<p>Each party's total aggregate liability under this Agreement shall "
        "not exceed the total fees paid or payable under this Agreement in "
        "the [__] months immediately preceding the event giving rise to the "
        "claim.</p>"
        "<h1><strong>8. Dispute Resolution</strong></h1>"
        "<p><strong>Governing Law: </strong>This Agreement shall be governed "
        "by the laws of the Province of <strong>[Province]</strong>, Canada.</p>"
        "<p>In the event of any dispute, the parties agree to first attempt "
        "to resolve it through good-faith negotiation. If negotiation fails "
        "within 30 days, the parties agree to submit the dispute to binding "
        "arbitration in accordance with the rules of [Arbitration Body], "
        "before pursuing litigation.</p>"
        "<h1><strong>9. General Provisions</strong></h1>"
        "<h2><strong>9.1 Entire Agreement</strong></h2>"
        "<p>This Agreement constitutes the entire agreement between the parties "
        "with respect to the subject matter hereof and supersedes all prior "
        "discussions, negotiations, and agreements.</p>"
        "<h2><strong>9.2 Amendments</strong></h2>"
        "<p>This Agreement may only be amended in writing signed by both parties."
        "</p>"
        "<h2><strong>9.3 Severability</strong></h2>"
        "<p>If any provision of this Agreement is found to be unenforceable, "
        "the remaining provisions shall continue in full force and effect.</p>"
        "<h2><strong>9.4 Waiver</strong></h2>"
        "<p>Failure by either party to enforce any right under this Agreement "
        "shall not constitute a waiver of that right.</p>"
        "<h2><strong>9.5 Independent Contractors</strong></h2>"
        "<p>The parties are independent contractors. Nothing in this Agreement "
        "creates an employment, partnership, joint venture, or agency "
        "relationship between the parties.</p>"
        "<h2><strong>9.6 Notices</strong></h2>"
        "<p>All notices under this Agreement shall be in writing and delivered "
        "via email (with read receipt) or registered mail to the addresses "
        "set out above.</p>"
        "<h2><strong>9.7 Force Majeure</strong></h2>"
        "<p>Neither party shall be liable for delays or failures in performance "
        "resulting from causes beyond their reasonable control, including but "
        "not limited to acts of God, war, pandemic, government orders, or "
        "natural disasters.</p>"
        "<h1><strong>10. Signatures</strong></h1>"
        "<p>By signing below, each party agrees to be bound by the terms and "
        "conditions of this Agreement.</p>"
        "<table><tr><td>"
        "<p><strong>CLIENT / PARTY A</strong></p>"
        "<p> </p>"
        "<p><em>Signature</em></p>"
        "<p> </p>"
        "<p><em>Full Printed Name</em></p>"
        "<p> </p>"
        "<p><em>Title / Position (if applicable)</em></p>"
        "<p> </p>"
        "<p><em>Date Signed</em></p>"
        "</td><td></td><td>"
        "<p><strong>SERVICE PROVIDER / PARTY B</strong></p>"
        "<p> </p>"
        "<p><em>Signature</em></p>"
        "<p> </p>"
        "<p><em>Full Printed Name</em></p>"
        "<p> </p>"
        "<p><em>Title / Position (if applicable)</em></p>"
        "<p> </p>"
        "<p><em>Date Signed</em></p>"
        "</td></tr></table>"
        "<p><strong>WITNESS (optional)</strong></p>"
        "<table><tr><td>"
        "<p> </p>"
        "<p><em>Witness Signature</em></p>"
        "<p> </p>"
        "<p><em>Witness Full Name</em></p>"
        "<p> </p>"
        "<p><em>Date</em></p>"
        "</td><td></td><td>"
        "<p> </p>"
        "<p><em>Witness Signature</em></p>"
        "<p> </p>"
        "<p><em>Witness Full Name</em></p>"
        "<p> </p>"
        "<p><em>Date</em></p>"
        "</td></tr></table>"
        "<p><em>This is a general-purpose template. Consult a legal professional "
        "to ensure this Agreement meets your specific needs and jurisdiction."
        "</em></p>"
    )
    
    TEST_DOCUMENT_REPOSITORY_NAME = "test_document"
    TEST_DOCX_FILENAME = "test.docx"
    TEST_FINAL_ROOT = "test_final_root"
    TEST_FOLDER_DIRECTORY = "folder"
    TEST_INITIALIZATION_METADATA = {
        BRANCHES_DICT_KEY: {
            MAIN_BRANCH_NAME: {
                HISTORY_DICT_KEY: {
                    INITIAL_COMMIT_DICT_KEY: TEST_COMMIT_HASH,
                    LATEST_COMMIT_DICT_KEY: TEST_COMMIT_HASH,
                    LATEST_COMMIT_NUMBER_DICT_KEY: INITIAL_COMMIT_NUMBER,
                    COMMIT_ORDER_DICT_KEY: {
                        str(INITIAL_COMMIT_NUMBER): TEST_COMMIT_HASH
                    }
                },
                LOG_DICT_KEY: {
                    TEST_COMMIT_HASH: {
                        TIMESTAMP_DICT_KEY: EPOCH_ISO_DATETIME,
                        AUTHOR_DICT_KEY: TEST_AUTHOR,
                        MESSAGE_DICT_KEY: INIT_COMMIT_MESSAGE
                    }
                },
                BYTE_HASH_DICT_KEY: {
                    TEST_COMMIT_HASH: TEST_DOCUMENT_HTML_HASH
                }
            }
        },
        COMMIT_MESSAGES_DICT_KEY: {
            TEST_COMMIT_HASH: INIT_COMMIT_MESSAGE
        },
        CURRENT_BRANCH_DICT_KEY: {
            CURRENT_BRANCH_DICT_KEY: MAIN_BRANCH_NAME,
            BRANCHES_DICT_KEY: [
                MAIN_BRANCH_NAME
            ],
            UPDATED_BRANCHES_DICT_KEY: []
        },
        CONFIG_DICT_KEY: {
            NAME_KEY: TEST_STRING,
            EMAIL_KEY: TEST_STRING
        }
    }
    TEST_MESSAGE_TEMPLATE = "Test {url}"
    TEST_REPOSITORY_CLONE_URL = "http://127.0.0.1:8000/test/test/clone"
    TEST_REPOSITORY_DIFF_HTML = (
        """<p data-number="1">GENERAL CONTRACT AGREEMENT</p><p data-number="3">This Agreement is entered into as of the date last signed below</p><p data-number="5">PARTIES</p><p data-number="10">CLIENT / PARTY A</p><p class="deleted" data-number="12">Full Legal Name: [Full Name]</p><p class="inserted" data-number="11">Full Legal Name: [Full Nae]</p><p data-number="14">Address: [Street Address]</p><p data-number="16">City, Province/State: [City, Province]</p><p data-number="18">Email: [Email Address]</p><p data-number="20">Phone: [Phone Number]</p><p data-number="23">SERVICE PROVIDER / PARTY B</p><p data-number="25">Full Legal Name: [Full Name]</p><p data-number="27">Address: [Street Address]</p><p data-number="29">City, Province/State: [City, Province]</p><p data-number="31">Email: [Email Address]</p><p data-number="33">Phone: [Phone Number]</p><h1 data-number="35">1. Scope of Work</h1><p data-number="37">Party B agrees to provide the following services to Party A (the "Services"):</p><p data-number="38">[Describe the specific services, deliverables, and work to be performed in detail. Include any milestones, phases, or specifications.]</p><p data-number="40">The Services shall be completed by: </p><p data-number="41">Completion Date: [Date]</p><h1 data-number="43">2. Compensation &amp; Payment Terms</h1><p data-number="45">In consideration for the Services, Party A agrees to pay Party B as follows:</p><p data-number="46">Total Amount: [$ Amount] CAD</p><p data-number="48">Payment Schedule: [e.g., 50% upfront, 50% upon completion]</p><p data-number="50">Accepted Payment Methods: [e.g., e-transfer, cheque, wire]</p><p data-number="52">Late payments shall accrue interest at a rate of [__]% per month on any outstanding balance. Party B reserves the right to suspend Services in the event of non-payment after [__] days written notice.</p><h1 data-number="53">3. Term &amp; Termination</h1><p data-number="55">Start Date: [Date]</p><p data-number="57">End Date: [Date or "Upon Completion"]</p><p data-number="59">Either party may terminate this Agreement upon [__] days written notice to the other party. In the event of termination:</p><li data-number="61">Party A shall pay for all Services rendered up to the termination date.</li><li data-number="62">Any non-refundable deposits paid shall remain with Party B.</li><li data-number="63">Sections 5, 6, 7, and 8 shall survive termination.</li><h1 data-number="64">4. Intellectual Property</h1><p data-number="66">Upon receipt of full payment, Party B assigns to Party A all rights, title, and interest in the deliverables produced under this Agreement, including any copyright, patent, or trade secret rights, except as follows:</p><p data-number="67">[Describe any retained rights, pre-existing IP, or tools/frameworks Party B retains ownership of]</p><p data-number="69">Party B retains the right to reference this project in their portfolio unless otherwise agreed in writing.</p><h1 data-number="70">5. Confidentiality</h1><p data-number="72">Each party agrees to hold in strict confidence any proprietary or confidential information disclosed by the other party in connection with this Agreement ("Confidential Information"). Confidential Information shall not be disclosed to third parties without prior written consent, and shall be used solely for the purposes of this Agreement.</p><p data-number="73">This obligation shall survive the termination of this Agreement for a period of [__] years.</p><h1 data-number="74">6. Representations &amp; Warranties</h1><h2 data-number="76">6.1 Party B Warrants That:</h2><li data-number="79">The Services will be performed in a professional and workmanlike manner.</li><li data-number="80">Party B has the full right and authority to enter into this Agreement.</li><li data-number="81">The deliverables will not infringe upon the intellectual property rights of any third party.</li><h2 data-number="82">6.2 Party A Warrants That:</h2><li data-number="85">Party A has the full authority to enter into this Agreement.</li><li data-number="86">All materials and information provided to Party B are accurate and lawfully obtained.</li><h1 data-number="87">7. Limitation of Liability</h1><p data-number="89">IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR IN CONNECTION WITH THIS AGREEMENT, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.</p><p data-number="90">Each party's total aggregate liability under this Agreement shall not exceed the total fees paid or payable under this Agreement in the [__] months immediately preceding the event giving rise to the claim.</p><h1 data-number="91">8. Dispute Resolution</h1><p data-number="93">Governing Law: This Agreement shall be governed by the laws of the Province of [Province], Canada.</p><p data-number="96">In the event of any dispute, the parties agree to first attempt to resolve it through good-faith negotiation. If negotiation fails within 30 days, the parties agree to submit the dispute to binding arbitration in accordance with the rules of [Arbitration Body], before pursuing litigation.</p><h1 data-number="97">9. General Provisions</h1><h2 data-number="99">9.1 Entire Agreement</h2><p data-number="101">This Agreement constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior discussions, negotiations, and agreements.</p><h2 data-number="102">9.2 Amendments</h2><p data-number="104">This Agreement may only be amended in writing signed by both parties.</p><h2 data-number="105">9.3 Severability</h2><p data-number="107">If any provision of this Agreement is found to be unenforceable, the remaining provisions shall continue in full force and effect.</p><h2 data-number="108">9.4 Waiver</h2><p data-number="110">Failure by either party to enforce any right under this Agreement shall not constitute a waiver of that right.</p><h2 data-number="111">9.5 Independent Contractors</h2><p data-number="113">The parties are independent contractors. Nothing in this Agreement creates an employment, partnership, joint venture, or agency relationship between the parties.</p><h2 data-number="114">9.6 Notices</h2><p data-number="116">All notices under this Agreement shall be in writing and delivered via email (with read receipt) or registered mail to the addresses set out above.</p><h2 data-number="117">9.7 Force Majeure</h2><p data-number="119">Neither party shall be liable for delays or failures in performance resulting from causes beyond their reasonable control, including but not limited to acts of God, war, pandemic, government orders, or natural disasters.</p><h1 data-number="120">10. Signatures</h1><p data-number="122">By signing below, each party agrees to be bound by the terms and conditions of this Agreement.</p><p data-number="126">CLIENT / PARTY A</p><p data-number="128"> </p><p data-number="129">Signature</p><p data-number="131"> </p><p data-number="132">Full Printed Name</p><p data-number="134"> </p><p data-number="135">Title / Position (if applicable)</p><p data-number="137"> </p><p data-number="138">Date Signed</p><p data-number="142">SERVICE PROVIDER / PARTY B</p><p data-number="144"> </p><p data-number="145">Signature</p><p data-number="147"> </p><p data-number="148">Full Printed Name</p><p data-number="150"> </p><p data-number="151">Title / Position (if applicable)</p><p data-number="153"> </p><p data-number="154">Date Signed</p><p data-number="156">WITNESS (optional)</p><p data-number="161"> </p><p data-number="162">Witness Signature</p><p data-number="164"> </p><p data-number="165">Witness Full Name</p><p data-number="167"> </p><p data-number="168">Date</p><p data-number="172"> </p><p data-number="173">Witness Signature</p><p data-number="175"> </p><p data-number="176">Witness Full Name</p><p data-number="178"> </p><p data-number="179">Date</p><p data-number="181">This is a general-purpose template. Consult a legal professional to ensure this Agreement meets your specific needs and jurisdiction.</p>"""
    )
    TEST_STAGING_ROOT = "test_staging_root"
    TEST_SYMLINK_DIRECTORY = "link"
    TEST_TEXT_FILENAME = "test.txt"
    TEST_ZIP_FILENAME = "test.zip"
    UNCOMMITTED_CHANGES_DETECTED_ERROR_MESSAGE = "Uncommitted changes detected. Please clean the working tree before proceeding."
    UNCOMMITTED_CHANGES_FOUND = "Status Report: Uncommitted changes detected."
    UNEXPECTED_ERROR_EXIT_CODE = 2
    UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE = "Unknown command: {command}"
    URL_ARGUMENT_HELP = "The URL of the hosted repository to clone."
    URL_ARGUMENT_NAME = "url"
    URL_FIELD_NAME = "URL"
    UTF_8 = "utf-8"
    UTILS_ARGUMENT_ERROR_MESSAGE = "Required argument missing. Please provide the required argument."
    VIEW_HTML_DIRECTORY = "view_html"
    WALK_ROOT = "."
    ZIPFILE_MODULE_NAME = "zipfile"
    ZIPPING_FILE_ERROR_MESSAGE = "Failed to zip current working directory."
    ZIP_BUFFER_CREATION_FAILED_ERROR_MESSAGE = "Failed to create a buffer for the zipped repository. Please try again."
    ZIP_BUFFER_SEEK_ERROR_MESSAGE = "Failed to reset buffer position. Please try again."
    ZIP_EXTENSION = ".zip"
