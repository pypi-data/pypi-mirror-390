"""Abstract base class for hotkey management."""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class HotkeyManager(ABC):
    """Abstract base class for hotkey management implementations."""

    def __init__(self):
        """Initialize hotkey manager."""
        self._registered_hotkeys = {}
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Check if hotkey listener is running."""
        return self._is_running

    @abstractmethod
    def register(
        self,
        hotkey: str,
        on_press: Optional[Callable[[], None]] = None,
        on_release: Optional[Callable[[], None]] = None
    ) -> bool:
        """
        Register a global hotkey with press and/or release callbacks.

        Args:
            hotkey: Hotkey combination (e.g., "<ctrl>+<super>")
            on_press: Function to call when hotkey is pressed (optional)
            on_release: Function to call when hotkey is released (optional)

        Returns:
            True if registration successful, False otherwise
        """
        pass

    @abstractmethod
    def unregister(self, hotkey: str) -> bool:
        """
        Unregister a hotkey.

        Args:
            hotkey: Hotkey combination to unregister

        Returns:
            True if unregistration successful, False otherwise
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """Start the hotkey listener."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the hotkey listener."""
        pass

    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        for hotkey in list(self._registered_hotkeys.keys()):
            self.unregister(hotkey)
