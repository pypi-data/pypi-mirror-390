#!/usr/bin/env python3
"""Test script for platform detection, text injection, and hotkeys."""

import sys
import time
sys.path.insert(0, 'src')

from talky.utils.platform import get_platform_detector
from talky.input import create_text_injector
from talky.hotkeys import create_hotkey_manager


def test_platform_detection():
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

    return detector


def test_text_injection():
    """Test text injection."""
    print("\n" + "=" * 60)
    print("TEXT INJECTION TEST")
    print("=" * 60)

    injector = create_text_injector()

    if not injector:
        print("\n✗ No text injection method available!")
        return False

    if hasattr(injector, 'get_active_method'):
        print(f"\nActive Method: {injector.get_active_method()}")

    print("\nText injection test:")
    print("1. Click in a text editor or any input field")
    print("2. Text will be injected in 5 seconds...")

    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    test_text = "Hello from Talky! This is a test."
    success = injector.inject_text(test_text)

    if success:
        print(f"\n✓ Text injection successful!")
        return True
    else:
        print(f"\n✗ Text injection failed!")
        return False


def test_hotkeys():
    """Test hotkey registration."""
    print("\n" + "=" * 60)
    print("HOTKEY TEST")
    print("=" * 60)

    manager = create_hotkey_manager()

    if not manager:
        print("\n✗ Hotkey manager not available!")
        return False

    print("\nHotkey Manager Type:", type(manager).__name__)

    # Test callback
    def test_callback():
        print("\n🎉 HOTKEY PRESSED! (Ctrl+Win)")

    # Register hotkey
    success = manager.register("<ctrl>+<super>", test_callback)

    if not success:
        print("\n✗ Failed to register hotkey")
        return False

    print("\n✓ Hotkey registered: Ctrl+Win")

    # Check if Wayland needs manual setup
    if hasattr(manager, 'get_setup_instructions'):
        instructions = manager.get_setup_instructions()
        if instructions:
            print(f"\n⚠️  Manual Setup Required:")
            print(f"   {instructions}")

    # Start listener
    try:
        manager.start()
        print("\n✓ Hotkey listener started")
        print("\nPress Ctrl+Win to test hotkey...")
        print("Press Ctrl+C to exit\n")

        # Wait for hotkey presses
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nStopping hotkey listener...")
        manager.stop()
        print("✓ Test complete")
        return True
    except Exception as e:
        print(f"\n✗ Error during hotkey test: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "TALKY PLATFORM TESTS" + " " * 23 + "║")
    print("╚" + "=" * 58 + "╝")

    # Test platform detection
    detector = test_platform_detection()

    # Test text injection
    print("\n\nWould you like to test text injection? (y/n): ", end="", flush=True)
    response = input().strip().lower()
    if response == 'y':
        test_text_injection()

    # Test hotkeys
    print("\n\nWould you like to test hotkeys? (y/n): ", end="", flush=True)
    response = input().strip().lower()
    if response == 'y':
        test_hotkeys()

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
