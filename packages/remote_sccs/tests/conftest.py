import pytest
from remote_sccs.constants_classes import RemoteSCCSConstants
from test_constants import SCCSTestConstants


@pytest.fixture()
def rc() -> RemoteSCCSConstants:
    """
    Return the Remote-SCCS constants.
    """

    return RemoteSCCSConstants()


@pytest.fixture()
def tc() -> SCCSTestConstants:
    """
    Return the SCCS test constants.
    """

    return SCCSTestConstants()
