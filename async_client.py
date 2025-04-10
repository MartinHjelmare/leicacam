"""Test client using asyncio."""

import asyncio

from leicacam.async_cam import AsyncCAM


async def run() -> None:
    """Run client."""
    cam = AsyncCAM()
    await cam.connect()
    print(cam.welcome_msg)
    await cam.send(b"/cmd:deletelist")
    print(await cam.receive())
    await cam.send(b"/cmd:deletelist")
    print(await cam.wait_for(cmd="cmd", timeout=0.1))
    await cam.send(b"/cmd:deletelist")
    print(await cam.wait_for(cmd="cmd", timeout=0))
    print(await cam.wait_for(cmd="cmd", timeout=0.1))
    print(await cam.wait_for(cmd="test", timeout=0.1))
    cam.close()


if __name__ == "__main__":
    asyncio.run(run())
