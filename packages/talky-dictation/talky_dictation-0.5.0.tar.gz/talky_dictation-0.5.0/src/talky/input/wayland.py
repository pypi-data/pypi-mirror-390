"""Wayland text injection implementations."""

import subprocess
import shutil
import time
from typing import Optional
from .base import TextInjector


class YDoToolInjector(TextInjector):
    """Text injection using ydotool (Wayland)."""

    def __init__(self, typing_delay_ms: int = 0):
        """
        Initialize ydotool injector.

        Args:
            typing_delay_ms: Delay between keystrokes in milliseconds
        """
        super().__init__()
        self.typing_delay_ms = typing_delay_ms
        self._available = self.check_availability()

    def check_availability(self) -> bool:
        """
        Check if ydotool is available and has proper permissions.

        Returns:
            True if available, False otherwise
        """
        if not shutil.which("ydotool"):
            return False

        # Test if ydotool actually works (permissions check)
        try:
            result = subprocess.run(
                ["ydotool", "type", ""],
                capture_output=True,
                timeout=2,
                text=True
            )
            # If returncode is 0 or if it fails due to empty string but command works
            return result.returncode in [0, 1]
        except Exception:
            return False

    def inject_text(self, text: str) -> bool:
        """
        Inject text using ydotool.

        Args:
            text: Text to inject

        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False

        try:
            cmd = ["ydotool", "type"]

            if self.typing_delay_ms > 0:
                # ydotool uses microseconds for delay
                delay_us = self.typing_delay_ms * 1000
                cmd.extend(["--key-delay", str(delay_us)])

            cmd.append("--")
            cmd.append(text)

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode != 0 and result.stderr:
                print(f"ydotool stderr: {result.stderr}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("ydotool timeout")
            return False
        except Exception as e:
            print(f"ydotool error: {e}")
            return False

    def simulate_key(self, key: str) -> bool:
        """
        Simulate a key press using ydotool.

        Args:
            key: Key name or keycode

        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            return False

        try:
            # Map common key names to Linux keycodes
            key_map = {
                "Return": "28:1 28:0",
                "return": "28:1 28:0",
                "enter": "28:1 28:0",
                "BackSpace": "14:1 14:0",
                "backspace": "14:1 14:0",
                "Delete": "111:1 111:0",
                "delete": "111:1 111:0",
                "Escape": "1:1 1:0",
                "escape": "1:1 1:0",
                "Tab": "15:1 15:0",
                "tab": "15:1 15:0",
            }

            keycode = key_map.get(key)
            if not keycode:
                # Try as direct keycode
                keycode = key

            result = subprocess.run(
                ["ydotool", "key", keycode],
                capture_output=True,
                timeout=2,
                text=True
            )

            return result.returncode == 0

        except Exception as e:
            print(f"ydotool key error: {e}")
            return False


