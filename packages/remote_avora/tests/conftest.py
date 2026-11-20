from types import FunctionType, SimpleNamespace
from typing import Any

import pytest
from remote_avora.constants_classes import RemoteAvoraConstants
from test_constants import AvoraTestConstants


@pytest.fixture()
def rc() -> RemoteAvoraConstants:
    """Return a ``RemoteAvoraConstants`` instance for use in tests."""

    return RemoteAvoraConstants()


@pytest.fixture()
def tc() -> AvoraTestConstants:
    """Return an ``AvoraTestConstants`` instance for use in tests."""

    return AvoraTestConstants()


@pytest.fixture()
def CustomSimpleNamespace(tc: AvoraTestConstants) -> Any:
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
