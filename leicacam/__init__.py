"""Control Leica microscopes with python."""
__author__ = "Arve Seljebu"
__email__ = "arve.seljebu@gmail.com"
from os.path import join, dirname

__version__ = open(join(dirname(__file__), "VERSION")).read().strip()

__all__ = ["CAM"]

from .cam import CAM
