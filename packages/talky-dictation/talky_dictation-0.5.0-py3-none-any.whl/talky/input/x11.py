"""X11 text injection implementations."""

import subprocess
import shutil
import time
from typing import Optional
from .base import TextInjector


class XDoToolInjector(TextInjector):
    """Text injection using xdotool (X11 only)."""

    def __init__(self, typing_delay_ms: int = 0):
        """
        Initialize xdotool injector.

        Args:
            typing_delay_ms: Delay between keystrokes in milliseconds
        """
        super().__init__()
        self.typing_delay_ms = typing_delay_ms
        self._available = self.check_availability()

    def check_availability(self) -> bool:
        """Check if xdotool is available."""
        return shutil.which("xdotool") is not None

    def inject_text(self, text: str) -> bool:
        """
        Inject text using xdotool.

        Args:
            text: Text to inject

        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False

        try:
            cmd = ["xdotool", "type"]

            if self.typing_delay_ms > 0:
                cmd.extend(["--delay", str(self.typing_delay_ms)])

            cmd.append("--")
            cmd.append(text)

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5,
                text=True
            )

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("xdotool timeout")
            return False
        except Exception as e:
            print(f"xdotool error: {e}")
            return False

    def simulate_key(self, key: str) -> bool:
        """
        Simulate a key press using xdotool.

        Args:
            key: Key name (e.g., "Return", "BackSpace", "Escape")

        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False

        try:
            result = subprocess.run(
                ["xdotool", "key", "--", key],
                capture_output=True,
                timeout=2,
                text=True
            )
            return result.returncode == 0

        except Exception as e:
            print(f"xdotool key error: {e}")
            return False


class PynputInjector(TextInjector):
    """Text injection using pynput (X11 fallback)."""

    def __init__(self, typing_delay_ms: int = 0):
        """
        Initialize pynput injector.

        Args:
            typing_delay_ms: Delay between keystrokes in milliseconds
        """
        super().__init__()
        self.typing_delay_ms = typing_delay_ms
        self._keyboard = None
        self._available = self.check_availability()

    def check_availability(self) -> bool:
        """Check if pynput is available."""
        try:
            from pynput.keyboard import Controller
            self._keyboard = Controller()
            return True
        except Exception as e:
            print(f"pynput not available: {e}")
            return False

    def inject_text(self, text: str) -> bool:
        """
        Inject text using pynput.

        Args:
            text: Text to inject

        Returns:
            True if successful, False otherwise
        """
        if not self._available or not self._keyboard:
            return False

        try:
            if self.typing_delay_ms > 0:
                delay_s = self.typing_delay_ms / 1000.0
                for char in text:
                    self._keyboard.type(char)
                    time.sleep(delay_s)
            else:
                self._keyboard.type(text)

            return True

        except Exception as e:
            print(f"pynput inject error: {e}")
            return False

    def simulate_key(self, key: str) -> bool:
        """
        Simulate a key press using pynput.

        Args:
            key: Key name (e.g., "enter", "backspace")

        Returns:
            True if successful, False otherwise
        """
        if not self._available or not self._keyboard:
            return False

        try:
            from pynput.keyboard import Key

            # Map common key names to pynput Key enum
            key_map = {
                "Return": Key.enter,
                "return": Key.enter,
                "enter": Key.enter,
                "BackSpace": Key.backspace,
                "backspace": Key.backspace,
                "Delete": Key.delete,
                "delete": Key.delete,
                "Escape": Key.esc,
                "escape": Key.esc,
                "Tab": Key.tab,
                "tab": Key.tab,
            }

            key_obj = key_map.get(key)
            if key_obj:
                self._keyboard.press(key_obj)
                self._keyboard.release(key_obj)
                return True
            else:
                # Try as string key
                self._keyboard.type(key)
                return True

        except Exception as e:
            print(f"pynput key error: {e}")
            return False


class X11TextInjector(TextInjector):
    """
    Unified X11 text injector with automatic fallback.

    Tries xdotool first, falls back to pynput if xdotool unavailable.
    """

    def __init__(self, typing_delay_ms: int = 0):
        """
        Initialize X11 text injector.

        Args:
            typing_delay_ms: Delay between keystrokes in milliseconds
        """
        super().__init__()
        self.typing_delay_ms = typing_delay_ms

        # Try xdotool first
        self._xdotool = XDoToolInjector(typing_delay_ms)
        self._pynput = PynputInjector(typing_delay_ms)

        if self._xdotool.is_available:
            self._active_injector = self._xdotool
            print("X11: Using xdotool for text injection")
        elif self._pynput.is_available:
            self._active_injector = self._pynput
            print("X11: Using pynput for text injection (xdotool not found)")
        else:
            self._active_injector = None
            print("X11: No text injection method available")

        self._available = self._active_injector is not None

    def check_availability(self) -> bool:
        """Check if any X11 injection method is available."""
        return self._available

    def inject_text(self, text: str) -> bool:
        """
        Inject text using available method.

        Args:
            text: Text to inject

        Returns:
            True if successful, False otherwise
        """
        if not self._active_injector:
            return False

        return self._active_injector.inject_text(text)

    def simulate_key(self, key: str) -> bool:
        """
        Simulate a key press.

        Args:
            key: Key name

        Returns:
            True if successful, False otherwise
        """
        if not self._active_injector:
            return False

        return self._active_injector.simulate_key(key)

    def get_active_method(self) -> Optional[str]:
        """Get the name of the active injection method."""
        if self._active_injector == self._xdotool:
            return "xdotool"
        elif self._active_injector == self._pynput:
            return "pynput"
        return None
