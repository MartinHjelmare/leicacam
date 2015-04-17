from leicacam.cam import *
import pytest

class EchoSocket:
    "Dummy echo socket for mocking."
    msg = ''

    def send(self, msg):
        self.msg = msg
        return len(msg)

    def recv(self, buffer_size):
        return self.msg[0:buffer_size]

    def connect(self, where):
        pass

    def settimeout(self, timeout):
        pass

# TEST
#- key (here cli) overrided if defined several times
#- prefix added
#- types (integer, float) should be converted to strings
def test_echo(monkeypatch):
    "Prefix + command sent should be same as echoed socket message."
    # mock socket
    monkeypatch.setattr("socket.socket", EchoSocket)

    # setup cam
    cam = CAM()

    cmd = [('cli', 'custom'), ('cmd', 'enableall'), ('value', 'true'),
           ('integer', 1234), ('float', 0.00234)]

    # monkeypathced EchoSocket will never flush
    def flush():
        pass
    cam.flush = flush

    cam.send(cmd)
    response = cam.receive()[0]

    sent = tuples_as_dict(cam.prefix + cmd)

    assert sent == response

def test_commands(monkeypatch):
    "short hand commands should work as intended"
    # mock socket
    monkeypatch.setattr("socket.socket", EchoSocket)

    # setup cam
    cam = CAM()

    # monkeypathced EchoSocket will never flush
    def flush():
        pass
    cam.flush = flush

    # get_information
    cmd = cam.prefix + [
        ('cmd', 'getinfo'),
        ('dev', 'stage')
    ]

    information = cam.get_information()
    should_be = tuples_as_dict(cmd)

    assert information == should_be

def test_load(monkeypatch):
    "load_template should strip path and .xml from filename"
    monkeypatch.setattr('socket.socket', EchoSocket)

    # setup cam
    cam = CAM()

    # monkeypathced EchoSocket will never flush
    def flush():
        pass
    cam.flush = flush

    response = cam.load_template('test')
    assert response['fil'] == '{ScanningTemplate}test'

    response = cam.load_template('test.xml')
    assert response['fil'] == '{ScanningTemplate}test'

    response = cam.load_template('/path/to/{ScanningTemplate}test.xml')
    assert response['fil'] == '{ScanningTemplate}test'
