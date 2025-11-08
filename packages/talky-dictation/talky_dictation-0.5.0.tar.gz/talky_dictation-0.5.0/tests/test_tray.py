#!/usr/bin/env python3
"""Unit tests for system tray components."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from talky.ui.icons import IconGenerator


class TestIconGenerator(unittest.TestCase):
    """Test icon generation."""

    def test_create_idle_icon(self):
        """Test creating idle state icon."""
        icon = IconGenerator.create_icon("idle")
        self.assertIsNotNone(icon)
        self.assertEqual(icon.size, (64, 64))
        self.assertEqual(icon.mode, "RGBA")

    def test_create_recording_icon(self):
        """Test creating recording state icon."""
        icon = IconGenerator.create_icon("recording")
        self.assertIsNotNone(icon)
        self.assertEqual(icon.size, (64, 64))
        self.assertEqual(icon.mode, "RGBA")

    def test_create_processing_icon(self):
        """Test creating processing state icon."""
        icon = IconGenerator.create_icon("processing")
        self.assertIsNotNone(icon)
        self.assertEqual(icon.size, (64, 64))
        self.assertEqual(icon.mode, "RGBA")

    def test_custom_size(self):
        """Test creating icon with custom size."""
        icon = IconGenerator.create_icon("idle", size=(32, 32))
        self.assertEqual(icon.size, (32, 32))

    def test_invalid_state(self):
        """Test that invalid state raises ValueError."""
        with self.assertRaises(ValueError):
            IconGenerator.create_icon("invalid_state")

    def test_all_colors_defined(self):
        """Test that all states have colors defined."""
        self.assertIn("idle", IconGenerator.COLORS)
        self.assertIn("recording", IconGenerator.COLORS)
        self.assertIn("processing", IconGenerator.COLORS)


class TestNotificationManager(unittest.TestCase):
    """Test notification manager."""

    def setUp(self):
        """Set up test fixtures."""
        from talky.ui.notifications import NotificationManager
        self.manager = NotificationManager()

    def test_initialization(self):
        """Test notification manager initialization."""
        self.assertEqual(self.manager.app_name, "Talky")

    def test_show_notification_with_unavailable_notify2(self):
        """Test notification when notify2 is unavailable."""
        if not self.manager.is_available:
            result = self.manager.show("Test", "Message")
            self.assertFalse(result)

    def test_show_transcription_complete(self):
        """Test transcription complete notification."""
        text = "This is a test transcription"
        result = self.manager.show_transcription_complete(text)
        self.assertIsInstance(result, bool)

    def test_show_transcription_complete_long_text(self):
        """Test transcription with text longer than preview."""
        text = "A" * 100
        result = self.manager.show_transcription_complete(text)
        self.assertIsInstance(result, bool)

    def test_show_error(self):
        """Test error notification."""
        result = self.manager.show_error("Test error")
        self.assertIsInstance(result, bool)

    def test_show_info(self):
        """Test info notification."""
        result = self.manager.show_info("Test info")
        self.assertIsInstance(result, bool)


class TestTrayManagerBasics(unittest.TestCase):
    """Test basic tray manager functionality (no actual tray creation)."""

    def test_import(self):
        """Test that TrayManager can be imported."""
        from talky.ui import TrayManager
        self.assertIsNotNone(TrayManager)

    def test_icon_generator_import(self):
        """Test that IconGenerator can be imported from ui package."""
        from talky.ui import IconGenerator
        self.assertIsNotNone(IconGenerator)

    def test_notification_manager_import(self):
        """Test that NotificationManager can be imported from ui package."""
        from talky.ui import NotificationManager
        self.assertIsNotNone(NotificationManager)


def main():
    """Run tests."""
    print("\n" + "=" * 60)
    print("SYSTEM TRAY UNIT TESTS")
    print("=" * 60 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestIconGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTrayManagerBasics))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ ALL TRAY TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60 + "\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
