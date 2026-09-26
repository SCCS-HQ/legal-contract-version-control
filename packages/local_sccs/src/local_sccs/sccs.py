import argparse
import sys
from pathlib import Path

import local_sccs.branch as branch
import local_sccs.clone as clone
import local_sccs.commit as commit
import local_sccs.config as config
import local_sccs.diff as diff
import local_sccs.exceptions as exceptions
import local_sccs.help as help
import local_sccs.init as init
import local_sccs.log as log
import local_sccs.merge as merge
import local_sccs.open as open
import local_sccs.publish as publish
import local_sccs.pull as pull
import local_sccs.push as push
import local_sccs.reset as reset
import local_sccs.revert as revert
import local_sccs.status as status
import local_sccs.switch as switch
import local_sccs.utils as utils
from local_sccs.constants_classes import ErrorWrappers, SCCSConstants
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)

c = SCCSConstants()
COMMANDS = {
    c.BRANCH_COMMAND_NAME: branch.main,
    c.CLONE_COMMAND_NAME: clone.main,
    c.COMMIT_COMMAND_NAME: commit.main,
    c.CONFIG_COMMAND_NAME: config.main,
    c.DIFF_COMMAND_NAME: diff.main,
    c.HELP_COMMAND_NAME: help.main,
    c.INIT_COMMAND_NAME: init.main,
    c.LOG_COMMAND_NAME: log.main,
    c.MERGE_COMMAND_NAME: merge.main,
    c.OPEN_COMMAND_NAME: open.main,
    c.PUBLISH_COMMAND_NAME: publish.main,
    c.PULL_COMMAND_NAME: pull.main,
    c.PUSH_COMMAND_NAME: push.main,
    c.RESET_COMMAND_NAME: reset.main,
    c.REVERT_COMMAND_NAME: revert.main,
    c.STATUS_COMMAND_NAME: status.main,
    c.SWITCH_COMMAND_NAME: switch.main,
}


