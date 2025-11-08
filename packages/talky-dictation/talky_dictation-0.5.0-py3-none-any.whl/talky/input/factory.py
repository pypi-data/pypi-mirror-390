"""Factory for creating appropriate text injector based on platform."""

from typing import Optional
from .base import TextInjector
from .x11 import X11TextInjector
from .wayland import WaylandTextInjector, ClipboardInjector
from ..utils.platform import get_platform_detector, DisplayServer


def create_text_injector(
    typing_delay_ms: int = 0,
    prefer_method: str = "auto"
) -> Optional[TextInjector]:
    """
    Create appropriate text injector for current platform.

    Args:
        typing_delay_ms: Delay between keystrokes in milliseconds
        prefer_method: Preferred injection method ("auto", "xdotool", "ydotool", "clipboard")

    Returns:
        TextInjector instance or None if no method available
    """
    detector = get_platform_detector()

    # Force clipboard method if requested
    if prefer_method == "clipboard":
        injector = ClipboardInjector(use_notification=True)
        if injector.is_available:
            print(f"Platform: Using clipboard text injection (forced)")
            return injector
        else:
            print("Platform: Clipboard method not available")
            return None

    # Platform-specific injection
    if detector.is_x11:
        injector = X11TextInjector(typing_delay_ms)
        if injector.is_available:
            print(f"Platform: X11 detected, using {injector.get_active_method()}")
            return injector
        else:
            print("Platform: X11 detected but no injection method available")
            return None

    elif detector.is_wayland:
        injector = WaylandTextInjector(typing_delay_ms, prefer_method)
        if injector.is_available:
            print(f"Platform: Wayland detected, using {injector.get_active_method()}")
            return injector
        else:
            print("Platform: Wayland detected but no injection method available")
            return None

    else:
        print(f"Platform: Unknown display server ({detector.display_server.value})")
        # Try clipboard as universal fallback
        injector = ClipboardInjector(use_notification=True)
        if injector.is_available:
            print("Platform: Using clipboard fallback")
            return injector

    return None
