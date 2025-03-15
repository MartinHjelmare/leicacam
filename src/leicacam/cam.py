"""Provide an interface to the CAM server."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
import functools
import logging
import os
import platform
import socket
from time import sleep, time
from typing import Any, Concatenate, ParamSpec, TypeVar, cast

import pydebug  # type: ignore[import-untyped]

_LOGGER = logging.getLogger(__name__)
_P = ParamSpec("_P")
_R = TypeVar("_R")


def logger(function: Callable[Concatenate[_P], _R]) -> Callable[_P, _R]:
    """Decorate passed in function and log message to module logger."""

    @functools.wraps(function)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        """Wrap function."""
        sep = cast(str, kwargs.get("sep", " "))
        end = cast(str, kwargs.get("end", ""))  # do not add newline by default
        out = sep.join([repr(x) for x in args])
        out = out + end
        _LOGGER.debug(out)
        return function(*args, **kwargs)

    return wrapper


# debug with `DEBUG=leicacam python script.py`
if platform.system() == "Windows":
    # monkeypatch
    @logger
    def debug(msg: bytes | str) -> None:
        """Debug on Windows."""
        try:
            dbg = os.environ["DEBUG"]
            if dbg in ("leicacam", "*"):
                print("leicacam " + str(msg))
        except KeyError:
            pass

else:
    debug = logger(pydebug.debug("leicacam"))


class BaseCAM:
    """Base driver for LASAF Computer Assisted Microscopy."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8895) -> None:
        """Set up instance."""
        self.host = host
        self.port = port
        # prefix for all commands
        self.prefix: list[tuple[str, str]] = [
            ("cli", "python-leicacam"),
            ("app", "matrix"),
        ]
        self.prefix_bytes = b"/cli:python-leicacam /app:matrix "
        self.buffer_size = 1024
        self.delay = 0.1  # poll every 100ms when waiting for incoming

    def _prepare_send(self, commands: list[tuple[str, str]] | bytes) -> bytes:
        """Prepare message to be sent.

        Parameters
        ----------
        commands : list of tuples or bytes string
            Commands as a list of tuples or a bytes string. cam.prefix is
            always prepended before sending.

        Returns
        -------
        string
            Message to be sent.

        """
        if isinstance(commands, bytes):
            msg = self.prefix_bytes + commands
        else:
            msg = tuples_as_bytes(self.prefix + commands)
        debug(b"> " + msg)
        return msg


def _parse_receive(incoming: bytes) -> list[OrderedDict[str, str]]:
    """Parse received response.

    Parameters
    ----------
    incoming : bytes string
        incoming bytes from socket server.

    Returns
    -------
    list of OrderedDict
        Received message as a list of OrderedDict.

    """
    debug(b"< " + incoming)
    # first split on terminating null byte
    incoming_split = incoming.split(b"\x00")
    msgs = []
    for msg in incoming_split:
        # then split on line ending
        split_msg = msg.splitlines()
        msgs.extend(split_msg)
    # return as list of several messages received
    return [bytes_as_dict(msg) for msg in msgs]


