"""System tray icon management."""

import logging
from typing import TYPE_CHECKING

import pystray
from pystray import MenuItem as Item

from .icons import IconGenerator
from .notifications import NotificationManager
from ..whisper.languages import (
    get_all_languages,
    get_popular_languages,
    get_language_name,
)

if TYPE_CHECKING:
    from ..main import TalkyApp

logger = logging.getLogger(__name__)


class TrayManager:
    """Manages system tray icon and menu."""

    def __init__(self, app: 'TalkyApp'):
        """
        Initialize tray manager.

        Args:
            app: TalkyApp instance
        """
        self.app = app
        self.icon = None
        self.is_running = False
        self._state = "idle"
        self.icon_generator = IconGenerator()
        self.notification_manager = NotificationManager()

        logger.info("Tray manager initialized")

    def set_state(self, state: str):
        """
        Update tray icon state.

        Args:
            state: One of "idle", "recording", "processing"
        """
        if state not in IconGenerator.COLORS:
            logger.warning(f"Invalid state: {state}")
            return

        self._state = state

        if self.icon:
            try:
                new_icon = self.icon_generator.create_icon(state)
                self.icon.icon = new_icon

                tooltip = f"Talky - {state.capitalize()}"
                self.icon.title = tooltip

                logger.debug(f"Tray state updated: {state}")
            except Exception as e:
                logger.error(f"Failed to update tray icon: {e}")

    def notify_transcription_complete(self, text: str):
        """
        Show notification for completed transcription.

        Args:
            text: Transcribed text
        """
        self.notification_manager.show_transcription_complete(text)

    def notify_error(self, error_msg: str, critical: bool = False):
        """
        Show error notification.

        Args:
            error_msg: Error message
            critical: Whether error is critical
        """
        urgency = "critical" if critical else "normal"
        self.notification_manager.show_error(error_msg, urgency=urgency)

    def notify_info(self, message: str):
        """
        Show informational notification.

        Args:
            message: Information message
        """
        self.notification_manager.show_info(message)

    def _create_menu(self) -> pystray.Menu:
        """
        Create tray menu.

        Returns:
            pystray.Menu instance
        """
        return pystray.Menu(
            Item(
                lambda: f"Talky - {self._state.capitalize()}",
                lambda: None,
                enabled=False
            ),
            Item.SEPARATOR,
            Item(
                "Language",
                pystray.Menu(
                    lambda: self._create_language_menu()
                )
            ),
            Item(
                "Settings",
                self._on_settings
            ),
            Item.SEPARATOR,
            Item(
                "About Talky",
                self._on_about
            ),
            Item(
                "Quit",
                self._on_quit
            )
        )

    def _create_language_menu(self):
        """Create language selection submenu."""
        current_lang = self.app.config.whisper.language or "auto"
        all_languages = get_all_languages()
        popular_langs = get_popular_languages()

        # Create menu items
        menu_items = []

        # Popular languages section
        menu_items.append(
            Item(
                "Popular Languages",
                lambda: None,
                enabled=False
            )
        )

        for lang_code in popular_langs:
            lang_name = all_languages[lang_code]
            is_current = (lang_code == current_lang)
            menu_items.append(
                Item(
                    lambda code=lang_code, name=lang_name: f"{'✓ ' if code == current_lang else '  '}{name}",
                    lambda icon, item, code=lang_code: self._on_language_select(code),
                    checked=lambda item, code=lang_code: code == current_lang
                )
            )

        menu_items.append(Item.SEPARATOR)
        menu_items.append(
            Item(
                "All Languages",
                lambda: None,
                enabled=False
            )
        )

        # All languages (sorted alphabetically)
        sorted_languages = sorted(
            [(code, name) for code, name in all_languages.items() if code not in popular_langs],
            key=lambda x: x[1]
        )

        for lang_code, lang_name in sorted_languages:
            is_current = (lang_code == current_lang)
            menu_items.append(
                Item(
                    lambda code=lang_code, name=lang_name: f"{'✓ ' if code == current_lang else '  '}{name}",
                    lambda icon, item, code=lang_code: self._on_language_select(code),
                    checked=lambda item, code=lang_code: code == current_lang
                )
            )

        return menu_items

    def _on_language_select(self, language_code: str):
        """
        Handle language selection.

        Args:
            language_code: Selected language code
        """
        try:
            # Update config
            self.app.config.whisper.language = None if language_code == "auto" else language_code

            # Save config
            self.app.config.save()

            # Update whisper engine
            if self.app.whisper_engine:
                self.app.whisper_engine.language = self.app.config.whisper.language

            # Show notification
            lang_name = get_language_name(language_code)
            self.notification_manager.show_info(f"Language changed to: {lang_name}")

            logger.info(f"Language changed to: {language_code}")

            # Recreate menu to update checkmarks
            if self.icon:
                self.icon.menu = self._create_menu()

        except Exception as e:
            logger.error(f"Failed to change language: {e}")
            self.notification_manager.show_error(f"Failed to change language: {e}")

    def _on_settings(self, icon, item):
        """Show settings dialog."""
        try:
            from .settings import SettingsDialog
            dialog = SettingsDialog(self.app)
            dialog.show()
        except ImportError:
            # Settings dialog not yet implemented
            self.notification_manager.show_info(
                "Settings: Edit ~/.config/talky/config.yaml\n"
                "Then restart Talky to apply changes."
            )
        except Exception as e:
            logger.error(f"Failed to open settings: {e}")
            self.notification_manager.show_error(f"Failed to open settings: {e}")

    def _on_about(self, icon, item):
        """Show about dialog."""
        try:
            from ..version import __version__
            version = __version__
        except ImportError:
            version = "unknown"

        # Get current language info
        current_lang = self.app.config.whisper.language or "auto"
        lang_name = get_language_name(current_lang)

        # Get current model info
        model_name = self.app.config.whisper.model

        about_text = (
            f"Talky v{version}\n\n"
            "System-wide dictation for Linux\n"
            "using OpenAI's Whisper AI\n\n"
            f"Model: {model_name}\n"
            f"Language: {lang_name}\n\n"
            "Push-to-talk: Hold Ctrl+Win, speak, release\n\n"
            "https://github.com/ChrisKalahiki/talky"
        )

        self.notification_manager.show(
            "About Talky",
            about_text,
            urgency="low",
            timeout=10000
        )

    def _on_quit(self, icon, item):
        """Quit application."""
        logger.info("Quit requested from tray")
        self.app.is_running = False
        if self.icon:
            self.icon.stop()

    def start(self):
        """Start system tray icon."""
        if self.is_running:
            logger.warning("Tray already running")
            return

        try:
            initial_icon = self.icon_generator.create_icon("idle")

            self.icon = pystray.Icon(
                "talky",
                initial_icon,
                "Talky - Idle",
                menu=self._create_menu()
            )

            logger.info("Starting system tray...")
            self.is_running = True

            self.icon.run_detached()

            logger.info("System tray started")

        except Exception as e:
            logger.error(f"Failed to start tray: {e}")
            self.is_running = False
            raise

    def stop(self):
        """Stop system tray icon."""
        if not self.is_running:
            return

        try:
            if self.icon:
                self.icon.stop()
                self.icon = None

            self.is_running = False
            logger.info("System tray stopped")

        except Exception as e:
            logger.error(f"Error stopping tray: {e}")
