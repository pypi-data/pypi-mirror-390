"""Wayland hotkey management with DE-specific implementations."""

import subprocess
from typing import Callable, Optional
from .base import HotkeyManager
from ..utils.platform import get_platform_detector, DesktopEnvironment


class WaylandHotkeyManager(HotkeyManager):
    """
    Hotkey manager for Wayland.

    Note: Wayland doesn't have universal global hotkey support.
    This implementation provides:
    1. DE-specific implementations (GNOME, KDE)
    2. Manual configuration instructions for compositor-based WMs
    3. Fallback polling mode (limited)
    """

    def __init__(self):
        """Initialize Wayland hotkey manager."""
        super().__init__()
        self._detector = get_platform_detector()
        self._callbacks = {}
        self._support_available = False
        self._instructions_shown = False

    def _show_setup_instructions(self, hotkey: str) -> None:
        """Show setup instructions for manual hotkey configuration."""
        if self._instructions_shown:
            return

        self._instructions_shown = True

        de = self._detector.desktop_environment

        if de == DesktopEnvironment.SWAY:
            instructions = f"""
Wayland (Sway): Manual hotkey setup required

Add this to your Sway config (~/.config/sway/config):

    bindsym Control+Super_L exec talky-toggle

Then reload Sway config (Mod+Shift+C)
"""
        elif de == DesktopEnvironment.HYPRLAND:
            instructions = f"""
Wayland (Hyprland): Manual hotkey setup required

Add this to your Hyprland config (~/.config/hypr/hyprland.conf):

    bind = CTRL, SUPER, exec, talky-toggle

Then reload Hyprland config
"""
        elif de == DesktopEnvironment.I3:
            instructions = f"""
Wayland (i3): Manual hotkey setup required

Add this to your i3 config (~/.config/i3/config):

    bindsym Control+Mod4 exec talky-toggle

Then reload i3 config (Mod+Shift+R)
"""
        else:
            instructions = f"""
Wayland: Global hotkeys not available on {de.value}

Workaround: Use system tray button to activate recording
Or: Configure hotkey in your compositor/window manager settings
"""

        print(instructions)

        # Try to show notification
        try:
            subprocess.run(
                [
                    "notify-send",
                    "-u", "normal",
                    "-t", "10000",
                    "Talky - Hotkey Setup Required",
                    instructions
                ],
                capture_output=True,
                timeout=1
            )
        except Exception:
            pass

    def register(
        self,
        hotkey: str,
        on_press: Optional[Callable[[], None]] = None,
        on_release: Optional[Callable[[], None]] = None
    ) -> bool:
        """
        Register a global hotkey (if supported).

        Note: Wayland does not support push-to-talk natively.
        For manual configuration, users should set up a toggle in their compositor.

        Args:
            hotkey: Hotkey combination (e.g., "<ctrl>+<super>")
            on_press: Function to call when hotkey is pressed
            on_release: Function to call when hotkey is released

        Returns:
            True if registration successful or instructions shown, False otherwise
        """
        # Store callbacks (Wayland compositors typically only support toggle)
        self._registered_hotkeys[hotkey] = (on_press, on_release)
        self._callbacks[hotkey] = (on_press, on_release)

        de = self._detector.desktop_environment

        # Try GNOME D-Bus keybinding (GNOME/Wayland)
        if de == DesktopEnvironment.GNOME:
            success = self._register_gnome(hotkey, callback)
            if success:
                print(f"Wayland (GNOME): Registered hotkey via D-Bus")
                return True
            else:
                print(f"Wayland (GNOME): Failed to register hotkey via D-Bus")

        # Try KDE KGlobalAccel (KDE Plasma/Wayland)
        elif de == DesktopEnvironment.KDE:
            success = self._register_kde(hotkey, callback)
            if success:
                print(f"Wayland (KDE): Registered hotkey via KGlobalAccel")
                return True
            else:
                print(f"Wayland (KDE): Failed to register hotkey via KGlobalAccel")

        # For compositor-based WMs, show manual setup instructions
        elif de in [DesktopEnvironment.SWAY, DesktopEnvironment.I3,
                    DesktopEnvironment.HYPRLAND]:
            self._show_setup_instructions(hotkey)
            print(f"Wayland ({de.value}): Manual hotkey setup required")
            return True  # Return True to indicate user action needed

        # Fallback: No support
        else:
            print(f"Wayland: Global hotkeys not supported on {de.value}")
            print(f"Wayland: Use system tray to activate recording")
            return False

    def _register_gnome(self, hotkey: str, callback: Callable[[], None]) -> bool:
        """
        Register hotkey via GNOME D-Bus.

        Note: This is a simplified implementation. Full implementation
        would require python-dbus and more complex D-Bus interaction.
        """
        # TODO: Implement GNOME D-Bus keybinding
        # This requires:
        # 1. Creating a custom keybinding in dconf
        # 2. Setting up D-Bus service to receive activation
        # 3. Calling callback when D-Bus signal received

        # For now, return False to indicate not implemented
        return False

    def _register_kde(self, hotkey: str, callback: Callable[[], None]) -> bool:
        """
        Register hotkey via KDE KGlobalAccel.

        Note: This is a simplified implementation. Full implementation
        would require KDE D-Bus interaction.
        """
        # TODO: Implement KDE KGlobalAccel registration
        # This requires:
        # 1. Registering application with KGlobalAccel via D-Bus
        # 2. Creating action and associating with hotkey
        # 3. Listening for activation signals

        # For now, return False to indicate not implemented
        return False

    def unregister(self, hotkey: str) -> bool:
        """
        Unregister a hotkey.

        Args:
            hotkey: Hotkey combination to unregister

        Returns:
            True if unregistration successful, False otherwise
        """
        if hotkey in self._registered_hotkeys:
            del self._registered_hotkeys[hotkey]

        if hotkey in self._callbacks:
            del self._callbacks[hotkey]

        print(f"Wayland: Unregistered hotkey {hotkey}")
        return True

    def start(self) -> None:
        """Start the hotkey listener (if supported)."""
        if self._is_running:
            return

        # For most Wayland compositors, there's no listener to start
        # Hotkeys are handled by the compositor itself
        self._is_running = True
        print("Wayland: Hotkey manager started (compositor-based)")

    def stop(self) -> None:
        """Stop the hotkey listener."""
        if not self._is_running:
            return

        self._is_running = False
        print("Wayland: Hotkey manager stopped")

    def is_supported(self) -> bool:
        """
        Check if global hotkeys are supported on current system.

        Returns:
            True if supported, False otherwise
        """
        de = self._detector.desktop_environment
        return de in [
            DesktopEnvironment.GNOME,
            DesktopEnvironment.KDE,
            DesktopEnvironment.SWAY,
            DesktopEnvironment.I3,
            DesktopEnvironment.HYPRLAND,
        ]

    def get_setup_instructions(self) -> Optional[str]:
        """
        Get setup instructions for manual hotkey configuration.

        Returns:
            Instructions string or None if not applicable
        """
        de = self._detector.desktop_environment

        if de == DesktopEnvironment.SWAY:
            return "Add 'bindsym Control+Super_L exec talky-toggle' to ~/.config/sway/config"
        elif de == DesktopEnvironment.HYPRLAND:
            return "Add 'bind = CTRL, SUPER, exec, talky-toggle' to ~/.config/hypr/hyprland.conf"
        elif de == DesktopEnvironment.I3:
            return "Add 'bindsym Control+Mod4 exec talky-toggle' to ~/.config/i3/config"
        elif de == DesktopEnvironment.GNOME:
            return "Configure in GNOME Settings > Keyboard > Custom Shortcuts"
        elif de == DesktopEnvironment.KDE:
            return "Configure in KDE System Settings > Shortcuts > Custom Shortcuts"
        else:
            return None
