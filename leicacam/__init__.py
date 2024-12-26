"""Control Leica microscopes with python."""

from pathlib import Path

__author__ = "Arve Seljebu"
__email__ = "arve.seljebu@gmail.com"
__version__ = (Path(__file__).parent / "VERSION").read_text(encoding="utf-8").strip()

__all__ = ["CAM"]

from .cam import CAM
