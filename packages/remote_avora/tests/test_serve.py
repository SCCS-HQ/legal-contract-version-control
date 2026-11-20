"""Tests for ``remote_avora.serve``."""

import socket
from pathlib import Path
from types import FunctionType
from typing import Any
from unittest import mock

import pytest
import uvicorn
from remote_avora import serve
from remote_avora.constants_classes import RemoteAvoraConstants
from remote_avora.exceptions import RemoteAvoraException
from test_constants import AvoraTestConstants


def test_create_repositories_directory_creates_directory(
    rc: RemoteAvoraConstants,
    tc: AvoraTestConstants,
) -> None:
    """Verify ``create_repositories_directory`` creates the ``./repos`` directory."""

    serve.create_repositories_directory(rc)
    assert Path(tc.REPOSITORIES_BASE_DIRECTORY).exists()


def test_create_repositories_directory_raises_if_directory_creation_fails(
    rc: RemoteAvoraConstants,
    tc: AvoraTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    """Verify ``create_repositories_directory`` raises on mkdir failure."""

    monkeypatch.setattr(Path, "mkdir", raise_exception)

    with pytest.raises(RemoteAvoraException) as e:
        serve.create_repositories_directory(rc)

        assert str(e.value) == tc.REPOSITORIES_DIRECTORY_CREATION_ERROR_MESSAGE


def test_print_avora_server_startup_prints_startup_messages(
    rc: RemoteAvoraConstants,
    tc: AvoraTestConstants,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify ``print_avora_server_startup`` prints the expected startup messages."""

    monkeypatch.setattr(
        socket.socket,
        "getsockname",
        lambda *args, **kwargs: (tc.DEFAULT_IP_ADDRESS, tc.DEFAULT_PORT),
    )

    serve.print_avora_server_startup(rc)

    assert capsys.readouterr().out.strip() == (
        tc.IP_ADDRESS_RETRIEVAL_SUCCESS_MESSAGE_TEMPLATE.format(
            ip_address=tc.DEFAULT_IP_ADDRESS
        )
        + tc.NEWLINE
        + tc.STARTING_UVICORN_SERVER_MESSAGE
    )


def test_print_avora_server_startup_raises_if_ip_retrieval_fails(
    rc: RemoteAvoraConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    tc: AvoraTestConstants,
) -> None:
    """Verify ``print_avora_server_startup`` raises when IP retrieval fails."""

    monkeypatch.setattr(socket.socket, "getsockname", raise_exception)

    with pytest.raises(RemoteAvoraException) as e:
        serve.print_avora_server_startup(rc)

        assert str(e.value) == tc.IP_ADDRESS_RETRIEVAL_ERROR_MESSAGE


def test_serve_main_creates_repositories_directory(
    rc: RemoteAvoraConstants,
    tc: AvoraTestConstants,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify ``serve.main`` creates the repositories directory."""

    monkeypatch.setattr(
        socket.socket,
        "getsockname",
        lambda *args, **kwargs: (tc.DEFAULT_IP_ADDRESS, tc.DEFAULT_PORT),
    )
    monkeypatch.setattr(uvicorn, "run", mock.MagicMock())

    serve.main(rc)

    assert Path(tc.REPOSITORIES_BASE_DIRECTORY).exists()


def test_serve_main_raises_if_repositories_directory_creation_fails(
    rc: RemoteAvoraConstants,
    tc: AvoraTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
) -> None:
    """Verify ``serve.main`` raises when directory creation fails."""

    monkeypatch.setattr(uvicorn, "run", mock.MagicMock())
    monkeypatch.setattr(Path, "mkdir", raise_exception)

    with pytest.raises(RemoteAvoraException):
        serve.main(rc)


def test_serve_main_prints_startup_messages(
    rc: RemoteAvoraConstants,
    tc: AvoraTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """Verify ``serve.main`` prints the expected startup messages."""

    monkeypatch.setattr(uvicorn, "run", mock.MagicMock())
    monkeypatch.setattr(
        socket.socket,
        "getsockname",
        lambda *args, **kwargs: (tc.DEFAULT_IP_ADDRESS, tc.DEFAULT_PORT),
    )

    serve.main(rc)

    assert capsys.readouterr().out.strip() == (
        tc.IP_ADDRESS_RETRIEVAL_SUCCESS_MESSAGE_TEMPLATE.format(
            ip_address=tc.DEFAULT_IP_ADDRESS
        )
        + tc.NEWLINE
        + tc.STARTING_UVICORN_SERVER_MESSAGE
    )


def test_serve_main_raises_if_ip_retrieval_fails(
    rc: RemoteAvoraConstants,
    monkeypatch: pytest.MonkeyPatch,
    raise_exception: FunctionType,
    tc: AvoraTestConstants,
) -> None:
    """Verify ``serve.main`` raises when IP retrieval fails."""

    monkeypatch.setattr(socket.socket, "getsockname", raise_exception)

    with pytest.raises(RemoteAvoraException) as e:
        serve.main(rc)

        assert str(e.value) == tc.IP_ADDRESS_RETRIEVAL_ERROR_MESSAGE


def test_main_starts_uvicorn_server(
    rc: RemoteAvoraConstants,
    tc: AvoraTestConstants,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """Verify ``serve.main`` starts the uvicorn server exactly once."""

    calls = 0

    def increment_calls(*args: Any, **kwargs: Any) -> None:
        """Increment the call counter each time ``uvicorn.run`` is called."""

        nonlocal calls
        calls += 1

    monkeypatch.setattr(uvicorn, "run", increment_calls)
    monkeypatch.setattr(
        socket.socket,
        "getsockname",
        lambda *args, **kwargs: (tc.DEFAULT_IP_ADDRESS, tc.DEFAULT_PORT),
    )

    serve.main(rc)

    assert calls == 1