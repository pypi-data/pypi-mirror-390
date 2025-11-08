"""Platform detection utilities for Linux display servers and desktop environments."""

import os
import subprocess
import shutil
from enum import Enum
from typing import Optional


class DisplayServer(Enum):
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


class DesktopEnvironment(Enum):
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    MATE = "mate"
    CINNAMON = "cinnamon"
    SWAY = "sway"
    I3 = "i3"
    HYPRLAND = "hyprland"
    OTHER = "other"
    UNKNOWN = "unknown"


class PlatformDetector:
    """Detect platform capabilities and available tools."""

    def __init__(self):
        self._display_server = None
        self._desktop_environment = None
        self._has_cuda = None

    @property
    def display_server(self) -> DisplayServer:
        """Detect the display server (X11 or Wayland)."""
        if self._display_server is None:
            self._display_server = self._detect_display_server()
        return self._display_server

    @property
    def desktop_environment(self) -> DesktopEnvironment:
        """Detect the desktop environment."""
        if self._desktop_environment is None:
            self._desktop_environment = self._detect_desktop_environment()
        return self._desktop_environment

    @property
    def is_x11(self) -> bool:
        """Check if running on X11."""
        return self.display_server == DisplayServer.X11

    @property
    def is_wayland(self) -> bool:
        """Check if running on Wayland."""
        return self.display_server == DisplayServer.WAYLAND

    @property
    def has_cuda(self) -> bool:
        """Check if NVIDIA CUDA is available."""
        if self._has_cuda is None:
            self._has_cuda = self._detect_cuda()
        return self._has_cuda

    def _detect_display_server(self) -> DisplayServer:
        """Detect display server from environment variables."""
        # Check XDG_SESSION_TYPE first (most reliable)
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session_type == "wayland":
            return DisplayServer.WAYLAND
        if session_type == "x11":
            return DisplayServer.X11

        # Check for Wayland display
        if os.environ.get("WAYLAND_DISPLAY"):
            return DisplayServer.WAYLAND

        # Check for X11 display
        if os.environ.get("DISPLAY"):
            return DisplayServer.X11

        return DisplayServer.UNKNOWN

    def _detect_desktop_environment(self) -> DesktopEnvironment:
        """Detect desktop environment from various environment variables."""
        # Check XDG_CURRENT_DESKTOP
        current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        desktop_session = os.environ.get("DESKTOP_SESSION", "").lower()

        # GNOME
        if "gnome" in current_desktop or "gnome" in desktop_session:
            return DesktopEnvironment.GNOME

        # KDE Plasma
        if "kde" in current_desktop or "plasma" in current_desktop:
            return DesktopEnvironment.KDE

        # XFCE
        if "xfce" in current_desktop or "xfce" in desktop_session:
            return DesktopEnvironment.XFCE

        # MATE
        if "mate" in current_desktop or "mate" in desktop_session:
            return DesktopEnvironment.MATE

        # Cinnamon
        if "cinnamon" in current_desktop or "cinnamon" in desktop_session:
            return DesktopEnvironment.CINNAMON

        # Sway (check process list)
        if self._is_process_running("sway"):
            return DesktopEnvironment.SWAY

        # i3
        if "i3" in current_desktop or self._is_process_running("i3"):
            return DesktopEnvironment.I3

        # Hyprland
        if "hyprland" in current_desktop or self._is_process_running("Hyprland"):
            return DesktopEnvironment.HYPRLAND

        # If we detected something but don't recognize it
        if current_desktop:
            return DesktopEnvironment.OTHER

        return DesktopEnvironment.UNKNOWN

    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running."""
        try:
            result = subprocess.run(
                ["pgrep", "-x", process_name],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _detect_cuda(self) -> bool:
        """Check if NVIDIA CUDA is available."""
        # Check for nvidia-smi
        if not shutil.which("nvidia-smi"):
            return False

        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=2,
                text=True
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def has_tool(self, tool_name: str) -> bool:
        """Check if a command-line tool is available."""
        return shutil.which(tool_name) is not None

    def check_audio_backend(self) -> str:
        """Detect available audio backend."""
        if self.has_tool("pw-cli"):
            return "pipewire"
        elif self.has_tool("pactl"):
            return "pulseaudio"
        else:
            return "alsa"

    def check_text_injection_tools(self) -> dict:
        """Check availability of text injection tools."""
        return {
            "xdotool": self.has_tool("xdotool"),
            "ydotool": self.has_tool("ydotool"),
        }

    def get_recommended_text_injector(self) -> str:
        """Get recommended text injection method for current platform."""
        tools = self.check_text_injection_tools()

        if self.is_x11:
            return "xdotool" if tools["xdotool"] else "clipboard"
        else:  # Wayland
            return "ydotool" if tools["ydotool"] else "clipboard"

    def get_platform_summary(self) -> dict:
        """Get a summary of platform capabilities."""
        return {
            "display_server": self.display_server.value,
            "desktop_environment": self.desktop_environment.value,
            "has_cuda": self.has_cuda,
            "audio_backend": self.check_audio_backend(),
            "text_injection": self.check_text_injection_tools(),
            "recommended_injector": self.get_recommended_text_injector(),
        }


# Global instance
_detector = None


def get_platform_detector() -> PlatformDetector:
    """Get the global platform detector instance."""
    global _detector
    if _detector is None:
        _detector = PlatformDetector()
    return _detector
