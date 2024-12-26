"""Tests for cam module."""

import socket
from collections import OrderedDict
from unittest.mock import MagicMock, patch

import pytest

from leicacam.cam import CAM, bytes_as_dict, tuples_as_bytes, tuples_as_dict

# pylint: disable=redefined-outer-name, unnecessary-pass,


def flush():
    """Flush the socket."""
    pass


@pytest.fixture
def mock_socket():
    """Return a mock echo socket."""
    echo_socket = EchoSocket()
    echo_socket.close = MagicMock()
    return echo_socket


@pytest.fixture
def cam(mock_socket):
    """Yield a CAM instance with a mock socket."""
    with patch("socket.socket") as mock_socket_class:
        mock_socket_class.return_value = mock_socket
        mock_cam = CAM()
        mock_cam.flush = flush

        yield mock_cam


class EchoSocket:
    """Dummy echo socket for mocking."""

    msg = ""

    def send(self, msg):
        """Send a message."""
        self.msg = msg
        return len(msg)

    def recv(self, buffer_size):
        """Receive a message."""
        return self.msg[0:buffer_size]

    def connect(self, where):
        """Connect to the socket."""
        pass

    def settimeout(self, timeout):
        """Set a timeout."""
        pass

    def close(self):
        """Close the socket."""
        pass


# TEST
# key (here cli) overridden if defined several times
# prefix added
# types (integer, float) should be converted to strings


def test_echo(cam):
    """Prefix + command sent should be same as echoed socket message."""
    cmd = [
        ("cli", "custom"),
        ("cmd", "enableall"),
        ("value", "true"),
        ("integer", 1234),
        ("float", 0.00234),
    ]

    cam.send(cmd)
    response = cam.receive()[0]

    sent = tuples_as_dict(cam.prefix + cmd)

    assert sent == response


def test_send_bytes(cam):
    """Test send a bytes string."""
    cmd = b"/cmd:enableall /value:true"
    cam.send(cmd)
    response = cam.receive()[0]

    sent = bytes_as_dict(cam.prefix_bytes + cmd)

    assert sent == response


def test_flush():
    """Test flush method."""
    cmd = b"/cmd:startscan\n"
    mock_recv = MagicMock()
    mock_recv.side_effect = [cmd, socket.error()]
    with patch("socket.socket") as mock_socket_class:
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        cam = CAM()
        cam.socket.recv = mock_recv

        cam.flush()

    assert len(mock_recv.mock_calls) == 2
    _, args, _ = mock_recv.mock_calls[0]
    assert args == (1024,)


def test_receive_error(cam):
    """Test receive method when a socket error happens."""
    cam.socket.recv = MagicMock()
    cam.socket.recv.side_effect = socket.error()
    response = cam.receive()

    assert isinstance(response, list)
    assert not response


def test_commands(cam):
    """Short hand commands should work as intended."""
    # get_information
    cmd = cam.prefix + [("cmd", "getinfo"), ("dev", "stage")]

    information = cam.get_information()
    should_be = tuples_as_dict(cmd)

    assert information == should_be

    # start_scan
    cmd = cam.prefix + [("cmd", "startscan")]

    response = cam.start_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # stop_scan
    cmd = cam.prefix + [("cmd", "stopscan")]

    response = cam.stop_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # autofocus_scan
    cmd = cam.prefix + [("cmd", "autofocusscan")]

    response = cam.autofocus_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # pause_scan
    cmd = cam.prefix + [("cmd", "pausescan")]

    response = cam.pause_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # enable
    cmd = [
        ("cmd", "enable"),
        ("slide", str(0)),
        ("wellx", str(1)),
        ("welly", str(1)),
        ("fieldx", str(1)),
        ("fieldy", str(1)),
        ("value", "true"),
    ]
    cmd = cam.prefix + cmd

    response = cam.enable()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # disable
    cmd = [
        ("cmd", "enable"),
        ("slide", str(0)),
        ("wellx", str(1)),
        ("welly", str(1)),
        ("fieldx", str(1)),
        ("fieldy", str(1)),
        ("value", "false"),
    ]
    cmd = cam.prefix + cmd

    response = cam.disable()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # enable_all
    cmd = [("cmd", "enableall"), ("value", "true")]
    cmd = cam.prefix + cmd

    response = cam.enable_all()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # disable_all
    cmd = [("cmd", "enableall"), ("value", "false")]
    cmd = cam.prefix + cmd

    response = cam.disable_all()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # save_template
    cmd = [
        ("sys", "0"),
        ("cmd", "save"),
        ("fil", "{ScanningTemplate}leicacam.xml"),
    ]
    cmd = cam.prefix + cmd

    response = cam.save_template()
    should_be = tuples_as_dict(cmd)

    assert response == should_be


