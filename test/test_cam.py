"""Tests for cam module."""
import pytest
from mock import patch

from leicacam.cam import CAM, bytes_as_dict, tuples_as_dict

# pylint: disable=redefined-outer-name


def flush():
    """Flush the socket."""
    pass


@pytest.fixture
def cam():
    """Mock a CAM instance."""
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


def test_load(cam):
    """load_template should strip path and .xml from filename."""
    response = cam.load_template('test')
    assert response['fil'] == '{ScanningTemplate}test'

    response = cam.load_template('test.xml')
    assert response['fil'] == '{ScanningTemplate}test'

    response = cam.load_template('/path/to/{ScanningTemplate}test.xml')
    assert response['fil'] == '{ScanningTemplate}test'
