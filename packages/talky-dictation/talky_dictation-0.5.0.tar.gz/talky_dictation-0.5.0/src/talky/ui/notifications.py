"""Desktop notification management."""

import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages desktop notifications using notify2."""

    def __init__(self, app_name: str = "Talky"):
        """
        Initialize notification manager.

        Args:
            app_name: Application name for notifications
        """
        self.app_name = app_name
        self._available = False
        self._init_notify2()

    def _init_notify2(self):
        """Initialize notify2 library."""
        try:
            import notify2
            if notify2.init(self.app_name):
                self._available = True
                logger.info("Desktop notifications initialized")
            else:
                logger.warning("Failed to initialize notify2")
        except ImportError:
            logger.warning("notify2 not available - notifications disabled")
        except Exception as e:
            logger.warning(f"Failed to initialize notifications: {e}")

    @property
    def is_available(self) -> bool:
        """Check if notifications are available."""
        return self._available

    def show(self, title: str, message: str, urgency: str = "normal", timeout: int = 3000):
        """
        Show desktop notification.

        Args:
            title: Notification title
            message: Notification message
            urgency: "low", "normal", or "critical"
            timeout: Timeout in milliseconds (default 3000)

        Returns:
            True if notification was shown, False otherwise
        """
        if not self._available:
            return False

        try:
            import notify2

            urgency_map = {
                "low": notify2.URGENCY_LOW,
                "normal": notify2.URGENCY_NORMAL,
                "critical": notify2.URGENCY_CRITICAL
            }

            notification = notify2.Notification(title, message)
            notification.set_urgency(urgency_map.get(urgency, notify2.URGENCY_NORMAL))
            notification.set_timeout(timeout)
            notification.show()
            return True

        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
            return False

    def show_transcription_complete(self, text: str, max_preview_length: int = 50) -> bool:
        """
        Show notification for completed transcription.

        Args:
            text: Transcribed text
            max_preview_length: Maximum characters to show in preview

        Returns:
            True if notification was shown
        """
        if not text:
            return self.show(
                "Talky",
                "No speech detected",
                urgency="low"
            )

        preview = text[:max_preview_length]
        if len(text) > max_preview_length:
            preview += "..."

        return self.show(
            "Transcription Complete",
            preview,
            urgency="normal"
        )

    def show_error(self, error_msg: str, urgency: str = "normal") -> bool:
        """
        Show error notification.

        Args:
            error_msg: Error message to display
            urgency: "normal" or "critical"

        Returns:
            True if notification was shown
        """
        return self.show(
            "Talky Error",
            error_msg,
            urgency=urgency,
            timeout=5000
        )

    def show_info(self, message: str) -> bool:
        """
        Show informational notification.

        Args:
            message: Information message

        Returns:
            True if notification was shown
        """
        return self.show(
            "Talky",
            message,
            urgency="low"
        )
