"""Tests for cam module."""
import socket

import pytest
from mock import MagicMock, patch

from leicacam.cam import CAM, bytes_as_dict, tuples_as_dict

# pylint: disable=redefined-outer-name


def flush():
    """Flush the socket."""
    pass


@pytest.fixture
def cam():
    """Yield a CAM instance with a mock socket."""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = EchoSocket()
        mock_socket_class.return_value = mock_socket
        mock_cam = CAM()
        mock_cam.flush = flush

        yield mock_cam


class EchoSocket(object):
    """Dummy echo socket for mocking."""

    msg = ''

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

# TEST
# key (here cli) overrided if defined several times
# prefix added
# types (integer, float) should be converted to strings


def test_echo(cam):
    """Prefix + command sent should be same as echoed socket message."""
    cmd = [('cli', 'custom'), ('cmd', 'enableall'), ('value', 'true'),
           ('integer', 1234), ('float', 0.00234)]

    cam.send(cmd)
    response = cam.receive()[0]

    sent = tuples_as_dict(cam.prefix + cmd)

    assert sent == response


def test_send_bytes(cam):
    """Test send a bytes string."""
    cmd = b'/cmd:enableall /value:true'
    cam.send(cmd)
    response = cam.receive()[0]

    sent = bytes_as_dict(cam.prefix_bytes + cmd)

    assert sent == response


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
    cmd = cam.prefix + [
        ('cmd', 'getinfo'),
        ('dev', 'stage')
    ]

    information = cam.get_information()
    should_be = tuples_as_dict(cmd)

    assert information == should_be

    # start_scan
    cmd = cam.prefix + [
        ('cmd', 'startscan'),
    ]

    response = cam.start_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # stop_scan
    cmd = cam.prefix + [
        ('cmd', 'stopscan'),
    ]

    response = cam.stop_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # autofocus_scan
    cmd = cam.prefix + [
        ('cmd', 'autofocusscan'),
    ]

    response = cam.autofocus_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # pause_scan
    cmd = cam.prefix + [
        ('cmd', 'pausescan'),
    ]

    response = cam.pause_scan()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # enable
    cmd = [
        ('cmd', 'enable'),
        ('slide', str(0)),
        ('wellx', str(1)),
        ('welly', str(1)),
        ('fieldx', str(1)),
        ('fieldy', str(1)),
        ('value', 'true')
    ]
    cmd = cam.prefix + cmd

    response = cam.enable()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # disable
    cmd = [
        ('cmd', 'enable'),
        ('slide', str(0)),
        ('wellx', str(1)),
        ('welly', str(1)),
        ('fieldx', str(1)),
        ('fieldy', str(1)),
        ('value', 'false')
    ]
    cmd = cam.prefix + cmd

    response = cam.disable()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # enable_all
    cmd = [('cmd', 'enableall'), ('value', 'true')]
    cmd = cam.prefix + cmd

    response = cam.enable_all()
    should_be = tuples_as_dict(cmd)

    assert response == should_be

    # disable_all
    cmd = [('cmd', 'enableall'), ('value', 'false')]
    cmd = cam.prefix + cmd

    response = cam.disable_all()
    should_be = tuples_as_dict(cmd)

    assert response == should_be


def test_load(cam):
    """load_template should strip path and .xml from filename."""
    response = cam.load_template('test')
    assert response['fil'] == '{ScanningTemplate}test'

    response = cam.load_template('test.xml')
    assert response['fil'] == '{ScanningTemplate}test'

    response = cam.load_template('/path/to/{ScanningTemplate}test.xml')
    assert response['fil'] == '{ScanningTemplate}test'
