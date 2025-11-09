# colorara/colorara/__init__.py

"""
colrs - A simple and elegant way to color your terminal text.
"""

__version__ = "0.1.1"

# Initialize colorama to make ANSI codes work on Windows and to auto-reset colors.
from colorama import init
init(autoreset=True)

from .core import cprint, cinput, colorize
from .magic import magic, revert

__all__ = [
    'cprint',
    'cinput',
    'colorize',
    'magic',
    'revert'
]
