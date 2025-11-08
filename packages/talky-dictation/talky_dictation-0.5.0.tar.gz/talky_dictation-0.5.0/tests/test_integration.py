#!/usr/bin/env python3
"""Comprehensive non-interactive integration test for Talky."""

import sys
import time
import numpy as np
sys.path.insert(0, 'src')

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("✓ Loaded .env file")
except ImportError:
    pass

from talky.utils.platform import get_platform_detector
from talky.utils.config import Config
from talky.audio import SoundDeviceCapture
from talky.whisper import create_whisper_engine
from talky.input import create_text_injector
from talky.hotkeys import create_hotkey_manager


class TestResults:
    """Track test results."""
    def __init__(self):
        self.tests = {}

    def record(self, test_name, passed, message=""):
        self.tests[test_name] = {"passed": passed, "message": message}

    def summary(self):
        total = len(self.tests)
        passed = sum(1 for t in self.tests.values() if t["passed"])
        return f"{passed}/{total} tests passed"

    def all_passed(self):
        return all(t["passed"] for t in self.tests.values())


def test_configuration():
    """Test configuration loading."""
    print("=" * 60)
    print("TEST: Configuration")
    print("=" * 60)

    try:
        config = Config.load()
        print(f"✓ Config loaded")
        print(f"  Model: {config.whisper.model}")
        print(f"  Language: {config.whisper.language}")
        print(f"  Hotkey: {config.hotkeys.toggle_recording}")
        print(f"  Device: {config.whisper.device}")
        return True, "Config loaded successfully"
    except Exception as e:
        print(f"✗ Config failed: {e}")
        return False, str(e)


def test_platform_detection():
    """Test platform detection."""
    print("\n" + "=" * 60)
    print("TEST: Platform Detection")
    print("=" * 60)

    try:
        detector = get_platform_detector()
        summary = detector.get_platform_summary()

        print(f"✓ Platform detected")
        print(f"  Display: {summary['display_server']}")
        print(f"  DE: {summary['desktop_environment']}")
        print(f"  CUDA: {summary['has_cuda']}")
        print(f"  Audio: {summary['audio_backend']}")
        print(f"  Injector: {summary['recommended_injector']}")

        return True, f"{summary['display_server']} detected"
    except Exception as e:
        print(f"✗ Platform detection failed: {e}")
        return False, str(e)


def test_audio_capture():
    """Test audio capture."""
    print("\n" + "=" * 60)
    print("TEST: Audio Capture")
    print("=" * 60)

    try:
        capture = SoundDeviceCapture(sample_rate=16000, channels=1)
        print(f"✓ Audio capture initialized")

        # Start and immediately stop
        capture.start()
        time.sleep(0.1)
        capture.stop()

        print(f"✓ Start/stop cycle successful")
        return True, "Audio capture working"
    except Exception as e:
        print(f"✗ Audio capture failed: {e}")
        return False, str(e)


def test_whisper_engine():
    """Test Whisper engine."""
    print("\n" + "=" * 60)
    print("TEST: Whisper Engine")
    print("=" * 60)

    try:
        print("Creating engine (base model)...")
        engine = create_whisper_engine(
            model_name="base",
            language="en",
            device="auto"
        )

        if not engine:
            return False, "Failed to create engine"

        print("✓ Engine created")

        print("Loading model (may take time on first run)...")
        if not engine.load_model():
            return False, "Failed to load model"

        print("✓ Model loaded")

        info = engine.get_model_info()
        print(f"  Device: {info['device']}")
        print(f"  Compute: {info['compute_type']}")

        # Test with synthetic audio
        print("\nTesting transcription with synthetic audio...")
        audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
        result = engine.transcribe(audio)

        print(f"✓ Transcription successful")
        print(f"  Result: {result.get('text', '(silence)'[:20])}")

        return True, f"Whisper on {info['device']}"
    except Exception as e:
        print(f"✗ Whisper failed: {e}")
        return False, str(e)


