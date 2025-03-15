"""Provide an interface using asyncio to the CAM server."""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from typing import Any

from async_timeout import timeout as async_timeout

from leicacam.cam import BaseCAM, _parse_receive, check_messages


class AsyncCAM(BaseCAM):
    """Driver for LASAF Computer Assisted Microscopy using asyncio."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set up instance."""
        super().__init__(*args, **kwargs)
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.welcome_msg: bytes | None = None

    async def connect(self) -> None:
        """Connect to LASAF through a CAM-socket."""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.welcome_msg = await self.reader.read(self.buffer_size)

    async def send(self, commands: list[tuple[str, str]] | bytes) -> None:
        """Send commands to LASAF through CAM-socket.

        Parameters
        ----------
        commands : list of tuples or bytes string
            Commands as a list of tuples or a bytes string. cam.prefix is
            allways prepended before sending.

        Returns
        -------
        int
            Bytes sent.

        Example
        -------
        ::

            >>> # send list of tuples
            >>> await cam.send([('cmd', 'enableall'), ('value', 'true')])

            >>> # send bytes string
            >>> await cam.send(b'/cmd:enableall /value:true')

        """
        if self.writer is None:
            raise RuntimeError("Not connected to CAM server.")
        msg = self._prepare_send(commands)
        self.writer.write(msg)
        await self.writer.drain()

    async def receive(self) -> list[OrderedDict[str, str]]:
        """Receive message from socket interface as list of OrderedDict."""
        if self.reader is None:
            raise RuntimeError("Not connected to CAM server.")
        try:
            incoming = await self.reader.read(self.buffer_size)
        except OSError:
            return []

        return _parse_receive(incoming)

    async def wait_for(
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
            Last received messsage or empty message if timeout is reached.

        """
        try:
            async with async_timeout(timeout * 60):
                while True:
                    msgs = await self.receive()
                    msg = check_messages(msgs, cmd, value=value)
                    if msg:
                        return msg
        except TimeoutError:
            return OrderedDict()

    def close(self) -> None:
        """Close stream."""
        if self.writer is None:
            return
        if self.writer.can_write_eof():
            self.writer.write_eof()
        self.writer.close()
