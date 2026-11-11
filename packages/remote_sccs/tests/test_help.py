import pytest
from remote_sccs import help
from remote_sccs.constants_classes import RemoteSCCSConstants
from test_constants import SCCSTestConstants


def test_print_help_prints_help_messages(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants, capsys: pytest.CaptureFixture[str]
) -> None:

    help.print_help(rc)

    assert capsys.readouterr().out.strip() == tc.NEWLINE.join(tc.HELP_MESSAGES)


def test_help_main_prints_help_messages(
    tc: SCCSTestConstants, rc: RemoteSCCSConstants, capsys: pytest.CaptureFixture[str]
) -> None:

    help.main(rc)

    assert capsys.readouterr().out.strip() == tc.NEWLINE.join(tc.HELP_MESSAGES)
