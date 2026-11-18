import argparse
import inspect
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest
from local_sccs import (
    branch,
    clone,
    commit,
    config,
    diff,
    help,
    init,
    log,
    merge,
    open,
    publish,
    pull,
    push,
    reset,
    revert,
    sccs_entrypoint,
    status,
    switch,
    utils,
)
from local_sccs.constants_classes import SCCSConstants
from local_sccs.exceptions import SCCSException
from local_sccs.repository_layout import (
    RepositoryData,
    RepositoryIO,
    RepositoryPaths,
    RepositoryStatus,
    RepositoryWrite,
    TargetBranch,
)
from test_constants import SCCSTestConstants


def test_sccs_COMMANDS_does_not_drift(tc: SCCSTestConstants) -> None:
    assert sccs_entrypoint.COMMANDS == {
        tc.BRANCH_COMMAND_NAME: branch.main,
        tc.CLONE_COMMAND_NAME: clone.main,
        tc.COMMIT_COMMAND_NAME: commit.main,
        tc.CONFIG_COMMAND_NAME: config.main,
        tc.DIFF_COMMAND_NAME: diff.main,
        tc.HELP_COMMAND_NAME: help.main,
        tc.INIT_COMMAND_NAME: init.main,
        tc.LOG_COMMAND_NAME: log.main,
        tc.MERGE_COMMAND_NAME: merge.main,
        tc.OPEN_COMMAND_NAME: open.main,
        tc.PUBLISH_COMMAND_NAME: publish.main,
        tc.PULL_COMMAND_NAME: pull.main,
        tc.PUSH_COMMAND_NAME: push.main,
        tc.RESET_COMMAND_NAME: reset.main,
        tc.REVERT_COMMAND_NAME: revert.main,
        tc.STATUS_COMMAND_NAME: status.main,
        tc.SWITCH_COMMAND_NAME: switch.main,
    }


