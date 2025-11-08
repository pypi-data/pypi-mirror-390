#!/usr/bin/env python3
"""Main Talky application."""

import sys
import time
from pathlib import Path
import os

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        if os.getenv("HF_TOKEN"):
            print(f"✓ Loaded HF_TOKEN from .env")
except ImportError:
    pass  # python-dotenv not installed, continue without it

from .utils.config import Config
from .utils.platform import get_platform_detector
from .audio import SoundDeviceCapture
from .whisper import create_whisper_engine
from .input import create_text_injector
from .hotkeys import create_hotkey_manager


class TalkyApp:
    """Main Talky application class."""

    def __init__(self, config_path: Path = None, enable_tray: bool = True):
        """
        Initialize Talky application.

        Args:
            config_path: Path to configuration file
            enable_tray: Whether to enable system tray (default: True)
        """
        # Load configuration
        self.config = Config.load(config_path)

        # Platform detection
        self.platform = get_platform_detector()
        print(f"Platform: {self.platform.display_server.value} / {self.platform.desktop_environment.value}")

        # Initialize components
        self.audio_capture = None
        self.whisper_engine = None
        self.text_injector = None
        self.hotkey_manager = None
        self.tray_manager = None

        # Configuration
        self.enable_tray = enable_tray

        # State
        self.is_recording = False
        self.is_running = False

    def initialize(self) -> bool:
        """
        Initialize all components.

        Returns:
            True if successful, False otherwise
        """
        print("\nInitializing Talky...")

        # Initialize audio capture
        print("  Audio capture...", end=" ")
        try:
            self.audio_capture = SoundDeviceCapture(
                sample_rate=self.config.audio.sample_rate,
                channels=self.config.audio.channels,
                buffer_size=self.config.audio.buffer_size
            )
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

        # Initialize Whisper engine
        print("  Whisper engine...", end=" ")
        try:
            self.whisper_engine = create_whisper_engine(
                model_name=self.config.whisper.model,
                language=self.config.whisper.language,
                device=self.config.whisper.device,
                compute_type=self.config.whisper.compute_type
            )
            if not self.whisper_engine:
                print("✗ Failed to create engine")
                return False

            # Load model
            if not self.whisper_engine.load_model():
                print("✗ Failed to load model")
                return False

            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

        # Initialize text injector
        print("  Text injector...", end=" ")
        try:
            self.text_injector = create_text_injector(
                typing_delay_ms=self.config.platform.typing_delay_ms,
                prefer_method=self.config.platform.prefer_method
            )
            if not self.text_injector:
                print("✗ No injection method available")
                return False
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

        # Initialize hotkey manager
        print("  Hotkey manager...", end=" ")
        try:
            self.hotkey_manager = create_hotkey_manager()
            if not self.hotkey_manager:
                print("✗ Not available")
                return False
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

        # Initialize system tray (optional)
        if self.enable_tray:
            print("  System tray...", end=" ")
            try:
                from .ui import TrayManager
                self.tray_manager = TrayManager(self)
                print("✓")
            except Exception as e:
                print(f"⚠️  Tray unavailable: {e} (continuing without tray)")
                self.enable_tray = False

        print("\n✓ All components initialized")
        return True

    def start_recording(self):
        """Start recording audio (called on hotkey press)."""
        if self.is_recording:
            return

        try:
            print("\n🎤 Recording... (hold hotkey and speak)")
            self.audio_capture.clear_buffer()
            self.audio_capture.start()
            self.is_recording = True

            # Notify tray
            if self.tray_manager:
                self.tray_manager.set_state("recording")

        except Exception as e:
            print(f"Error starting recording: {e}")
            if self.tray_manager:
                self.tray_manager.notify_error(f"Recording error: {e}")

    def stop_recording(self):
        """Stop recording and transcribe (called on hotkey release)."""
        if not self.is_recording:
            return

        try:
            # Stop recording
            self.audio_capture.stop()
            self.is_recording = False
            print("⏹️  Recording stopped (hotkey released)")

            # Get audio data
            audio_data = self.audio_capture.get_audio_data()

            if audio_data is None or len(audio_data) == 0:
                print("⚠️  No audio captured")
                if self.tray_manager:
                    self.tray_manager.set_state("idle")
                return

            duration = len(audio_data) / self.config.audio.sample_rate
            print(f"🔄 Transcribing {duration:.1f}s of audio...")

            # Notify tray
            if self.tray_manager:
                self.tray_manager.set_state("processing")

            # Transcribe
            start_time = time.time()
            result = self.whisper_engine.transcribe(audio_data)
            elapsed = time.time() - start_time

            # Check for errors
            if result.get("error"):
                error_msg = result['error']
                print(f"✗ Transcription error: {error_msg}")
                if self.tray_manager:
                    self.tray_manager.set_state("idle")
                    self.tray_manager.notify_error(f"Transcription error: {error_msg}")
                return

            # Get transcribed text
            text = result.get("text", "").strip()

            if not text:
                print("⚠️  No speech detected")
                if self.tray_manager:
                    self.tray_manager.set_state("idle")
                return

            print(f"✓ Transcribed in {elapsed:.2f}s: \"{text}\"")

            # Inject text
            print("⌨️  Injecting text...")
            success = self.text_injector.inject_text(text)

            if success:
                print("✓ Text injected successfully\n")
                if self.tray_manager:
                    self.tray_manager.set_state("idle")
                    self.tray_manager.notify_transcription_complete(text)
            else:
                print("✗ Text injection failed\n")
                if self.tray_manager:
                    self.tray_manager.set_state("idle")
                    self.tray_manager.notify_error("Text injection failed")

        except Exception as e:
            print(f"Error during transcription: {e}")
            self.is_recording = False
            if self.tray_manager:
                self.tray_manager.set_state("idle")
                self.tray_manager.notify_error(f"Error: {e}")

    def run(self) -> int:
        """
        Run the Talky application.

        Returns:
            Exit code
        """
        # Initialize components
        if not self.initialize():
            print("\n✗ Initialization failed")
            return 1

        # Sync autostart with config
        try:
            from .autostart import AutostartManager
            autostart_manager = AutostartManager()
            autostart_manager.sync_with_config(self.config.autostart)
        except Exception as e:
            print(f"⚠️  Autostart sync failed: {e}")

        # Register hotkey (push-to-talk mode)
        hotkey = self.config.hotkeys.toggle_recording
        print(f"\nRegistering hotkey: {hotkey} (push-to-talk mode)")

        success = self.hotkey_manager.register(
            hotkey,
            on_press=self.start_recording,
            on_release=self.stop_recording
        )

        if not success:
            print(f"✗ Failed to register hotkey")
            if hasattr(self.hotkey_manager, 'get_setup_instructions'):
                instructions = self.hotkey_manager.get_setup_instructions()
                if instructions:
                    print(f"\n⚠️  Setup Required:")
                    print(f"   {instructions}")
            return 1

        print("✓ Hotkey registered")

        # Start system tray
        if self.tray_manager:
            try:
                self.tray_manager.start()
                print("✓ System tray started")
            except Exception as e:
                print(f"⚠️  Tray failed to start: {e} (continuing without tray)")
                self.enable_tray = False

        # Start hotkey listener
        try:
            self.hotkey_manager.start()
            print("\n" + "=" * 60)
            print("✓ Talky is running! (Push-to-Talk Mode)")
            print("=" * 60)
            print(f"\n📝 Usage:")
            print(f"   1. Hold down {hotkey}")
            print(f"   2. Speak while holding")
            print(f"   3. Release when done")
            print(f"   4. Text will be transcribed and inserted!\n")
            print(f"Press Ctrl+C to exit\n")

            self.is_running = True

            # Main loop
            while self.is_running:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nShutting down...")
        finally:
            self.shutdown()

        return 0

    def shutdown(self):
        """Shutdown the application."""
        print("Cleaning up...")

        # Stop system tray
        if self.tray_manager:
            self.tray_manager.stop()

        # Stop hotkey manager
        if self.hotkey_manager:
            self.hotkey_manager.stop()

        # Stop recording if active
        if self.is_recording:
            self.audio_capture.stop()

        # Unload model
        if self.whisper_engine:
            self.whisper_engine.unload_model()

        self.is_running = False
        print("✓ Goodbye!")