class CAM(BaseCAM):
    """Driver for LASAF Computer Assisted Microscopy."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set up instance."""
        super().__init__(*args, **kwargs)
        self.connect()

    def connect(self) -> None:
        """Connect to LASAF through a CAM-socket."""
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(False)  # non-blocking
        sleep(self.delay)  # wait for response
        self.welcome_msg = self.socket.recv(self.buffer_size)  # receive welcome message

    def flush(self) -> None:
        """Flush incoming socket messages."""
        debug("flushing incoming socket messages")
        try:
            while True:
                msg = self.socket.recv(self.buffer_size)
                debug(b"< " + msg)
        except OSError:
            pass

    def send(self, commands: list[tuple[str, str]] | bytes) -> int:
        """Send commands to LASAF through CAM-socket.

        Parameters
        ----------
        commands : list of tuples or bytes string
            Commands as a list of tuples or a bytes string. cam.prefix is
            always prepended before sending.

        Returns
        -------
        int
            Bytes sent.

        Example
        -------
        ::

            >>> # send list of tuples
            >>> cam.send([('cmd', 'enableall'), ('value', 'true')])

            >>> # send bytes string
            >>> cam.send(b'/cmd:enableall /value:true')

        """
        self.flush()  # discard any waiting messages
        msg = self._prepare_send(commands)
        return self.socket.send(msg)

    def receive(self) -> list[OrderedDict[str, str]]:
        """Receive message from socket interface as list of OrderedDict."""
        try:
            incoming = self.socket.recv(self.buffer_size)
        except OSError:
            return []

        return _parse_receive(incoming)

    def wait_for(
        self, cmd: str, value: str | None = None, timeout: int = 60
    ) -> OrderedDict[str, str]:
        """Hang until command is received.

        If value is supplied, it will hang until ``cmd:value`` is received.

        Parameters
        ----------
        cmd : string
            Command to wait for in bytestring from microscope CAM interface. If
            ``value`` is falsy, value of received command does not matter.
        value : string
            Wait until ``cmd:value`` is received.
        timeout : int
            Minutes to wait for command. If timeout is reached, an empty
            OrderedDict will be returned.

        Returns
        -------
        collections.OrderedDict
            Last received message or empty message if timeout is reached.

        """
        wait = time() + timeout * 60
        while True:
            if time() > wait:
                return OrderedDict()
            msgs = self.receive()
            msg = check_messages(msgs, cmd, value=value)
            if msg:
                return msg
            sleep(self.delay)

    def close(self) -> None:
        """Close the socket."""
        self.socket.close()

    # convenience methods for commands
    def start_scan(self) -> OrderedDict[str, str]:
        """Start the matrix scan."""
        cmd = [("cmd", "startscan")]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def stop_scan(self) -> OrderedDict[str, str]:
        """Stop the matrix scan."""
        cmd = [("cmd", "stopscan")]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def autofocus_scan(self) -> OrderedDict[str, str]:
        """Start the autofocus job."""
        cmd = [("cmd", "autofocusscan")]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def pause_scan(self) -> OrderedDict[str, str]:
        """Pause the matrix scan."""
        cmd = [("cmd", "pausescan")]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def enable(
        self,
        slide: int = 0,
        wellx: int = 1,
        welly: int = 1,
        fieldx: int = 1,
        fieldy: int = 1,
    ) -> OrderedDict[str, str]:
        """Enable a given scan field."""
        cmd = [
            ("cmd", "enable"),
            ("slide", str(slide)),
            ("wellx", str(wellx)),
            ("welly", str(welly)),
            ("fieldx", str(fieldx)),
            ("fieldy", str(fieldy)),
            ("value", "true"),
        ]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def disable(
        self,
        slide: int = 0,
        wellx: int = 1,
        welly: int = 1,
        fieldx: int = 1,
        fieldy: int = 1,
    ) -> OrderedDict[str, str]:
        """Disable a given scan field."""
        cmd = [
            ("cmd", "enable"),
            ("slide", str(slide)),
            ("wellx", str(wellx)),
            ("welly", str(welly)),
            ("fieldx", str(fieldx)),
            ("fieldy", str(fieldy)),
            ("value", "false"),
        ]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def enable_all(self) -> OrderedDict[str, str]:
        """Enable all scan fields."""
        cmd = [("cmd", "enableall"), ("value", "true")]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def disable_all(self) -> OrderedDict[str, str]:
        """Disable all scan fields."""
        cmd = [("cmd", "enableall"), ("value", "false")]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def save_template(
        self, filename: str = "{ScanningTemplate}leicacam.xml"
    ) -> OrderedDict[str, str]:
        """Save scanning template to filename."""
        cmd = [("sys", "0"), ("cmd", "save"), ("fil", str(filename))]
        self.send(cmd)
        return self.wait_for(*cmd[0])

    def load_template(
        self, filename: str = "{ScanningTemplate}leicacam.xml"
    ) -> OrderedDict[str, str]:
        """Load scanning template from filename.

        Template needs to exist in database, otherwise it will not load.

        Parameters
        ----------
        filename : str
            Filename to template to load. Filename may contain path also, in
            such case, the basename will be used. '.xml' will be stripped
            from the filename if it exists because of a bug; LASAF implicit
            add '.xml'. If '{ScanningTemplate}' is omitted, it will be added.

        Returns
        -------
        collections.OrderedDict
            Response from LASAF in an ordered dict.

        Example
        -------
        ::

            >>> # load {ScanningTemplate}leicacam.xml
            >>> cam.load_template('leicacam')

            >>> # load {ScanningTemplate}leicacam.xml
            >>> cam.load_template('{ScanningTemplate}leicacam')

            >>> # load {ScanningTemplate}leicacam.xml
            >>> cam.load_template('/path/to/{ScanningTemplate}leicacam.xml')

        """
        basename = os.path.basename(filename)
        if basename[-4:] == ".xml":
            basename = basename[:-4]
        if basename[:18] != "{ScanningTemplate}":
            basename = "{ScanningTemplate}" + basename
        cmd = [("sys", "0"), ("cmd", "load"), ("fil", str(basename))]
        self.send(cmd)
        return self.wait_for(*cmd[1])

    def get_information(self, about: str = "stage") -> OrderedDict[str, str]:
        """Get information about given keyword. Defaults to stage."""
        cmd = [("cmd", "getinfo"), ("dev", str(about))]
        self.send(cmd)
        return self.wait_for(*cmd[1])


