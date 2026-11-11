from types import FunctionType, SimpleNamespace
from typing import Any

import pytest
from remote_sccs.constants_classes import RemoteSCCSConstants
from test_constants import SCCSTestConstants


@pytest.fixture()
def rc() -> RemoteSCCSConstants:
    """Return a ``RemoteSCCSConstants`` instance for use in tests."""

    return RemoteSCCSConstants()


@pytest.fixture()
def tc() -> SCCSTestConstants:
    """Return an ``SCCSTestConstants`` instance for use in tests."""

    return SCCSTestConstants()


@pytest.fixture()
def CustomSimpleNamespace(tc: SCCSTestConstants) -> Any:
    """
    Return a custom SimpleNamespace class that returns None for missing attributes.
    """

    class _CustomSimpleNamespace(SimpleNamespace):
        """A SimpleNamespace subclass that returns ``None`` for missing attributes."""

        def __getattr__(self, name: str) -> Any:
            """Return ``None`` for any missing attribute access."""

            return None

    return _CustomSimpleNamespace


@pytest.fixture()
def raise_exception() -> FunctionType:
    """
    Return a callable that raises an exception when called.
    """

    def _raise_exception(*args: Any, **kwargs: Any) -> None:
        """Raise ``OSError`` when called."""

        raise OSError

    return _raise_exception
