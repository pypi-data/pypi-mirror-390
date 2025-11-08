"""Autostart management for Talky using XDG Autostart standard."""

import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AutostartManager:
    """Manages XDG autostart configuration for Talky."""

    AUTOSTART_DIR = Path.home() / ".config" / "autostart"
    DESKTOP_FILE_NAME = "talky.desktop"

    DESKTOP_TEMPLATE = """[Desktop Entry]
Type=Application
Version=1.0
Name=Talky
GenericName=System Dictation
Comment=System-wide dictation using OpenAI Whisper
Exec={exec_path}
Icon=talky
Terminal=false
Categories=Utility;AudioVideo;Audio;Accessibility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay={delay}
X-KDE-autostart-after=panel
Hidden=false

# Managed by Talky autostart system
# Use 'talky --enable-autostart' or 'talky --disable-autostart' to manage
"""

    def __init__(self):
        """Initialize autostart manager."""
        self.desktop_file_path = self.AUTOSTART_DIR / self.DESKTOP_FILE_NAME

    @staticmethod
    def get_executable_path() -> Optional[str]:
        """
        Get the path to the Talky executable.

        Returns:
            Full path to talky executable, or None if not found
        """
        talky_path = shutil.which('talky')
        if talky_path:
            return talky_path

        if getattr(sys, 'frozen', False):
            return sys.executable

        python_exe = sys.executable
        return f"{python_exe} -m talky.main"

    def _create_desktop_file_content(self, delay_seconds: int = 5) -> str:
        """
        Create .desktop file content.

        Args:
            delay_seconds: Startup delay in seconds

        Returns:
            Desktop file content as string
        """
        exec_path = self.get_executable_path()
        if not exec_path:
            raise RuntimeError("Could not determine Talky executable path")

        return self.DESKTOP_TEMPLATE.format(
            exec_path=exec_path,
            delay=delay_seconds
        )

    def enable(self, delay_seconds: int = 5) -> bool:
        """
        Enable autostart by creating .desktop file.

        Args:
            delay_seconds: Startup delay in seconds (default: 5)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)

            desktop_content = self._create_desktop_file_content(delay_seconds)

            self.desktop_file_path.write_text(desktop_content)
            self.desktop_file_path.chmod(0o644)

            logger.info(f"Autostart enabled: {self.desktop_file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable autostart: {e}")
            return False

    def disable(self) -> bool:
        """
        Disable autostart by removing .desktop file.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.desktop_file_path.exists():
                self.desktop_file_path.unlink()
                logger.info(f"Autostart disabled: {self.desktop_file_path}")
            else:
                logger.debug("Autostart already disabled (no .desktop file)")

            return True

        except Exception as e:
            logger.error(f"Failed to disable autostart: {e}")
            return False

    def is_enabled(self) -> bool:
        """
        Check if autostart is currently enabled.

        Returns:
            True if .desktop file exists and is not hidden
        """
        if not self.desktop_file_path.exists():
            return False

        try:
            content = self.desktop_file_path.read_text()
            return "Hidden=false" in content or "Hidden=true" not in content
        except Exception as e:
            logger.error(f"Error checking autostart status: {e}")
            return False

    def get_status(self) -> dict:
        """
        Get detailed autostart status.

        Returns:
            Dict with status information:
                - enabled: bool
                - desktop_file: Path or None
                - executable: str or None
                - exists: bool
        """
        enabled = self.is_enabled()
        exec_path = self.get_executable_path()

        return {
            "enabled": enabled,
            "desktop_file": str(self.desktop_file_path) if self.desktop_file_path.exists() else None,
            "executable": exec_path,
            "exists": self.desktop_file_path.exists()
        }

    def sync_with_config(self, autostart_config) -> bool:
        """
        Synchronize .desktop file with configuration.

        Args:
            autostart_config: AutostartConfig object from config.yaml

        Returns:
            True if sync successful
        """
        try:
            if autostart_config.enabled:
                if not self.is_enabled():
                    logger.info("Config has autostart enabled, creating .desktop file")
                    return self.enable(delay_seconds=autostart_config.delay_seconds)
                else:
                    current_content = self.desktop_file_path.read_text()
                    new_content = self._create_desktop_file_content(
                        delay_seconds=autostart_config.delay_seconds
                    )

                    if current_content.strip() != new_content.strip():
                        logger.info("Updating .desktop file to match current config")
                        return self.enable(delay_seconds=autostart_config.delay_seconds)

            else:
                if self.is_enabled():
                    logger.info("Config has autostart disabled, removing .desktop file")
                    return self.disable()

            return True

        except Exception as e:
            logger.error(f"Failed to sync autostart with config: {e}")
            return False
