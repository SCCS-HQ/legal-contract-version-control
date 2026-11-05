import pytest
from remote_sccs.constants_classes import RemoteSCCSConstants
from test_constants import SCCSTestConstants


@pytest.fixture()
def rc() -> RemoteSCCSConstants:

    return RemoteSCCSConstants()


@pytest.fixture()
def tc() -> SCCSTestConstants:

    return SCCSTestConstants()
