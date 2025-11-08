"""Global hotkey management."""

from .base import HotkeyManager
from .x11 import X11HotkeyManager
from .wayland import WaylandHotkeyManager
from .factory import create_hotkey_manager

__all__ = [
    "HotkeyManager",
    "X11HotkeyManager",
    "WaylandHotkeyManager",
    "create_hotkey_manager",
]
