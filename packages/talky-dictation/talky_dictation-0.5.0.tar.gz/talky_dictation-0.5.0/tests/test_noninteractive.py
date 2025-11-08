#!/usr/bin/env python3
"""Non-interactive test for platform components."""

import sys
sys.path.insert(0, 'src')

from talky.utils.platform import get_platform_detector
from talky.input import create_text_injector
from talky.hotkeys import create_hotkey_manager


def test_platform():
    """Test platform detection."""
    print("=" * 60)
    print("PLATFORM DETECTION TEST")
    print("=" * 60)

    detector = get_platform_detector()
    summary = detector.get_platform_summary()

    print(f"\nDisplay Server: {summary['display_server']}")
    print(f"Desktop Environment: {summary['desktop_environment']}")
    print(f"CUDA Available: {summary['has_cuda']}")
    print(f"Audio Backend: {summary['audio_backend']}")
    print(f"\nText Injection Tools:")
    for tool, available in summary['text_injection'].items():
        status = "✓" if available else "✗"
        print(f"  {status} {tool}")
    print(f"\nRecommended Injector: {summary['recommended_injector']}")


def test_text_injector():
    """Test text injector creation."""
    print("\n" + "=" * 60)
    print("TEXT INJECTOR TEST")
    print("=" * 60)

    injector = create_text_injector()

    if not injector:
        print("\n✗ No text injection method available!")
        return False

    print(f"\n✓ Text injector created successfully")
    print(f"  Available: {injector.is_available}")

    if hasattr(injector, 'get_active_method'):
        print(f"  Active Method: {injector.get_active_method()}")

    return True


def test_hotkey_manager():
    """Test hotkey manager creation."""
    print("\n" + "=" * 60)
    print("HOTKEY MANAGER TEST")
    print("=" * 60)

    manager = create_hotkey_manager()

    if not manager:
        print("\n✗ Hotkey manager not available!")
        return False

    print(f"\n✓ Hotkey manager created successfully")
    print(f"  Type: {type(manager).__name__}")

    # Try to register a test hotkey
    def dummy_callback():
        pass

    success = manager.register("<ctrl>+<super>", dummy_callback)

    if success:
        print(f"  ✓ Hotkey registration successful")
        manager.unregister("<ctrl>+<super>")
    else:
        print(f"  ✗ Hotkey registration failed")

    # Check for Wayland setup instructions
    if hasattr(manager, 'get_setup_instructions'):
        instructions = manager.get_setup_instructions()
        if instructions:
            print(f"\n  ⚠️  Manual Setup Required:")
            print(f"     {instructions}")

    return True


def test_audio():
    """Test audio capture."""
    print("\n" + "=" * 60)
    print("AUDIO CAPTURE TEST")
    print("=" * 60)

    try:
        from talky.audio import SoundDeviceCapture

        capture = SoundDeviceCapture()
        print(f"\n✓ Audio capture initialized")
        print(f"  Sample Rate: {capture.sample_rate} Hz")
        print(f"  Channels: {capture.channels}")

        # List devices
        devices = SoundDeviceCapture.list_devices()
        print(f"  Input Devices Available: {len(devices)}")

        if devices:
            default = SoundDeviceCapture.get_default_device()
            if default:
                print(f"  Default Device: {default.get('name', 'Unknown')}")

        return True

    except Exception as e:
        print(f"\n✗ Audio capture error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "TALKY COMPONENT TESTS" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")

    results = {
        "Platform Detection": False,
        "Text Injector": False,
        "Hotkey Manager": False,
        "Audio Capture": False,
    }

    # Run tests
    try:
        test_platform()
        results["Platform Detection"] = True
    except Exception as e:
        print(f"Platform detection error: {e}")

    try:
        results["Text Injector"] = test_text_injector()
    except Exception as e:
        print(f"Text injector error: {e}")

    try:
        results["Hotkey Manager"] = test_hotkey_manager()
    except Exception as e:
        print(f"Hotkey manager error: {e}")

    try:
        results["Audio Capture"] = test_audio()
    except Exception as e:
        print(f"Audio capture error: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")

    all_passed = all(results.values())
    print("\n" + ("=" * 60))
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 60)
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
