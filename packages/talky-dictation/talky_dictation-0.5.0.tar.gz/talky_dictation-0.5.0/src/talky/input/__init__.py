"""Text injection backends for X11 and Wayland."""

from .base import TextInjector
from .x11 import X11TextInjector, XDoToolInjector, PynputInjector
from .wayland import WaylandTextInjector, YDoToolInjector, ClipboardInjector
from .factory import create_text_injector

__all__ = [
    "TextInjector",
    "X11TextInjector",
    "XDoToolInjector",
    "PynputInjector",
    "WaylandTextInjector",
    "YDoToolInjector",
    "ClipboardInjector",
    "create_text_injector",
]