class ClipboardInjector(TextInjector):
    """
    Text injection using clipboard + paste simulation.

    This is a fallback method that works on both X11 and Wayland.
    It copies text to clipboard and simulates Ctrl+V.
    """

    def __init__(self, use_notification: bool = True):
        """
        Initialize clipboard injector.

        Args:
            use_notification: Show notification to user to paste manually
        """
        super().__init__()
        self.use_notification = use_notification
        self._available = self.check_availability()
        self._clipboard_tool = self._detect_clipboard_tool()

    def _detect_clipboard_tool(self) -> Optional[str]:
        """Detect available clipboard tool."""
        tools = ["wl-copy", "xclip", "xsel"]
        for tool in tools:
            if shutil.which(tool):
                return tool
        return None

    def check_availability(self) -> bool:
        """Check if clipboard tools are available."""
        return self._detect_clipboard_tool() is not None

    def _copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard."""
        if not self._clipboard_tool:
            return False

        try:
            if self._clipboard_tool == "wl-copy":
                # Wayland clipboard
                result = subprocess.run(
                    ["wl-copy"],
                    input=text,
                    text=True,
                    capture_output=True,
                    timeout=2
                )
            elif self._clipboard_tool == "xclip":
                # X11 clipboard
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text,
                    text=True,
                    capture_output=True,
                    timeout=2
                )
            elif self._clipboard_tool == "xsel":
                # X11 clipboard alternative
                result = subprocess.run(
                    ["xsel", "--clipboard", "--input"],
                    input=text,
                    text=True,
                    capture_output=True,
                    timeout=2
                )
            else:
                return False

            return result.returncode == 0

        except Exception as e:
            print(f"Clipboard copy error: {e}")
            return False

    def _simulate_paste(self) -> bool:
        """Simulate Ctrl+V to paste."""
        # Try ydotool first (Wayland)
        if shutil.which("ydotool"):
            try:
                # Ctrl = keycode 29, V = keycode 47
                result = subprocess.run(
                    ["ydotool", "key", "29:1", "47:1", "47:0", "29:0"],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0
            except Exception:
                pass

        # Try xdotool (X11)
        if shutil.which("xdotool"):
            try:
                result = subprocess.run(
                    ["xdotool", "key", "ctrl+v"],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0
            except Exception:
                pass

        return False

    def _show_notification(self) -> None:
        """Show notification to user to paste manually."""
        if not self.use_notification:
            return

        try:
            subprocess.run(
                [
                    "notify-send",
                    "-u", "normal",
                    "-t", "3000",
                    "Talky",
                    "Text copied to clipboard. Press Ctrl+V to paste."
                ],
                capture_output=True,
                timeout=1
            )
        except Exception:
            pass

    def inject_text(self, text: str) -> bool:
        """
        Inject text via clipboard.

        Args:
            text: Text to inject

        Returns:
            True if text copied to clipboard, False otherwise
        """
        if not self._available:
            return False

        # Copy to clipboard
        if not self._copy_to_clipboard(text):
            return False

        # Try to simulate paste
        paste_success = self._simulate_paste()

        # If paste simulation failed, show notification
        if not paste_success and self.use_notification:
            self._show_notification()

        # Return True if at least copied to clipboard
        return True

    def simulate_key(self, key: str) -> bool:
        """
        Simulate key press (limited support via clipboard).

        Args:
            key: Key name

        Returns:
            False (not supported via clipboard)
        """
        return False


class WaylandTextInjector(TextInjector):
    """
    Unified Wayland text injector with automatic fallback.

    Tries ydotool first, falls back to clipboard if unavailable.
    """

    def __init__(self, typing_delay_ms: int = 0, prefer_method: str = "auto"):
        """
        Initialize Wayland text injector.

        Args:
            typing_delay_ms: Delay between keystrokes in milliseconds
            prefer_method: Preferred method ("auto", "ydotool", "clipboard")
        """
        super().__init__()
        self.typing_delay_ms = typing_delay_ms
        self.prefer_method = prefer_method

        # Initialize both methods
        self._ydotool = YDoToolInjector(typing_delay_ms)
        self._clipboard = ClipboardInjector(use_notification=True)

        # Choose active injector based on preference and availability
        if prefer_method == "ydotool" and self._ydotool.is_available:
            self._active_injector = self._ydotool
            print("Wayland: Using ydotool for text injection")
        elif prefer_method == "clipboard" and self._clipboard.is_available:
            self._active_injector = self._clipboard
            print("Wayland: Using clipboard for text injection")
        elif prefer_method == "auto":
            if self._ydotool.is_available:
                self._active_injector = self._ydotool
                print("Wayland: Using ydotool for text injection")
            elif self._clipboard.is_available:
                self._active_injector = self._clipboard
                print("Wayland: Using clipboard for text injection (ydotool not available)")
            else:
                self._active_injector = None
                print("Wayland: No text injection method available")
        else:
            self._active_injector = None
            print(f"Wayland: Preferred method '{prefer_method}' not available")

        self._available = self._active_injector is not None

    def check_availability(self) -> bool:
        """Check if any Wayland injection method is available."""
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

        success = self._active_injector.inject_text(text)

        # If ydotool failed, try clipboard as fallback
        if not success and self._active_injector == self._ydotool:
            if self._clipboard.is_available:
                print("Wayland: ydotool failed, trying clipboard fallback")
                return self._clipboard.inject_text(text)

        return success

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
        if self._active_injector == self._ydotool:
            return "ydotool"
        elif self._active_injector == self._clipboard:
            return "clipboard"
        return None