def test_create_argument_parser(c: SCCSConstants, tc: SCCSTestConstants) -> None:
    parser = argparse.ArgumentParser(
        prog=tc.LOCAL_SCCS,
        description=tc.LOCAL_SCCS_DESCRIPTION,
    )

    parser.add_argument(
        tc.DEBUG_FLAG_SHORT,
        tc.DEBUG_FLAG,
        action=tc.STORE_TRUE_ACTION,
        help=tc.FLAG_DESCRIPTIONS[tc.DEBUG_FLAG_GENERAL],
    )

    command_parser = parser.add_subparsers(dest=tc.COMMAND_FIELD_NAME)

    branch_parser = command_parser.add_parser(
        tc.BRANCH_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.BRANCH_COMMAND_NAME]
    )

    branch_subcommand_parser = branch_parser.add_subparsers(
        dest=tc.SUBCOMMAND_FIELD_NAME, required=True
    )

    branch_create_parser = branch_subcommand_parser.add_parser(
        tc.CREATE_SUBCOMMAND, help=tc.BRANCH_CREATE_SUBCOMMAND_HELP
    )

    branch_create_parser.add_argument(
        tc.BRANCH_NAME_ARGUMENT_NAME, help=tc.BRANCH_CREATE_ARGUMENT_HELP
    )

    branch_delete_parser = branch_subcommand_parser.add_parser(
        tc.DELETE_SUBCOMMAND, help=tc.BRANCH_DELETE_SUBCOMMAND_HELP
    )

    branch_delete_parser.add_argument(
        tc.BRANCH_NAME_ARGUMENT_NAME, help=tc.BRANCH_DELETE_ARGUMENT_HELP
    )

    branch_subcommand_parser.add_parser(
        tc.LIST_SUBCOMMAND, help=tc.BRANCH_LIST_SUBCOMMAND_HELP
    )

    clone_parser = command_parser.add_parser(
        tc.CLONE_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.CLONE_COMMAND_NAME]
    )

    clone_parser.add_argument(tc.URL_ARGUMENT_NAME, help=tc.URL_ARGUMENT_HELP)

    commit_parser = command_parser.add_parser(
        tc.COMMIT_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.COMMIT_COMMAND_NAME]
    )

    commit_parser.add_argument(
        tc.COMMIT_MESSAGE_ARGUMENT_NAME,
        help=tc.COMMIT_MESSAGE_ARGUMENT_HELP,
    )

    config_parser = command_parser.add_parser(
        tc.CONFIG_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.CONFIG_COMMAND_NAME]
    )

    config_parser.add_argument(
        tc.CONFIG_KEY_ARGUMENT_NAME,
        help=tc.CONFIG_KEY_ARGUMENT_HELP_TEMPLATE.format(
            keys=tc.COMMA_SPACE.join(tc.ACCEPTED_CONFIG_KEYS)
        ),
    )

    config_parser.add_argument(
        tc.CONFIG_VALUE_ARGUMENT_NAME, help=tc.CONFIG_VALUE_ARGUMENT_HELP
    )

    diff_parser = command_parser.add_parser(
        tc.DIFF_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.DIFF_COMMAND_NAME]
    )

    diff_parser.add_argument(
        tc.COMMIT_IDENTIFIER_ARGUMENT_NAME,
        help=tc.COMMIT_IDENTIFIER_DIFF_ARGUMENT_HELP,
    )

    command_parser.add_parser(
        tc.HELP_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.HELP_COMMAND_NAME]
    )

    init_parser = command_parser.add_parser(
        tc.INIT_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.INIT_COMMAND_NAME]
    )

    init_parser.add_argument(
        tc.DOCUMENT_PATH_ARGUMENT_NAME, help=tc.DOCUMENT_PATH_ARGUMENT_HELP
    )

    command_parser.add_parser(
        tc.LOG_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.LOG_COMMAND_NAME]
    )

    merge_parser = command_parser.add_parser(
        tc.MERGE_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.MERGE_COMMAND_NAME]
    )

    merge_parser.add_argument(
        tc.BRANCH_NAME_ARGUMENT_NAME, help=tc.BRANCH_MERGE_ARGUMENT_HELP
    )

    open_parser = command_parser.add_parser(
        tc.OPEN_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.OPEN_COMMAND_NAME]
    )

    open_parser.add_argument(
        tc.COMMIT_IDENTIFIER_ARGUMENT_NAME,
        help=tc.COMMIT_IDENTIFIER_OPEN_ARGUMENT_HELP,
    )

    command_parser.add_parser(
        tc.PUBLISH_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.PUBLISH_COMMAND_NAME]
    )

    command_parser.add_parser(
        tc.PULL_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.PULL_COMMAND_NAME]
    )

    command_parser.add_parser(
        tc.PUSH_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.PUSH_COMMAND_NAME]
    )

    command_parser.add_parser(
        tc.RESET_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.RESET_COMMAND_NAME]
    )

    revert_parser = command_parser.add_parser(
        tc.REVERT_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.REVERT_COMMAND_NAME]
    )

    revert_parser.add_argument(
        tc.COMMIT_IDENTIFIER_ARGUMENT_NAME,
        help=tc.COMMIT_IDENTIFIER_REVERT_ARGUMENT_HELP,
    )

    command_parser.add_parser(
        tc.STATUS_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.STATUS_COMMAND_NAME]
    )

    switch_parser = command_parser.add_parser(
        tc.SWITCH_COMMAND_NAME, help=tc.COMMAND_DESCRIPTIONS[tc.SWITCH_COMMAND_NAME]
    )

    switch_parser.add_argument(
        tc.BRANCH_NAME_ARGUMENT_NAME, help=tc.BRANCH_SWITCH_ARGUMENT_HELP
    )

    assert repr(sccs_entrypoint.create_argument_parser(c)) == repr(parser)