def create_argument_parser(c: SCCSConstants) -> argparse.ArgumentParser:
    """
    Creates and returns a ArgumentParser object to parse SCCS commands and arguments.
    """

    parser = argparse.ArgumentParser(
        prog=c.LOCAL_SCCS,
        description=c.LOCAL_SCCS_DESCRIPTION,
    )

    parser.add_argument(
        c.DEBUG_FLAG_SHORT,
        c.DEBUG_FLAG,
        action=c.STORE_TRUE_ACTION,
        help=c.FLAG_DESCRIPTIONS[c.DEBUG_FLAG_GENERAL],
    )

    command_parser = parser.add_subparsers(dest=c.COMMAND_FIELD_NAME)

    branch_parser = command_parser.add_parser(
        c.BRANCH_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.BRANCH_COMMAND_NAME]
    )

    branch_subcommand_parser = branch_parser.add_subparsers(
        dest=c.SUBCOMMAND_FIELD_NAME, required=True
    )

    branch_create_parser = branch_subcommand_parser.add_parser(
        c.CREATE_SUBCOMMAND, help=c.BRANCH_CREATE_SUBCOMMAND_HELP
    )

    branch_create_parser.add_argument(
        c.BRANCH_NAME_ARGUMENT_NAME, help=c.BRANCH_CREATE_ARGUMENT_HELP, required=True
    )

    branch_delete_parser = branch_subcommand_parser.add_parser(
        c.DELETE_SUBCOMMAND, help=c.BRANCH_DELETE_SUBCOMMAND_HELP
    )

    branch_delete_parser.add_argument(
        c.BRANCH_NAME_ARGUMENT_NAME, help=c.BRANCH_DELETE_ARGUMENT_HELP, required=True
    )

    branch_subcommand_parser.add_parser(
        c.LIST_SUBCOMMAND, help=c.BRANCH_LIST_SUBCOMMAND_HELP
    )

    clone_parser = command_parser.add_parser(
        c.CLONE_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.CLONE_COMMAND_NAME]
    )

    clone_parser.add_argument(
        c.URL_ARGUMENT_NAME, help=c.URL_ARGUMENT_HELP, required=True
    )

    commit_parser = command_parser.add_parser(
        c.COMMIT_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.COMMIT_COMMAND_NAME]
    )

    commit_parser.add_argument(
        c.COMMIT_MESSAGE_ARGUMENT_NAME,
        help=c.COMMIT_MESSAGE_ARGUMENT_HELP,
        required=True
    )

    config_parser = command_parser.add_parser(
        c.CONFIG_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.CONFIG_COMMAND_NAME]
    )

    config_parser.add_argument(
        c.CONFIG_KEY_ARGUMENT_NAME,
        help=c.CONFIG_KEY_ARGUMENT_HELP_TEMPLATE.format(
            keys=", ".join(c.ACCEPTED_CONFIG_KEYS)
        ),
        required=True
    )

    config_parser.add_argument(
        c.CONFIG_VALUE_ARGUMENT_NAME,
        help=c.CONFIG_VALUE_ARGUMENT_HELP,required=True
    )

    diff_parser = command_parser.add_parser(
        c.DIFF_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.DIFF_COMMAND_NAME]
    )

    diff_parser.add_argument(
        c.COMMIT_IDENTIFIER_ARGUMENT_NAME,
        help=c.COMMIT_IDENTIFIER_DIFF_ARGUMENT_HELP,required=True
    )

    command_parser.add_parser(
        c.HELP_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.HELP_COMMAND_NAME]
    )

    init_parser = command_parser.add_parser(
        c.INIT_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.INIT_COMMAND_NAME]
    )

    init_parser.add_argument(
        c.DOCUMENT_PATH_ARGUMENT_NAME,
        help=c.DOCUMENT_PATH_ARGUMENT_HELP,
        required=True
    )

    command_parser.add_parser(
        c.LOG_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.LOG_COMMAND_NAME]
    )

    merge_parser = command_parser.add_parser(
        c.MERGE_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.MERGE_COMMAND_NAME]
    )

    merge_parser.add_argument(
        c.BRANCH_NAME_ARGUMENT_NAME, help=c.BRANCH_MERGE_ARGUMENT_HELP, required=True
    )

    open_parser = command_parser.add_parser(
        c.OPEN_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.OPEN_COMMAND_NAME]
    )

    open_parser.add_argument(
        c.COMMIT_IDENTIFIER_ARGUMENT_NAME, help=c.COMMIT_IDENTIFIER_OPEN_ARGUMENT_HELP, required=True
    )

    command_parser.add_parser(
        c.PUBLISH_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.PUBLISH_COMMAND_NAME]
    )

    command_parser.add_parser(
        c.PULL_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.PULL_COMMAND_NAME]
    )

    command_parser.add_parser(
        c.PUSH_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.PUSH_COMMAND_NAME]
    )

    command_parser.add_parser(
        c.RESET_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.RESET_COMMAND_NAME]
    )

    revert_parser = command_parser.add_parser(
        c.REVERT_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.REVERT_COMMAND_NAME]
    )

    revert_parser.add_argument(
        c.COMMIT_IDENTIFIER_ARGUMENT_NAME,
        help=c.COMMIT_IDENTIFIER_REVERT_ARGUMENT_HELP,
        required=True
    )

    command_parser.add_parser(
        c.STATUS_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.STATUS_COMMAND_NAME]
    )

    switch_parser = command_parser.add_parser(
        c.SWITCH_COMMAND_NAME, help=c.COMMAND_DESCRIPTIONS[c.SWITCH_COMMAND_NAME]
    )

    switch_parser.add_argument(
        c.BRANCH_NAME_ARGUMENT_NAME, help=c.BRANCH_SWITCH_ARGUMENT_HELP, required=True
    )

    return parser


