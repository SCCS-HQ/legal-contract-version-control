from local_sccs.constants_classes import SCCSConstants
from local_sccs import help
import pytest
from test_constants import SCCSTestConstants

def test_print_help_prints_help_message(capsys: pytest.CaptureFixture[str], c: SCCSConstants, tc: SCCSTestConstants) -> None:
    """
    Test the print_help function to ensure it prints the correct help messages.
    """

    help.print_help(c)
    expected_output = tc.NEWLINE.join(tc.HELP_MESSAGES) + tc.NEWLINE
    assert capsys.readouterr().out == expected_output


def test_help_main_prints_help_message(capsys: pytest.CaptureFixture[str], c: SCCSConstants, tc: SCCSTestConstants) -> None:
    """
    Test the main function to ensure it calls print_help and prints the correct help messages.
    """

    help.main(c)
    expected_output = tc.NEWLINE.join(tc.HELP_MESSAGES) + tc.NEWLINE
    assert capsys.readouterr().out == expected_output