def test_run_command_prints_error_and_help_message_if_command_does_not_exist(
    tc: SCCSTestConstants, capsys: pytest.CaptureFixture
) -> None:

    arguments = SimpleNamespace(command=tc.TEST_STRING, debug=False)

    sccs_entrypoint.run_command(arguments)  # pyright: ignore[reportArgumentType]
    assert capsys.readouterr().out.strip() == (
        tc.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=arguments.command)
        + tc.NEWLINE
        + (tc.NEWLINE).join(tc.HELP_MESSAGES)
    )


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_run_command_prints_expected_error_message_if_command_raises_sccs_exception_if_debug_is_false(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    command: str,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    e = SCCSException(tc.TEST_STRING)

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: MagicMock(side_effect=e)},
    )

    with pytest.raises(SystemExit) as exc_info:
        sccs_entrypoint.run_command(
            CustomSimpleNamespace(command=command, debug=False)
        )  # pyright: ignore[reportArgumentType]

        assert exc_info.value.code == tc.EXPECTED_ERROR_EXIT_CODE

    assert capsys.readouterr().out.strip() == tc.EXPECTED_ERROR_TEMPLATE.format(e=e)


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_run_command_prints_unexpected_error_message_if_command_raises_unexpected_exception_if_debug_is_false(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    command: str,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    e = Exception(tc.TEST_STRING)

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: MagicMock(side_effect=e)},
    )

    with pytest.raises(SystemExit) as exc_info:
        sccs_entrypoint.run_command(
            CustomSimpleNamespace(command=command, debug=False)
        )  # pyright: ignore[reportArgumentType]

        assert exc_info.value.code == tc.UNEXPECTED_ERROR_EXIT_CODE

    assert capsys.readouterr().out.strip() == tc.UNEXPECTED_ERROR_TEMPLATE.format(
        e=e, type_name=type(e).__name__
    )


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_run_command_does_not_except_exceptions_if_debug_is_true(
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    tc: SCCSTestConstants,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    e = Exception(tc.TEST_STRING)

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: MagicMock(side_effect=e)},
    )

    with pytest.raises(Exception) as exc_info:
        sccs_entrypoint.run_command(
            CustomSimpleNamespace(command=command, debug=True)
        )  # pyright: ignore[reportArgumentType]

        assert exc_info.value == e


def test_COMMAND_ARGUMENTS_does_not_drift(
    tc: SCCSTestConstants,
    CustomSimpleNamespace: Callable[..., Any],
    c: SCCSConstants,
    target: TargetBranch,
) -> None:

    wd = utils.working_directory(c)
    wd_repository_name = wd.name

    wd_rd = RepositoryData(wd, wd_repository_name, c, target)
    wd_rp = RepositoryPaths(wd, wd_repository_name, c)
    wd_rs = RepositoryStatus(wd, wd_repository_name, c, target)
    wd_rw = RepositoryWrite(wd, wd_repository_name, c, target)

    cwd_ri = RepositoryIO(utils.working_directory(c), wd_repository_name, c, target)
    cwd_rp = RepositoryPaths(utils.working_directory(c), wd_repository_name, c)
    cwd_rs = RepositoryStatus(utils.working_directory(c), wd_repository_name, c, target)
    cwd_rw = RepositoryWrite(utils.working_directory(c), wd_repository_name, c, target)
    arguments = CustomSimpleNamespace(command=tc.TEST_STRING, debug=False)

    expected_command_arguments = {
        c.BRANCH_COMMAND_NAME: lambda: [
            c,
            arguments.subcommand,
            getattr(arguments, c.BRANCH_NAME_ARGUMENT_NAME, None),
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
            RepositoryPaths(repository_root, root_repository_name, c),
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

    result = sccs_entrypoint.COMMAND_ARGUMENTS(
        CustomSimpleNamespace(command=tc.TEST_STRING, debug=False)
    )

    for command_name, args_factory in result.items():
        args = args_factory()
        inspect.signature(sccs_entrypoint.COMMANDS[command_name]).bind(*args)

    assert set(result) == set(
        expected_command_arguments
    )  # pyright: ignore[reportArgumentType]

    assert [i.__code__.co_code for i in result.values()] == [
        i.__code__.co_code for i in expected_command_arguments.values()
    ]  # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_run_command_calls_specified_local_sccs_module_main(
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    tc: SCCSTestConstants,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    calls = 0

    def increment_calls(*args: Any, **kwargs: Any) -> None:
        inspect.signature(sccs_entrypoint.COMMANDS[command]).bind(*args, **kwargs)
        nonlocal calls
        calls += 1

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: increment_calls},
    )

    sccs_entrypoint.run_command(
        CustomSimpleNamespace(command=command, debug=True)
    )  # pyright: ignore[reportArgumentType]

    assert calls == 1


