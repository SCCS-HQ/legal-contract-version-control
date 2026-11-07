import argparse
import sys
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest
from remote_sccs import help, serve
from remote_sccs import remote_sccs_entrypoint as remote_sccs
from remote_sccs.constants_classes import RemoteSCCSConstants
from test_constants import SCCSTestConstants


def test_remote_sccs_COMMANDS_does_not_drift(rc: RemoteSCCSConstants) -> None:
    assert remote_sccs.COMMANDS == {
        rc.SERVE_COMMAND_NAME: serve.main,
        rc.HELP_COMMAND_NAME: help.main,
    }


def test_create_argument_parser(rc: RemoteSCCSConstants, tc: SCCSTestConstants) -> None:
    parser = argparse.ArgumentParser(
        prog=tc.REMOTE_SCCS,
        description=tc.REMOTE_SCCS_DESCRIPTION,
    )

    parser.add_argument(tc.COMMAND_FIELD_NAME)

    assert repr(remote_sccs.create_argument_parser(rc)) == repr(parser)


def test_run_command_prints_error_and_help_message_if_command_does_not_exist(
    tc: SCCSTestConstants, capsys: pytest.CaptureFixture
) -> None:

    arguments = SimpleNamespace(command=tc.TEST_STRING)

    remote_sccs.run_command(arguments)  # pyright: ignore[reportArgumentType]
    assert capsys.readouterr().out.strip() == (
        tc.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=arguments.command)
        + tc.NEWLINE
        + tc.NEWLINE.join(tc.HELP_MESSAGES)
    )


@pytest.mark.parametrize(
    "command",
    [
        "serve",
        "help",
    ],
)
def test_run_command_prints_unexpected_error_message_if_command_raises_exception(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    command: str,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    e = Exception(tc.TEST_STRING)

    monkeypatch.setattr(
        remote_sccs, "COMMANDS", {**remote_sccs.COMMANDS, command: MagicMock(side_effect=e)}
    )

    with pytest.raises(SystemExit) as exc_info:
        remote_sccs.run_command(
            CustomSimpleNamespace(command=command)  # pyright: ignore[reportArgumentType]
        )

    assert exc_info.value.code == tc.UNEXPECTED_ERROR_EXIT_CODE

    assert capsys.readouterr().out.strip() == tc.UNEXPECTED_ERROR_TEMPLATE.format(
        e=e, type_name=type(e).__name__
    )


@pytest.mark.parametrize(
    "command",
    [
        "serve",
        "help",
    ],
)
def test_run_command_calls_specified_remote_sccs_module_main(
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    tc: SCCSTestConstants,
    CustomSimpleNamespace: Callable[..., Any],
) -> None:

    calls = 0

    def increment_calls(*args: Any, **kwargs: Any) -> None:
        nonlocal calls
        calls += 1

    monkeypatch.setattr(
        remote_sccs, "COMMANDS", {**remote_sccs.COMMANDS, command: increment_calls}
    )

    remote_sccs.run_command(
        CustomSimpleNamespace(command=command)  # pyright: ignore[reportArgumentType]
    )

    assert calls == 1


def test_remote_sccs_main_prints_unknown_command_error_message_and_help_message_if_command_does_not_exist(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    tc: SCCSTestConstants,
) -> None:

    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, tc.TEST_STRING])

    remote_sccs.main()

    assert (
        capsys.readouterr().out.strip()
        == tc.UNKNOWN_COMMAND_ERROR_MESSAGE_TEMPLATE.format(command=tc.TEST_STRING)
        + tc.NEWLINE
        + tc.NEWLINE.join(tc.HELP_MESSAGES)
    )


@pytest.mark.parametrize(
    "command",
    [
        "serve",
        "help",
    ],
)
def test_remote_sccs_main_prints_unexpected_error_message_if_command_raises_exception(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    command: str,
) -> None:

    e = Exception(tc.TEST_STRING)

    monkeypatch.setattr(
        remote_sccs, "COMMANDS", {**remote_sccs.COMMANDS, command: MagicMock(side_effect=e)}
    )
    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, command])
    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda *args, **kwargs: SimpleNamespace(command=command),
    )

    with pytest.raises(SystemExit) as exc_info:
        remote_sccs.main()

    assert exc_info.value.code == tc.UNEXPECTED_ERROR_EXIT_CODE

    assert capsys.readouterr().out.strip() == tc.UNEXPECTED_ERROR_TEMPLATE.format(
        e=e, type_name=type(e).__name__
    )


@pytest.mark.parametrize(
    "command",
    [
        "serve",
        "help",
    ],
)
def test_remote_sccs_main_calls_specified_remote_sccs_module_main(
    monkeypatch: pytest.MonkeyPatch,
    command: str,
    tc: SCCSTestConstants,
) -> None:

    calls = 0

    def increment_calls(*args: Any, **kwargs: Any) -> None:
        nonlocal calls
        calls += 1

    monkeypatch.setattr(
        remote_sccs, "COMMANDS", {**remote_sccs.COMMANDS, command: increment_calls}
    )
    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING, command])
    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda *args, **kwargs: SimpleNamespace(command=command),
    )

    remote_sccs.main()

    assert calls == 1


def test_remote_sccs_main_prints_help_message_if_length_of_argv_is_less_than_two(
    tc: SCCSTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:

    monkeypatch.setattr(sys, "argv", [tc.TEST_STRING])
    remote_sccs.main()
    assert capsys.readouterr().out.strip() == tc.NEWLINE.join(tc.HELP_MESSAGES)
