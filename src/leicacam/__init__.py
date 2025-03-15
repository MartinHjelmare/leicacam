"""Control Leica microscopes with python."""

from .async_cam import AsyncCAM
from .cam import CAM

__all__ = ["CAM", "AsyncCAM"]
__version__ = "0.6.0"
