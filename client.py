"""Test client."""
from time import sleep

from leicacam.cam import CAM


def run():
    """Run client."""
    cam = CAM()
    print(cam.welcome_msg)
    print(cam.send(b"/cmd:deletelist"))
    sleep(0.1)
    print(cam.receive())
    print(cam.send(b"/cmd:deletelist"))
    sleep(0.1)
    print(cam.wait_for(cmd="cmd", timeout=0.1))
    cam.close()


if __name__ == "__main__":
    run()
