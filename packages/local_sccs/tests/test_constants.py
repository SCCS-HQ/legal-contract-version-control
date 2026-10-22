import datetime
import hashlib


class SCCSTestConstants:
    ARGV_OBJECT_NAME = "argv"
    AUTHOR_DICT_KEY = "author"

    BRANCHES_DICT_KEY = "branches"
    BYTE_HASH_DICT_KEY = "byte_hash"

    CLONE_SUCCESS_MESSAGE = "Repository cloned successfully.\n"
    COMMIT_AUTHOR_TEMPLATE = "{name} <{email}>"
    COMMIT_CREATED_SUCCESS_MESSAGE_TEMPLATE = (
        "Commit {commit_identifier} created successfully.\n"
    )
    COMMIT_IDENTIFIER_DISPLAY_LENGTH = 10
    COMMIT_MESSAGES_DICT_KEY = "commit_messages"
    COMMIT_ORDER_DICT_KEY = "commit_order"
    CONFIG_DICT_KEY = "config"
    CONFIG_SUCCESS_MESSAGE_TEMPLATE = (
        "Configuration '{key}' set to '{value}' successfully.\n"
    )
    CONSTANTS_CLASSES_ADDED_OR_REMOVED_MESSAGE =(
        "{module_name} has been modified. Added: {added}, Removed: {removed}."
    )
    CONSTANTS_CLASSES_CHANGED_VALUE_MESSAGE = (
        "Constant: {module_name}.{constant_name}, Expected: {expected_value!r}, Actual:"
        " {actual_value!r}."
    )
    COPY_FROM_DIRECTORY = "copy_from"
    CURRENT_BRANCH_DICT_KEY = "current_branch"
    CWD_OBJECT_NAME = "cwd"

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
    DESTINATION_DIRECTORY = "destination"
    DIFF_SUCCESS_MESSAGE = "Commit diff successfully created.\n"
    DOCUMENT_DIRECTORY = "docx"
    DOCUMENT_EXTENSION = ".docx"

    EMAIL_KEY = "email"
    EMPTY_STRING = ""
    EPOCH_ISO_DATETIME = datetime.datetime(1970, 1, 1, 0, 0, 0).isoformat()
    ESCAPED_BACKSLASH = "\\"

    FIRST_ELEMENT_INDEX = 0

    HEX_DIGITS = "0123456789abcdef"
    HISTORY_DICT_KEY = "history"
    HTML_BOILERPLATE_TEMPLATE = (
        "<!DOCTYPE html><html><head><meta charset='UTF-8'>{styles}</head><body>"
        "<div class='center'><div id='target'>{html}</div></div></body></html>"
    )
    HTML_DIRECTORY = "html"
    HTML_EXTENSION = ".html"
    HTML_PARSER = "html.parser"

    INCREMENT_ONE = 1
    INITIAL_CALL_COUNTER_VALUE = 0
    INITIAL_COMMIT_DICT_KEY = "initial_commit"
    INITIAL_COMMIT_NUMBER = 1
    INIT_COMMIT_MESSAGE = "Initial commit (This is a default commit message for the initial version)"

    JSON_INDENT = 4

    LATEST_COMMIT_DICT_KEY = "latest_commit"
    LATEST_COMMIT_NUMBER_DICT_KEY = "latest_commit_number"
    LOG_DICT_KEY = "log"

    MAIN_BRANCH_NAME = "main"
    MESSAGE_DICT_KEY = "message"
    METADATA_JSON = "metadata.json"

    NAME_KEY = "name"
    NEWLINE = "\n"
    NO_PATH_TEST_URL = "http://127.0.0.1:8000"

    OBJECTS_DIRECTORY = "objects"
    ONE_CALL = 1

    PATH_SEPARATOR = "/"
    PROGRAM_START_TIME_SCCS_CONSTANTS_ATTRIBUTE_NAME = "PROGRAM_START_TIME"
    PWD_ENVIRONMENT_VARIABLE = "PWD"

    REMOTE_KEY = "remote"
    RENAME_FUNCTION_NAME = "rename"
    RGLOB_ALL_FILES_PATTERN = "*"

    SCCS_DIRECTORY = ".sccs"

    # Next constants out of alphabetical order as they would be used by constants defined before it
    TEST_STRING = "test"
    UTF_8 = "utf-8"
    SECOND_COMMIT_HASH = hashlib.sha256(
        PATH_SEPARATOR.join(
            [
                EPOCH_ISO_DATETIME,
                TEST_STRING,
                TEST_STRING,
                TEST_STRING
            ]
        ).encode(UTF_8)
    ).hexdigest()
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
    SECOND_COMMIT_TEST_HTML_HASH = hashlib.sha256(
        SECOND_COMMIT_TEST_DOCUMENT_HTML.encode(UTF_8)
    ).hexdigest()
    # Next constants out of alphabetical order as they would be used by constants defined before it
    TEST_AUTHOR = COMMIT_AUTHOR_TEMPLATE.format(name=TEST_STRING, email=TEST_STRING)
    TEST_COMMIT_HASH = hashlib.sha256(
        PATH_SEPARATOR.join(
            [
                EPOCH_ISO_DATETIME,
                INIT_COMMIT_MESSAGE,
                TEST_STRING,
                TEST_STRING
            ]
        ).encode(UTF_8)
    ).hexdigest()
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
    TEST_DOCUMENT_HTML_HASH = hashlib.sha256(
        TEST_DOCUMENT_HTML.encode(UTF_8)
    ).hexdigest()
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
    SECOND_TEST_STRING = "test2"
    SPACE = " "
    STATUS_CODE_MESSAGE_TEMPLATE = "Status Code: {status_code}\n"
    STATUS_CODE_ONE_HUNDRED = 100
    STATUS_CODE_TWO_HUNDRED = 200

    TEMPORARY_DIRECTORY_PREFIX = "sccs_temp_"
    TEST_DICTIONARY = {TEST_STRING: TEST_STRING}
    TEST_DIFF_HTML = """
    <html>
        <head>
            <style>p { color: red; }</style>
            <title>Test Document</title>
        </head>
        <body>
            <h1>Test Heading</h1>
            <p>
                First
                <b>bold text</b>
                and <i>italic text</i>.
            </p>
            <div>
                <p><strong>Important</strong> information.</p>
                <p><em>Emphasized</em> content with <u>underlining</u>.</p>
            </div>
            <table>
                <tr>
                    <td>First cell</td>
                    <td><strong>Second cell</strong></td>
                </tr>
                <tr>
                    <td>Third cell</td>
                    <td>Fourth cell</td>
                </tr>
            </table>
            <ol>
                <li>First ordered item</li>
                <li>Second ordered item</li>
            </ol>
            <ul>
                <li>First unordered item</li>
                <li>Second unordered item</li>
            </ul>
        </body>
    </html>
    """
    TEST_DIFF_HTML_WITH_DATA_NUMBER = """
    <html data-number="0">
        <head data-number="1">
            <style data-number="2">p { color: red; }</style>
            <title data-number="3">Test Document</title>
        </head>
        <body data-number="4">
            <h1 data-number="5">Test Heading</h1>
            <p data-number="6">
                First
                <b data-number="7">bold text</b>
                and <i data-number="8">italic text</i>.
            </p>
            <div data-number="9">
                <p data-number="10"><strong data-number="11">Important</strong> information.</p>
                <p data-number="12"><em data-number="13">Emphasized</em> content with <u data-number="14">underlining</u>.</p>
            </div>
            <table data-number="15">
                <tr data-number="16">
                    <td data-number="17">First cell</td>
                    <td data-number="18"><strong data-number="19">Second cell</strong></td>
                </tr>
                <tr data-number="20">
                    <td data-number="21">Third cell</td>
                    <td data-number="22">Fourth cell</td>
                </tr>
            </table>
            <ol data-number="23">
                <li data-number="24">First ordered item</li>
                <li data-number="25">Second ordered item</li>
            </ol>
            <ul data-number="26">
                <li data-number="27">First unordered item</li>
                <li data-number="28">Second unordered item</li>
            </ul>
        </body>
    </html>
    """
    TEST_DOCUMENTS_DIRECTORY = "test_documents"
    TEST_DOCUMENT_FILENAME = "test_document.docx"
    TEST_DOCUMENT_HTML_HASH = hashlib.sha256(
        TEST_DOCUMENT_HTML.encode(UTF_8)
    ).hexdigest()
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
    TEST_STAGING_ROOT = "test_staging_root"
    TEST_SYMLINK_DIRECTORY = "link"
    TEST_TEXT_FILENAME = "test.txt"
    TEST_ZIP_FILENAME = "test.zip"

    VIEW_HTML_DIRECTORY = "view_html"

    ZIPFILE_MODULE_NAME = "zipfile"
