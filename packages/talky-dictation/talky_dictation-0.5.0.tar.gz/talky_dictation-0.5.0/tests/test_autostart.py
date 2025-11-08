#!/usr/bin/env python3
"""Unit tests for autostart functionality."""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from talky.autostart import AutostartManager
from talky.utils.config import Config, AutostartConfig


class TestAutostartManager(unittest.TestCase):
    """Test autostart manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.autostart_dir = Path(self.temp_dir) / "autostart"
        self.autostart_dir.mkdir(parents=True, exist_ok=True)

        self.manager = AutostartManager()
        self.original_autostart_dir = AutostartManager.AUTOSTART_DIR
        AutostartManager.AUTOSTART_DIR = self.autostart_dir
        self.manager.desktop_file_path = self.autostart_dir / AutostartManager.DESKTOP_FILE_NAME

    def tearDown(self):
        """Clean up test fixtures."""
        AutostartManager.AUTOSTART_DIR = self.original_autostart_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_executable_path(self):
        """Test getting executable path."""
        exec_path = AutostartManager.get_executable_path()
        self.assertIsNotNone(exec_path)
        self.assertTrue(len(exec_path) > 0)

    def test_enable_autostart(self):
        """Test enabling autostart."""
        success = self.manager.enable()
        self.assertTrue(success)
        self.assertTrue(self.manager.desktop_file_path.exists())

        content = self.manager.desktop_file_path.read_text()
        self.assertIn("[Desktop Entry]", content)
        self.assertIn("Type=Application", content)
        self.assertIn("Name=Talky", content)
        self.assertIn("Hidden=false", content)

    def test_enable_with_custom_delay(self):
        """Test enabling with custom delay."""
        success = self.manager.enable(delay_seconds=10)
        self.assertTrue(success)

        content = self.manager.desktop_file_path.read_text()
        self.assertIn("X-GNOME-Autostart-Delay=10", content)

    def test_disable_autostart(self):
        """Test disabling autostart."""
        self.manager.enable()
        self.assertTrue(self.manager.desktop_file_path.exists())

        success = self.manager.disable()
        self.assertTrue(success)
        self.assertFalse(self.manager.desktop_file_path.exists())

    def test_disable_when_not_enabled(self):
        """Test disabling when not already enabled."""
        success = self.manager.disable()
        self.assertTrue(success)

    def test_is_enabled_when_enabled(self):
        """Test is_enabled returns True when enabled."""
        self.manager.enable()
        self.assertTrue(self.manager.is_enabled())

    def test_is_enabled_when_disabled(self):
        """Test is_enabled returns False when disabled."""
        self.assertFalse(self.manager.is_enabled())

    def test_get_status_enabled(self):
        """Test get_status when enabled."""
        self.manager.enable()
        status = self.manager.get_status()

        self.assertTrue(status["enabled"])
        self.assertEqual(status["desktop_file"], str(self.manager.desktop_file_path))
        self.assertIsNotNone(status["executable"])
        self.assertTrue(status["exists"])

    def test_get_status_disabled(self):
        """Test get_status when disabled."""
        status = self.manager.get_status()

        self.assertFalse(status["enabled"])
        self.assertIsNone(status["desktop_file"])
        self.assertIsNotNone(status["executable"])
        self.assertFalse(status["exists"])

    def test_sync_with_config_enable(self):
        """Test syncing when config says enabled."""
        config = AutostartConfig(enabled=True, delay_seconds=5)

        success = self.manager.sync_with_config(config)
        self.assertTrue(success)
        self.assertTrue(self.manager.is_enabled())

    def test_sync_with_config_disable(self):
        """Test syncing when config says disabled."""
        self.manager.enable()

        config = AutostartConfig(enabled=False, delay_seconds=5)
        success = self.manager.sync_with_config(config)

        self.assertTrue(success)
        self.assertFalse(self.manager.is_enabled())

    def test_sync_updates_delay(self):
        """Test sync updates delay when changed."""
        self.manager.enable(delay_seconds=5)

        config = AutostartConfig(enabled=True, delay_seconds=10)
        self.manager.sync_with_config(config)

        content = self.manager.desktop_file_path.read_text()
        self.assertIn("X-GNOME-Autostart-Delay=10", content)

    def test_sync_idempotent(self):
        """Test sync is idempotent."""
        config = AutostartConfig(enabled=True, delay_seconds=5)

        self.manager.sync_with_config(config)
        first_mtime = self.manager.desktop_file_path.stat().st_mtime

        self.manager.sync_with_config(config)
        second_mtime = self.manager.desktop_file_path.stat().st_mtime

        self.assertGreaterEqual(second_mtime, first_mtime)

    def test_file_permissions(self):
        """Test desktop file has correct permissions."""
        self.manager.enable()

        mode = self.manager.desktop_file_path.stat().st_mode
        self.assertEqual(oct(mode)[-3:], '644')


class TestConfigIntegration(unittest.TestCase):
    """Test autostart config integration."""

    def test_default_config_has_autostart(self):
        """Test default config includes autostart section."""
        config = Config()
        self.assertIsNotNone(config.autostart)
        self.assertFalse(config.autostart.enabled)
        self.assertEqual(config.autostart.delay_seconds, 5)

    def test_config_to_dict_includes_autostart(self):
        """Test config serialization includes autostart."""
        config = Config()
        data = config.to_dict()

        self.assertIn("autostart", data)
        self.assertIn("enabled", data["autostart"])
        self.assertIn("delay_seconds", data["autostart"])

    def test_config_from_dict_with_autostart(self):
        """Test config deserialization with autostart."""
        data = {
            "autostart": {
                "enabled": True,
                "delay_seconds": 10
            }
        }

        config = Config.from_dict(data)
        self.assertTrue(config.autostart.enabled)
        self.assertEqual(config.autostart.delay_seconds, 10)

    def test_config_from_dict_without_autostart(self):
        """Test config deserialization without autostart (uses defaults)."""
        data = {}
        config = Config.from_dict(data)

        self.assertFalse(config.autostart.enabled)
        self.assertEqual(config.autostart.delay_seconds, 5)


def main():
    """Run tests."""
    print("\n" + "=" * 60)
    print("AUTOSTART UNIT TESTS")
    print("=" * 60 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAutostartManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ ALL AUTOSTART TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60 + "\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