def main():
    """Main entry point."""
    import argparse

    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 25 + "TALKY" + " " * 28 + "║")
    print("║" + " " * 15 + "System-Wide Dictation" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")

    parser = argparse.ArgumentParser(
        description="Talky - System-wide dictation for Linux using Whisper AI"
    )
    parser.add_argument(
        "--no-tray",
        action="store_true",
        help="Disable system tray (run in headless CLI mode)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )

    autostart_group = parser.add_mutually_exclusive_group()
    autostart_group.add_argument(
        "--enable-autostart",
        action="store_true",
        help="Enable Talky to start automatically on login"
    )
    autostart_group.add_argument(
        "--disable-autostart",
        action="store_true",
        help="Disable autostart on login"
    )
    parser.add_argument(
        "--autostart-status",
        action="store_true",
        help="Show current autostart status"
    )
    parser.add_argument(
        "--wayland-setup",
        action="store_true",
        help="Check Wayland setup status and show issues"
    )
    parser.add_argument(
        "--wayland-setup-guide",
        action="store_true",
        help="Show complete Wayland setup guide"
    )
    parser.add_argument(
        "--skip-setup-wizard",
        action="store_true",
        help="Skip first-run setup wizard"
    )

    args = parser.parse_args()

    # Handle Wayland setup commands
    if args.wayland_setup or args.wayland_setup_guide:
        from .ui import WaylandSetupChecker
        checker = WaylandSetupChecker()

        if args.wayland_setup:
            checker.print_status_report()
        elif args.wayland_setup_guide:
            print(checker.get_setup_guide())

        return 0

    # Handle autostart commands (don't start app, just configure and exit)
    if args.enable_autostart or args.disable_autostart or args.autostart_status:
        from .autostart import AutostartManager
        manager = AutostartManager()

        if args.enable_autostart:
            print("Enabling autostart...")
            if manager.enable():
                print("✓ Autostart enabled. Talky will launch on next login.")
                print(f"  Desktop file: {manager.desktop_file_path}")
                return 0
            else:
                print("✗ Failed to enable autostart")
                return 1

        elif args.disable_autostart:
            print("Disabling autostart...")
            if manager.disable():
                print("✓ Autostart disabled")
                return 0
            else:
                print("✗ Failed to disable autostart")
                return 1

        elif args.autostart_status:
            status = manager.get_status()
            print("\nAutostart Status:")
            print("=" * 60)
            if status["enabled"]:
                print("Status: ✓ Enabled")
                print(f"Desktop file: {status['desktop_file']}")
                print(f"Executable: {status['executable']}")
            else:
                if status["exists"]:
                    print("Status: Disabled (desktop file exists but hidden)")
                else:
                    print("Status: ✗ Disabled")
                print(f"To enable: talky --enable-autostart")
            print("=" * 60)
            return 0

    # Check if first-run setup wizard should be shown
    if not args.skip_setup_wizard:
        from .ui import SetupWizard
        if SetupWizard.should_show(args.config):
            print("\n" + "=" * 60)
            print("First-run setup detected. Opening setup wizard...")
            print("=" * 60 + "\n")

            # Create temporary app instance for wizard
            temp_app = TalkyApp(
                config_path=args.config,
                enable_tray=False
            )

            wizard = SetupWizard(temp_app)
            if not wizard.show():
                print("\nSetup cancelled. Run 'talky' again to retry.")
                return 1

            print("\n" + "=" * 60)
            print("Setup complete! Starting Talky...")
            print("=" * 60 + "\n")

    app = TalkyApp(
        config_path=args.config,
        enable_tray=not args.no_tray
    )
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
