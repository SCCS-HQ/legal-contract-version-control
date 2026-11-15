"""Tests for ``remote_avora.help``."""

import pytest
from remote_avora import help
from remote_avora.constants_classes import RemoteAvoraConstants
from test_constants import AvoraTestConstants


def test_print_help_prints_help_messages(
    tc: AvoraTestConstants,
    rc: RemoteAvoraConstants,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify ``print_help`` prints the joined help messages."""

    help.print_help(rc)

    assert capsys.readouterr().out.strip() == tc.NEWLINE.join(tc.HELP_MESSAGES)


def test_help_main_prints_help_messages(
    tc: AvoraTestConstants,
    rc: RemoteAvoraConstants,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify ``help.main`` prints the joined help messages."""

    help.main(rc)

    assert capsys.readouterr().out.strip() == tc.NEWLINE.join(tc.HELP_MESSAGES)