def run_command(arguments: argparse.Namespace) -> None:
    """
    Run the specified SCCS command by using an ArgumentParser object and reading what
    command was called.

    If and invalid command is provided, inform the user and run SCCS help.
    """

    if arguments.command not in COMMANDS:
        c = SCCSConstants()
        print(
            c.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=arguments.command)
        )
        help.main(c)
        return

    c = SCCSConstants()
    error_wrappers = ErrorWrappers()
    wd = utils.working_directory(c)
    target = TargetBranch(c)
    wd_repository_name = wd.name

    wd_rd = RepositoryData(wd, wd_repository_name, c, target)
    wd_rp = RepositoryPaths(wd, wd_repository_name, c, target)
    wd_rs = RepositoryStatus(wd, wd_repository_name, c, target)
    wd_rw = RepositoryWrite(wd, wd_repository_name, c, target)

    cwd_ri = RepositoryIO(Path.cwd(), wd_repository_name, c, target)
    cwd_rp = RepositoryPaths(Path.cwd(), wd_repository_name, c, target)
    cwd_rs = RepositoryStatus(Path.cwd(), wd_repository_name, c, target)
    cwd_rw = RepositoryWrite(Path.cwd(), wd_repository_name, c, target)

    COMMAND_ARGUMENTS = {
        c.BRANCH_COMMAND_NAME: lambda: [
            c,
            arguments.subcommand,
            arguments.branch_name,
            wd_rd,
            wd_rp,
            wd_rs,
            wd_rw,
        ],
        c.CLONE_COMMAND_NAME: lambda: [c, arguments.url],
        c.COMMIT_COMMAND_NAME: lambda: [
            c,
            arguments.commit_message,
            wd_rd,
            cwd_rs,
            cwd_rw,
        ],
        c.CONFIG_COMMAND_NAME: lambda: [
            c,
            arguments.key,
            arguments.value,
            wd_rd,
            cwd_ri,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.DIFF_COMMAND_NAME: lambda: [
            c,
            arguments.commit_identifier,
            wd_rd,
            cwd_ri,
            cwd_rs,
        ],
        c.HELP_COMMAND_NAME: lambda: [
            c,
        ],
        c.INIT_COMMAND_NAME: lambda: [
            c,
            document_path := Path(arguments.document_path),
            RepositoryIO(
                repository_root := document_path.with_suffix(c.EMPTY_STRING),
                root_repository_name := repository_root.name,
                c,
                target,
            ),
            RepositoryPaths(repository_root, root_repository_name, c, target),
            RepositoryStatus(repository_root, root_repository_name, c, target),
            RepositoryWrite(repository_root, root_repository_name, c, target),
        ],
        c.LOG_COMMAND_NAME: lambda: [
            c,
            wd_rd,
            cwd_ri,
            cwd_rs,
        ],
        c.MERGE_COMMAND_NAME: lambda: [
            c,
            arguments.branch_name,
            wd_rd,
            cwd_ri,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.OPEN_COMMAND_NAME: lambda: [
            c,
            arguments.commit_identifier,
            wd_rd,
            cwd_rs,
        ],
        c.PUBLISH_COMMAND_NAME: lambda: [
            c,
            wd_rd,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.PULL_COMMAND_NAME: lambda: [
            c,
            wd_rd,
            cwd_rp,
            cwd_rs,
        ],
        c.PUSH_COMMAND_NAME: lambda: [
            c,
            wd_rd,
            cwd_ri,
            cwd_rp,
            cwd_rs,
        ],
        c.RESET_COMMAND_NAME: lambda: [
            c,
            wd_rd,
            cwd_rp,
            cwd_rs,
        ],
        c.REVERT_COMMAND_NAME: lambda: [
            c,
            arguments.commit_identifier,
            wd_rd,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
        c.STATUS_COMMAND_NAME: lambda: [
            c,
            wd_rd,
            cwd_rs,
        ],
        c.SWITCH_COMMAND_NAME: lambda: [
            c,
            arguments.branch_name,
            wd_rd,
            cwd_rp,
            cwd_rs,
            cwd_rw,
        ],
    }

    if not arguments.debug:
        try:
            COMMANDS[arguments.command](*COMMAND_ARGUMENTS[arguments.command]())
        except exceptions.SCCSException as e:
            print(error_wrappers.EXPECTED_ERROR_TEMPLATE.format(e=e))
            sys.exit(c.EXPECTED_ERROR_EXIT_CODE)

        except Exception as e:
            print(
                error_wrappers.UNEXPECTED_ERROR_TEMPLATE.format(
                    type_name=type(e).__name__, e=e
                )
            )
            sys.exit(c.UNEXPECTED_ERROR_EXIT_CODE)

    else:
        COMMANDS[arguments.command](*COMMAND_ARGUMENTS[arguments.command]())


def main() -> None:
    """
    Run the specified SCCS command by reading and parsing the entered arguments.

    If no arguments are provided, run SCCS help.
    """

    c = SCCSConstants()

    if len(sys.argv) < c.MINIMUM_ARGUMENTS:
        help.main(c)
        return

    command = utils.entered_argument(c, 1)

    if command not in COMMANDS:
        print(c.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=command))
        help.main(c)
        return

    arguments = create_argument_parser(c).parse_args()

    run_command(arguments)
