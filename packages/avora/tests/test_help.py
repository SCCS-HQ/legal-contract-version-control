import pytest
from avora import help
from avora.constants_classes import AvoraConstants
from test_constants import AvoraTestConstants


def test_print_help_prints_help_message(
    c: AvoraConstants, tc: AvoraTestConstants, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test the print_help function to ensure it prints the correct help messages.
    """

    help.print_help(c)
    expected_output = tc.NEWLINE.join(tc.HELP_MESSAGES)
    assert capsys.readouterr().out.strip() == expected_output


def test_help_main_prints_help_message(
    c: AvoraConstants, tc: AvoraTestConstants, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test the main function to ensure it calls print_help and prints the
    correct help messages.
    """

    help.main(c)
    expected_output = tc.NEWLINE.join(tc.HELP_MESSAGES)
    assert capsys.readouterr().out.strip() == expected_output