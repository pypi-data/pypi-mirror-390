# colorara/colorara/__init__.py

"""
colrs - A simple and elegant way to color your terminal text.
"""

__version__ = "0.1.8"

# Initialize colorama to make ANSI codes work on Windows and to auto-reset colors.
from colorama import init
init(autoreset=True)

# The public API is now just act() and unact() for maximum simplicity.
from .magic import act, unact
from .animations import loading
from .tables import table
from .menus import menu
from .live import Live
from .logger import ColorizingStreamHandler
from .components import checkbox

__all__ = [
    'act',
    'unact',
    'loading',
    'table',
    'menu',
    'Live',
    'ColorizingStreamHandler',
    'checkbox'
]
