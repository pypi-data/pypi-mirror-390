"""User interface components (system tray, notifications)."""

from .tray import TrayManager
from .notifications import NotificationManager
from .icons import IconGenerator
from .settings import SettingsDialog
from .setup_wizard import SetupWizard
from .wayland_setup import WaylandSetupChecker

__all__ = [
    'TrayManager',
    'NotificationManager',
    'IconGenerator',
    'SettingsDialog',
    'SetupWizard',
    'WaylandSetupChecker',
]
