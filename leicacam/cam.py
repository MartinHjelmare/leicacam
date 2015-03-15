from time import sleep
from collections import OrderedDict
import socket, pydebug, platform, os

# debug with `DEBUG=leicacam python script.py`
if platform.system() == 'Windows':
    # monkeypatch
    def debug(msg):
        try:
            dbg = os.environ['DEBUG']
            if dbg == 'leicacam' or dbg == '*':
                print('leicacam ' + str(msg))
        except KeyError:
            pass
else:
    debug = pydebug.debug('leicacam')


class CAM:
    "Driver for LASAF Computer Assisted Microscopy."

    def __init__(self, host='127.0.0.1', port=8895):
        self.host = host
        self.port = port
        # prefix for all commands
        self.prefix = [('cli', 'python-leicacam'),
                       ('app', 'matrix')]
        self.prefix_bytes = b'/cli:python-leicacam /app:matrix '
        self.buffer_size = 1024
        self.delay = 0.1 # wait 100ms for response when sending commands
        self.connect()


    def connect(self):
        "Connects to LASAF through a CAM-socket."
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(False) # non-blocking
        sleep(self.delay) # wait for response
        self.welcome_msg = self.socket.recv(self.buffer_size) # receive welcome message


    def flush(self):
        "Flush incomming socket messages."
        debug('flushing incomming socket messages')
        try:
            while(True):
                msg = self.socket.recv(self.buffer_size)
                debug(b'< ' + msg)
        except socket.error:
            pass


    def send(self, commands, delay=None):
        """Send commands to LASAF through CAM-socket.

        Paramenters
        -----------
        commands : list of tuples or bytes string
            Commands as a list of tuples or a bytes string.
            leicacam.prefix is allways prepended before sending.
            Example: [('cmd', 'enableall'), ('value', 'true')]
        delay : float
            Wait for response in given amount of seconds.

        Returns
        -------
        OrderedDict
            Response message from LAS AF as an OrderedDict.
        """
        self.flush() # discard any waiting messages
        if type(commands) == bytes:
            msg = self.prefix_bytes + commands
        else:
            msg = tuples_as_bytes(self.prefix + commands)
        debug(b'> ' + msg)
        self.socket.send(msg)
        if delay:
            sleep(delay)
        else:
            sleep(self.delay)
        return self.receive()


    def receive(self):
        "Receive message from socket interface as list of OrderedDict."

        try:
            incomming = self.socket.recv(self.buffer_size)
            debug(b'< ' + incomming)
        except socket.error:
            return []

        # split received messages
        # return as list of several messages received
        msgs = incomming.splitlines()
        return [bytes_as_dict(msg) for msg in msgs]


    # convinience functions for commands
    def start_scan(self):
        "Starts the matrix scan."
        cmd = [('cmd', 'startscan')]
        return self.send(cmd)


    def stop_scan(self):
        "Stops the matrix scan."
        cmd = [('cmd', 'stopscan')]
        return self.send(cmd)


    def pause_scan(self):
        "Pauses the matrix scan."
        cmd = [('cmd', 'pausescan')]
        return self.send(cmd)


    def enable(self, slide=0, wellx=1, welly=1,
               fieldx=1, fieldy=1):
        "Enable a given scan field."
        cmd = [
            ('cmd', 'enable'),
            ('slide', str(slide)),
            ('wellx', str(wellx)),
            ('welly', str(welly)),
            ('fieldx', str(fieldx)),
            ('fieldy', str(fieldy)),
            ('value', 'true')
        ]
        return self.send(cmd)


    def disable(self, slide=0, wellx=1, welly=1,
               fieldx=1, fieldy=1):
        "Disable a given scan field."
        cmd = [
            ('cmd', 'enable'),
            ('slide', str(slide)),
            ('wellx', str(wellx)),
            ('welly', str(welly)),
            ('fieldx', str(fieldx)),
            ('fieldy', str(fieldy)),
            ('value', 'false')
        ]
        return self.send(cmd)


    def enable_all(self):
        "Enable all scan fields."
        cmd = [('cmd', 'enableall'), ('value', 'true')]
        return self.send(cmd)


    def disable_all(self):
        "Disable all scan fields."
        cmd = [('cmd', 'enableall'), ('value', 'false')]
        return self.send(cmd)


    def save_template(self, filename="{ScanningTemplate}leicacam.xml"):
        "Save scanning template to filename."
        cmd = [
            ('sys', '0'),
            ('cmd', 'save'),
            ('fil', str(filename))
        ]
        return self.send(cmd, delay=0.5)


    def load_template(self, filename="{ScanningTemplate}leicacam.xml"):
        """Load scanning template from filename. Template needs to exist
        in database, otherwise it will not load.

        Parameters
        ----------
        filename : str
            Filename to template to load. Filename may contain path also, in
            such case, the basename will be used. '.xml' will be stripped
            from the filename if it exists because of a bug; LASAF implicit
            add '.xml'. If '{ScanningTemplate}' is omitted, it will be added.

                > # load {ScanningTemplate}leicacam.xml
                > cam.load_template('leicacam')

                > # load {ScanningTemplate}leicacam.xml
                > cam.load_template('{ScanningTemplate}leicacam')

                > # load {ScanningTemplate}leicacam.xml
                > cam.load_template('/path/to/{ScanningTemplate}leicacam.xml')

        Returns
        -------
        collections.OrderedDict
            Response from LASAF in an ordered dict.
        """
        basename = os.path.basename(filename)
        if basename[-4:] == '.xml':
            basename = basename[:-4]
        if basename[:18] != '{ScanningTemplate}':
            basename = '{ScanningTemplate}' + basename
        cmd = [
            ('sys', '0'),
            ('cmd', 'load'),
            ('fil', str(basename))
        ]
        return self.send(cmd, delay=1)


    def get_information(self, about='stage'):
        "Get information about given keyword. Defaults to stage."
        cmd = [
            ('cmd', 'getinfo'),
            ('dev', str(about))
        ]
        response = self.send(cmd, delay=0.5) # wait a half second
        if response:
            return response[0] # assume we want first response
        else:
            return None



