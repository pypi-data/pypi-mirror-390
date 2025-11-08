"""Abstract base class for text injection."""

from abc import ABC, abstractmethod
from typing import Optional


class TextInjector(ABC):
    """Abstract base class for text injection implementations."""

    def __init__(self):
        """Initialize text injector."""
        self._available = False

    @property
    def is_available(self) -> bool:
        """Check if this injection method is available."""
        return self._available

    @abstractmethod
    def inject_text(self, text: str) -> bool:
        """
        Inject text at the current cursor position.

        Args:
            text: Text to inject

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """
        Check if this text injection method is available.

        Returns:
            True if available, False otherwise
        """
        pass

    def inject_text_with_delay(self, text: str, delay_ms: int = 50) -> bool:
        """
        Inject text with a delay between characters.

        Args:
            text: Text to inject
            delay_ms: Delay between characters in milliseconds

        Returns:
            True if successful, False otherwise
        """
        return self.inject_text(text)

    @abstractmethod
    def simulate_key(self, key: str) -> bool:
        """
        Simulate a key press (e.g., "Return", "BackSpace").

        Args:
            key: Key name to simulate

        Returns:
            True if successful, False otherwise
        """
        pass