##
# Helper methods
##


def tuples_as_bytes(cmds: list[tuple[str, str]]) -> bytes:
    """Format list of tuples to CAM message with format /key:val.

    Parameters
    ----------
    cmds : list of tuples
        List of commands as tuples.

    Returns
    -------
    bytes
        Sequence of /key:val.

    Example
    -------
    ::

        >>> tuples_as_bytes([('cmd', 'val'), ('cmd2', 'val2')])
        b'/cmd:val /cmd2:val2'

    """
    commands = OrderedDict(cmds)  # override equal keys
    tmp = []
    for key, val in commands.items():
        key = str(key)
        val = str(val)
        tmp.append("/" + key + ":" + val)
    return " ".join(tmp).encode()


def tuples_as_dict(_list: list[tuple[str, str]]) -> OrderedDict[str, str]:
    """Translate a list of tuples to OrderedDict with key and val as strings.

    Parameters
    ----------
    _list : list of tuples

    Returns
    -------
    collections.OrderedDict

    Example
    -------
    ::

        >>> tuples_as_dict([('cmd', 'val'), ('cmd2', 'val2')])
        OrderedDict([('cmd', 'val'), ('cmd2', 'val2')])

    """
    _dict = OrderedDict()
    for key, val in _list:
        key = str(key)
        val = str(val)
        _dict[key] = val
    return _dict


def bytes_as_dict(msg: bytes) -> OrderedDict[str, str]:
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
    cmd_strings = msg.decode()[1:].split(r" /")
    cmds = OrderedDict()
    for cmd in cmd_strings:
        unpacked = cmd.split(":")
        # handle string not well formatted (ex filenames with c:\)
        if len(unpacked) > 2:
            key = unpacked[0]
            val = ":".join(unpacked[1:])
        elif len(unpacked) < 2:
            continue
        else:
            key, val = unpacked
        cmds[key] = val
    return cmds


def check_messages(
    msgs: list[OrderedDict[str, str]], cmd: str, value: str | None = None
) -> OrderedDict[str, str] | None:
    """Check if specific message is present.

    Parameters
    ----------
    cmd : string
        Command to check for in bytestring from microscope CAM interface. If
        ``value`` is falsy, value of received command does not matter.
    value : string
        Check if ``cmd:value`` is received.

    Returns
    -------
    collections.OrderedDict
        Correct message or None if no correct message if found.

    """
    for msg in msgs:
        if value and msg.get(cmd) == value:
            return msg
        if not value and msg.get(cmd):
            return msg
    return None