def test_text_injector():
    """Test text injector."""
    print("\n" + "=" * 60)
    print("TEST: Text Injector")
    print("=" * 60)

    try:
        injector = create_text_injector()

        if not injector:
            return False, "No injector available"

        print(f"✓ Text injector created")

        if hasattr(injector, 'get_active_method'):
            method = injector.get_active_method()
            print(f"  Method: {method}")

        print(f"  Available: {injector.is_available}")

        # Don't actually inject text in automated test
        print(f"✓ Injector ready (not testing actual injection)")

        return True, "Text injector ready"
    except Exception as e:
        print(f"✗ Text injector failed: {e}")
        return False, str(e)


def test_hotkey_manager():
    """Test hotkey manager with push-to-talk."""
    print("\n" + "=" * 60)
    print("TEST: Hotkey Manager (Push-to-Talk)")
    print("=" * 60)

    try:
        manager = create_hotkey_manager()

        if not manager:
            return False, "No hotkey manager available"

        print(f"✓ Hotkey manager created")
        print(f"  Type: {type(manager).__name__}")

        # Test registration with press/release callbacks
        press_called = []
        release_called = []

        def on_press():
            press_called.append(True)

        def on_release():
            release_called.append(True)

        success = manager.register(
            "<ctrl>+<super>",
            on_press=on_press,
            on_release=on_release
        )

        if not success:
            return False, "Failed to register hotkey"

        print(f"✓ Push-to-talk hotkey registered")
        print(f"  on_press callback: registered")
        print(f"  on_release callback: registered")

        manager.unregister("<ctrl>+<super>")
        print(f"✓ Hotkey unregistered successfully")

        return True, "Push-to-talk hotkeys working"
    except Exception as e:
        print(f"✗ Hotkey manager failed: {e}")
        return False, str(e)


def test_end_to_end_simulation():
    """Simulate end-to-end workflow without real input."""
    print("\n" + "=" * 60)
    print("TEST: End-to-End Simulation")
    print("=" * 60)

    try:
        # Initialize all components
        print("Initializing all components...")

        config = Config.load()
        audio_capture = SoundDeviceCapture(
            sample_rate=config.audio.sample_rate,
            channels=config.audio.channels
        )
        engine = create_whisper_engine(
            model_name="base",
            language="en",
            device="auto"
        )

        if not engine or not engine.load_model():
            return False, "Failed to initialize engine"

        injector = create_text_injector()
        if not injector:
            return False, "Failed to initialize injector"

        print("✓ All components initialized")

        # Simulate workflow
        print("\nSimulating push-to-talk workflow:")
        print("  1. Press hotkey (simulated)")

        # Simulate: Start recording
        print("  2. Start recording...")
        audio_capture.clear_buffer()
        audio_capture.start()
        time.sleep(0.5)  # Simulate speaking

        print("  3. Release hotkey (simulated)")

        # Simulate: Stop recording
        print("  4. Stop recording...")
        audio_capture.stop()

        audio_data = audio_capture.get_audio_data()
        if audio_data is None or len(audio_data) == 0:
            print("  ⚠️  No audio (expected in simulation)")
        else:
            print(f"  ✓ Captured {len(audio_data)} samples")

            # Transcribe
            print("  5. Transcribing...")
            result = engine.transcribe(audio_data)
            print(f"  ✓ Transcription complete")

        print("\n✓ End-to-end simulation successful")
        return True, "Workflow simulation complete"

    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        return False, str(e)


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "TALKY INTEGRATION TESTS" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\nRunning comprehensive non-interactive tests...\n")

    results = TestResults()

    # Run all tests
    tests = [
        ("Configuration", test_configuration),
        ("Platform Detection", test_platform_detection),
        ("Audio Capture", test_audio_capture),
        ("Whisper Engine", test_whisper_engine),
        ("Text Injector", test_text_injector),
        ("Hotkey Manager", test_hotkey_manager),
        ("End-to-End", test_end_to_end_simulation),
    ]

    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            results.record(test_name, passed, message)
        except Exception as e:
            results.record(test_name, False, f"Exception: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results.tests.items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if result["message"]:
            print(f"         {result['message']}")

    print("\n" + "=" * 60)
    print(results.summary())

    if results.all_passed():
        print("✓ ALL TESTS PASSED - Ready for full application test!")
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")

    print("=" * 60)
    print()

    return 0 if results.all_passed() else 1


if __name__ == "__main__":
    sys.exit(main())