def test_load(cam):
    """load_template should strip path and .xml from filename."""
    response = cam.load_template("test")
    assert response["fil"] == "{ScanningTemplate}test"

    response = cam.load_template("test.xml")
    assert response["fil"] == "{ScanningTemplate}test"

    response = cam.load_template("/path/to/{ScanningTemplate}test.xml")
    assert response["fil"] == "{ScanningTemplate}test"


def test_wait_for_timeout(cam):
    """Test wait_for when timeout expires."""
    cmd = "cmd"
    value = "stopscan"
    response = cam.wait_for(cmd, value, 0)

    assert response == OrderedDict()


def test_wait_for_long_timeout(cam, mock_socket):
    """Test wait_for when timeout expires."""
    cmd = "cmd"
    value = "stopscan"
    timeout = 1
    mock_socket.recv = MagicMock()
    mock_socket.recv.return_value = b""
    time_patch = patch("leicacam.cam.time", side_effect=[0, 0, 120])
    sleep_patch = patch("leicacam.cam.sleep")
    with sleep_patch, time_patch:
        response = cam.wait_for(cmd, value, timeout)

    assert response == OrderedDict()


def test_wait_for_any_value(cam):
    """Test wait_for a command and any value."""
    cmd = [("cmd", "startscan")]
    cam.send(cmd)
    response = cam.wait_for("cmd", None)

    cmd = cam.prefix + cmd
    should_be = tuples_as_dict(cmd)

    assert response == should_be


def test_close(cam, mock_socket):
    """Test closing the socket."""
    cam.close()

    assert mock_socket.close.call_count == 1


def test_receive_colon_string(cam):
    """Test bytes_as_dict function receiving a string with colon."""
    cmd = [("relpath", "C:\\image.ome.tif")]
    cam.socket.recv = MagicMock()
    cam.socket.recv.return_value = tuples_as_bytes(cmd)
    response = cam.receive()

    assert isinstance(response, list)
    for msg in response:
        assert msg == OrderedDict(cmd)


def test_receive_bad_string(cam):
    """Test bytes_as_dict function receiving an incomplete command."""
    cmd = [("cmd", "enableall")]
    cmd_string = "/cmd:enableall /value"
    cam.socket.recv = MagicMock()
    cam.socket.recv.return_value = cmd_string.encode()
    response = cam.receive()

    assert isinstance(response, list)
    for msg in response:
        assert msg == OrderedDict(cmd)


def test_receive_terminate_null_byte(cam):
    """Test _parse_receive function parsing a message with null byte."""
    start_cmd = [("cmd", "startscan")]
    stop_cmd = [("cmd", "stopscan")]
    all_cmds = [OrderedDict(start_cmd), OrderedDict(stop_cmd)]
    cmd_byte = b"/cmd:startscan\x00/cmd:stopscan\r\n"
    cam.socket.recv = MagicMock()
    cam.socket.recv.return_value = cmd_byte
    response = cam.receive()

    assert isinstance(response, list)
    assert response == all_cmds