def test_sccs_main_prints_unknown_command_error_message_and_help_message_if_command_does_not_exist(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    tc: SCCSTestConstants,
) -> None:

    monkeypatch.setattr(
        utils, "entered_argument", lambda *args, **kwargs: tc.TEST_STRING
    )

    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, tc.TEST_STRING])

    sccs_entrypoint.main()

    assert (
        capsys.readouterr().out.strip()
        == tc.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=tc.TEST_STRING)
        + tc.NEWLINE
        + (tc.NEWLINE).join(tc.HELP_MESSAGES)
    )


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_sccs_main_prints_expected_error_message_if_command_raises_sccs_exception_if_debug_is_false(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    command: str,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    e = SCCSException(tc.TEST_STRING)

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: MagicMock(side_effect=e)},
    )
    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, command])
    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda *args, **kwargs: CustomSimpleNamespace(command=command, debug=False),
    )

    with pytest.raises(SystemExit) as exc_info:
        sccs_entrypoint.main()
        assert exc_info.value.code == tc.EXPECTED_ERROR_EXIT_CODE

    assert capsys.readouterr().out.strip() == tc.EXPECTED_ERROR_TEMPLATE.format(e=e)


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_sccs_main_prints_unexpected_error_message_if_command_raises_unexpected_exception_if_debug_is_false(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    command: str,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    e = Exception(tc.TEST_STRING)

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: MagicMock(side_effect=e)},
    )
    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, command])
    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda *args, **kwargs: CustomSimpleNamespace(command=command, debug=False),
    )

    with pytest.raises(SystemExit) as exc_info:
        sccs_entrypoint.main()
        assert exc_info.value.code == tc.UNEXPECTED_ERROR_EXIT_CODE

    assert capsys.readouterr().out.strip() == tc.UNEXPECTED_ERROR_TEMPLATE.format(
        e=e, type_name=type(e).__name__
    )


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_sccs_main_does_not_except_exceptions_if_debug_is_true(
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    tc: SCCSTestConstants,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    e = Exception(tc.TEST_STRING)

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: MagicMock(side_effect=e)},
    )
    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, command])
    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda *args, **kwargs: CustomSimpleNamespace(command=command, debug=True),
    )

    with pytest.raises(Exception) as exc_info:
        sccs_entrypoint.main()  # pyright: ignore[reportArgumentType]

        assert exc_info.value == e


@pytest.mark.parametrize(
    "command",
    [
        "branch",
        "clone",
        "commit",
        "config",
        "diff",
        "help",
        "init",
        "log",
        "merge",
        "open",
        "publish",
        "pull",
        "push",
        "reset",
        "revert",
        "status",
        "switch",
    ],
)
def test_sccs_main_calls_specified_local_sccs_module_main(
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    tc: SCCSTestConstants,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    calls = 0

    def increment_calls(*args: Any, **kwargs: Any) -> None:
        inspect.signature(sccs_entrypoint.COMMANDS[command]).bind(*args, **kwargs)
        nonlocal calls
        calls += 1

    monkeypatch.setattr(
        sccs_entrypoint,
        "COMMANDS",
        {**sccs_entrypoint.COMMANDS, command: increment_calls},
    )
    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, command])
    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda *args, **kwargs: CustomSimpleNamespace(command=command, debug=True),
    )

    sccs_entrypoint.run_command(
        CustomSimpleNamespace(command=command, debug=True)
    )  # pyright: ignore[reportArgumentType]

    assert calls == 1


# fixture for CustomSimpleNamespace


def test_sccs_main_prints_help_message_if_length_of_argv_is_less_than_two(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:

    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING])
    sccs_entrypoint.main()
    assert capsys.readouterr().out.strip() == (tc.NEWLINE).join(tc.HELP_MESSAGES)
