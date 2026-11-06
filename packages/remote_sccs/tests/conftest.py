import pytest
from remote_sccs.constants_classes import RemoteSCCSConstants
from test_constants import SCCSTestConstants
from typing import Any
from types import FunctionType


@pytest.fixture()
def rc() -> RemoteSCCSConstants:

    return RemoteSCCSConstants()


@pytest.fixture()
def tc() -> SCCSTestConstants:

    return SCCSTestConstants()


@pytest.fixture()
def raise_exception() -> FunctionType:
    """
    Return a callable that raises an exception when called.
    """

    def _raise_exception(*args: Any, **kwargs: Any) -> None:
        raise OSError

    return _raise_exception
