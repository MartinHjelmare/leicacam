"""Tests for async cam module."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from leicacam.async_cam import AsyncCAM
from leicacam.cam import bytes_as_dict, tuples_as_dict


class MockEchoConnection:
    """Mock an echo connection."""

    msg = b""

    def write(self, msg):
        """Write a message."""
        self.msg = msg

    async def read(self, buffer_size):
        """Read a message."""
        return self.msg[0:buffer_size]


@pytest.fixture(name="mock_connection")
def mock_connection_fixture():
    """Return an echo connection."""
    return MockEchoConnection()


@pytest.fixture(name="mock_writer")
def mock_writer_fixture(mock_connection):
    """Mock an asyncio connection writer."""
    writer = Mock()
    writer.write = mock_connection.write
    writer.drain = AsyncMock()
    writer.wait_closed = AsyncMock()
    yield writer


@pytest.fixture(name="mock_reader")
def mock_reader_fixture(mock_connection):
    """Mock an asyncio connection reader."""
    reader = Mock()
    reader.read = mock_connection.read
    reader.read_line = AsyncMock()
    reader.readexactly = AsyncMock()
    reader.readuntil = AsyncMock()
    yield reader


@pytest.fixture(name="open_connection_ret")
def open_connection_ret_fixture(mock_reader, mock_writer):
    """Define the side_effect for open_connection."""
    return mock_reader, mock_writer


@pytest.fixture(name="mock_open_connection")
def mock_open_connection_fixture(open_connection_ret):
    """Mock asyncio open_connection."""
    open_connection_patch = patch(
        "leicacam.async_cam.asyncio.open_connection", return_value=open_connection_ret
    )
    with open_connection_patch as mock_open:
        yield mock_open


@pytest.fixture(name="async_cam")
async def async_cam_fixture(mock_open_connection):
    """Yield an AsyncCAM instance with a mock socket."""
    # pylint: disable=unused-argument
    _async_cam = AsyncCAM()
    await _async_cam.connect()
    yield _async_cam


async def test_echo(async_cam):
    """Prefix + command sent should be same as echoed socket message."""
    cmd = [
        ("cli", "custom"),
        ("cmd", "enableall"),
        ("value", "true"),
        ("integer", 5678),
        ("float", 0.00567),
    ]

    await async_cam.send(cmd)
    [response] = await async_cam.receive()

    sent = tuples_as_dict(async_cam.prefix + cmd)

    assert sent == response


async def test_send_bytes(async_cam):
    """Test send a bytes string."""
    cmd = b"/cmd:enableall /value:true"
    await async_cam.send(cmd)
    [response] = await async_cam.receive()

    sent = bytes_as_dict(async_cam.prefix_bytes + cmd)

    assert sent == response


async def test_receive_error(async_cam, mock_reader):
    """Test receive method when a socket error happens."""
    mock_reader.read = Mock()
    mock_reader.read.side_effect = OSError()
    response = await async_cam.receive()

    assert isinstance(response, list)
    assert not response


async def test_close(async_cam, mock_writer):
    """Test writer close."""
    async_cam.close()
    assert mock_writer.close.call_count == 1
