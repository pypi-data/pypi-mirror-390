"""Factory for creating appropriate hotkey manager based on platform."""

from typing import Optional
from .base import HotkeyManager
from .x11 import X11HotkeyManager
from .wayland import WaylandHotkeyManager
from ..utils.platform import get_platform_detector


def create_hotkey_manager() -> Optional[HotkeyManager]:
    """
    Create appropriate hotkey manager for current platform.

    Returns:
        HotkeyManager instance or None if platform not supported
    """
    detector = get_platform_detector()

    if detector.is_x11:
        try:
            manager = X11HotkeyManager()
            print(f"Platform: X11 detected, using pynput hotkey manager")
            return manager
        except Exception as e:
            print(f"Platform: X11 hotkey manager failed to initialize: {e}")
            return None

    elif detector.is_wayland:
        manager = WaylandHotkeyManager()
        print(f"Platform: Wayland detected, using {detector.desktop_environment.value} hotkey manager")
        if not manager.is_supported():
            print(f"Platform: Warning - Global hotkeys may require manual setup on Wayland")
        return manager

    else:
        print(f"Platform: Unknown display server ({detector.display_server.value})")
        print(f"Platform: Hotkey management not available")
        return None
