#!/usr/bin/env python3
"""Tests for SCCS exception messages."""

import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commands"))

import exceptions


class SCCSExceptionTests(unittest.TestCase):
    """Regression coverage for user-facing SCCS exception messages."""

    def test_sccs_exceptions_have_default_messages(self) -> None:
        """Custom SCCS exceptions should not render as blank messages."""

        for _, exception_cls in inspect.getmembers(exceptions, inspect.isclass):
            if not issubclass(exception_cls, exceptions.SCCSException):
                continue
            with self.subTest(exception_cls=exception_cls.__name__):
                self.assertTrue(str(exception_cls()))

    def test_explicit_message_is_preserved(self) -> None:
        """Call-site-specific messages should still override class defaults."""

        self.assertEqual(
            str(exceptions.FileOpenError("Could not read config.json.")),
            "Could not read config.json.",
        )


if __name__ == "__main__":
    unittest.main()