##
# Helper methods
##

def tuples_as_bytes(cmds):
    """Format list of tuples to CAM message with format /key:val.

    Parameters
    ----------
    cmds : list of tuples
        List of commands as tuples.
        Example: [('cmd', 'val'), ('cmd2', 'val2')]

    Returns
    -------
    bytes
        Sequence of /key:val.
    """
    cmds = OrderedDict(cmds) # override equal keys
    tmp = []
    for key,val in cmds.items():
        key = str(key)
        val = str(val)
        tmp.append('/' + key + ':' + val)
    return ' '.join(tmp).encode()


def tuples_as_dict(_list):
    """Translate a list of tuples to OrderedDict with key and val
    as strings.

    Parameters
    ----------
    _list : list of tuples
        Example: [('cmd', 'val'), ('cmd2', 'val2')]

    Returns
    -------
    collections.OrderedDict
    """
    _dict = OrderedDict()
    for key,val in _list:
        key = str(key)
        val = str(val)
        _dict[key] = val
    return _dict


def bytes_as_dict(msg):
    """Parse CAM message to OrderedDict based on format /key:val.

    Parameters
    ----------
    msg : bytes
        Sequence of /key:val.

    Returns
    -------
    collections.OrderedDict
        With /key:val => dict[key] = val.
    """
    # decode bytes, assume '/' in start
    cmd_strings = msg.decode()[1:].split(r' /')
    cmds = OrderedDict()
    for cmd in cmd_strings:
        unpacked = cmd.split(':')
        # handle string not well formated (ex filenames with c:\)
        if len(unpacked) > 2:
            key = unpacked[0]
            val = ':'.join(unpacked[1:])
        elif len(unpacked) < 2:
            continue
        else:
            key,val = unpacked
        cmds[key] = val
    return cmds
