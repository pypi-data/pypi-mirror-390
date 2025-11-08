"""X11 hotkey management using pynput with push-to-talk support."""

from typing import Callable, Dict, Set, Optional, Tuple
from .base import HotkeyManager


class X11HotkeyManager(HotkeyManager):
    """Hotkey manager for X11 using pynput with push-to-talk support."""

    def __init__(self):
        """Initialize X11 hotkey manager."""
        super().__init__()
        self._listener = None
        self._current_keys: Set = set()
        self._hotkey_combinations: Dict[frozenset, Tuple[Optional[Callable], Optional[Callable]]] = {}
        self._active_hotkeys: Set[frozenset] = set()  # Track which hotkeys are currently active

    def _parse_hotkey(self, hotkey: str) -> Optional[frozenset]:
        """
        Parse hotkey string into set of keys.

        Args:
            hotkey: Hotkey string (e.g., "<ctrl>+<super>")

        Returns:
            Frozenset of key objects or None if invalid
        """
        try:
            from pynput.keyboard import Key

            # Map string to pynput Key objects
            key_map = {
                "<ctrl>": Key.ctrl,
                "<control>": Key.ctrl,
                "<shift>": Key.shift,
                "<alt>": Key.alt,
                "<super>": Key.cmd,  # Super/Windows key
                "<cmd>": Key.cmd,
                "<win>": Key.cmd,
                "<space>": Key.space,
                "<enter>": Key.enter,
                "<return>": Key.enter,
                "<tab>": Key.tab,
                "<esc>": Key.esc,
                "<escape>": Key.esc,
            }

            keys = set()
            parts = hotkey.lower().replace(" ", "").split("+")

            for part in parts:
                if part in key_map:
                    keys.add(key_map[part])
                elif len(part) == 1:
                    # Single character key
                    keys.add(part)
                else:
                    print(f"Warning: Unknown key '{part}' in hotkey '{hotkey}'")
                    return None

            return frozenset(keys) if keys else None

        except ImportError:
            print("Error: pynput not available")
            return None

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
            on_press: Function to call when hotkey is pressed
            on_release: Function to call when hotkey is released

        Returns:
            True if registration successful, False otherwise
        """
        if not on_press and not on_release:
            print("Error: At least one callback (on_press or on_release) must be provided")
            return False

        key_combo = self._parse_hotkey(hotkey)
        if key_combo is None:
            return False

        self._hotkey_combinations[key_combo] = (on_press, on_release)
        self._registered_hotkeys[hotkey] = (on_press, on_release)

        print(f"X11: Registered hotkey {hotkey} (push-to-talk mode)")
        return True

    def unregister(self, hotkey: str) -> bool:
        """
        Unregister a hotkey.

        Args:
            hotkey: Hotkey combination to unregister

        Returns:
            True if unregistration successful, False otherwise
        """
        key_combo = self._parse_hotkey(hotkey)
        if key_combo is None:
            return False

        if key_combo in self._hotkey_combinations:
            del self._hotkey_combinations[key_combo]

        if key_combo in self._active_hotkeys:
            self._active_hotkeys.discard(key_combo)

        if hotkey in self._registered_hotkeys:
            del self._registered_hotkeys[hotkey]

        print(f"X11: Unregistered hotkey {hotkey}")
        return True

    def _on_press(self, key):
        """Handle key press event."""
        try:
            # Normalize the key
            if hasattr(key, 'char') and key.char:
                normalized_key = key.char
            else:
                normalized_key = key

            # Add key to current pressed keys
            self._current_keys.add(normalized_key)

            # Check if current combination matches any registered hotkey
            current_combo = frozenset(self._current_keys)

            for hotkey_combo, (on_press_cb, on_release_cb) in self._hotkey_combinations.items():
                # Check if all keys in the hotkey are pressed
                if hotkey_combo.issubset(current_combo):
                    # Only fire on_press if this hotkey wasn't already active
                    if hotkey_combo not in self._active_hotkeys:
                        self._active_hotkeys.add(hotkey_combo)
                        if on_press_cb:
                            on_press_cb()

        except Exception as e:
            print(f"X11 hotkey error on press: {e}")

    def _on_release(self, key):
        """Handle key release event."""
        try:
            # Normalize the key
            if hasattr(key, 'char') and key.char:
                normalized_key = key.char
            else:
                normalized_key = key

            # Check which active hotkeys contain this key
            for hotkey_combo in list(self._active_hotkeys):
                if normalized_key in hotkey_combo:
                    # This hotkey is being released
                    self._active_hotkeys.discard(hotkey_combo)

                    # Call the on_release callback
                    on_press_cb, on_release_cb = self._hotkey_combinations.get(hotkey_combo, (None, None))
                    if on_release_cb:
                        on_release_cb()

            # Remove key from current pressed keys
            self._current_keys.discard(normalized_key)

        except Exception as e:
            print(f"X11 hotkey error on release: {e}")

    def start(self) -> None:
        """Start the hotkey listener."""
        if self._is_running:
            return

        try:
            from pynput.keyboard import Listener

            self._listener = Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self._listener.start()
            self._is_running = True
            print("X11: Hotkey listener started (push-to-talk mode)")

        except Exception as e:
            print(f"Error starting X11 hotkey listener: {e}")
            raise

    def stop(self) -> None:
        """Stop the hotkey listener."""
        if not self._is_running:
            return

        try:
            if self._listener:
                self._listener.stop()
                self._listener = None
            self._is_running = False
            self._current_keys.clear()
            self._active_hotkeys.clear()
            print("X11: Hotkey listener stopped")

        except Exception as e:
            print(f"Error stopping X11 hotkey listener: {e}")
            raise
