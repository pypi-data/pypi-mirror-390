#!/usr/bin/env python3
"""Test script for Whisper transcription."""

import sys
import time
import numpy as np
sys.path.insert(0, 'src')

from talky.whisper import create_whisper_engine
from talky.audio import SoundDeviceCapture


def test_whisper_availability():
    """Test if Whisper is available."""
    print("=" * 60)
    print("WHISPER AVAILABILITY TEST")
    print("=" * 60)

    try:
        import faster_whisper
        print("\n✓ faster-whisper is installed")
        print(f"  Version: {faster_whisper.__version__}")
        return True
    except ImportError:
        print("\n✗ faster-whisper not installed")
        print("  Install with: pip install faster-whisper")
        return False


def test_whisper_engine():
    """Test Whisper engine creation and model loading."""
    print("\n" + "=" * 60)
    print("WHISPER ENGINE TEST")
    print("=" * 60)

    # Create engine with base model
    print("\nCreating Whisper engine (base model)...")
    engine = create_whisper_engine(
        model_name="base",
        language="en",
        device="auto",
        compute_type="default"
    )

    if not engine:
        print("✗ Failed to create Whisper engine")
        return None

    print("✓ Engine created")

    # Load model
    print("\nLoading model (this may take a moment on first run)...")
    success = engine.load_model()

    if not success:
        print("✗ Failed to load model")
        return None

    # Show model info
    info = engine.get_model_info()
    print("\nModel Information:")
    print(f"  Model: {info['model_name']}")
    print(f"  Device: {info['device']}")
    print(f"  Compute Type: {info['compute_type']}")
    print(f"  Language: {info['language']}")
    print(f"  Loaded: {info['is_loaded']}")

    return engine


def test_transcription_with_audio(engine):
    """Test transcription with real audio."""
    print("\n" + "=" * 60)
    print("AUDIO TRANSCRIPTION TEST")
    print("=" * 60)

    print("\nInitializing audio capture...")
    capture = SoundDeviceCapture(sample_rate=16000, channels=1)

    print("\n📢 Get ready to speak!")
    print("   Recording will start in 3 seconds...")
    print("   Speak for about 5 seconds after recording starts.")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    # Start recording
    print("\n🎤 RECORDING... (speak now)")
    capture.start()

    # Record for 5 seconds
    time.sleep(5)

    # Stop recording
    capture.stop()
    print("⏹️  Recording stopped\n")

    # Get audio data
    audio_data = capture.get_audio_data()

    if audio_data is None or len(audio_data) == 0:
        print("✗ No audio data captured")
        return False

    print(f"Audio captured: {len(audio_data)} samples ({len(audio_data)/16000:.2f} seconds)")

    # Transcribe
    print("\n🔄 Transcribing...")
    start_time = time.time()

    result = engine.transcribe(audio_data)

    elapsed = time.time() - start_time

    # Display results
    print(f"✓ Transcription complete in {elapsed:.2f}s")
    print("\n" + "=" * 60)
    print("TRANSCRIPTION RESULT")
    print("=" * 60)

    if result.get("error"):
        print(f"\n✗ Error: {result['error']}")
        return False

    print(f"\nText: {result['text']}")
    print(f"Language: {result['language']} (confidence: {result.get('language_probability', 0):.2%})")
    print(f"Duration: {result.get('duration', 0):.2f}s")

    if result.get("segments"):
        print(f"\nSegments: {len(result['segments'])}")
        for i, seg in enumerate(result['segments'], 1):
            print(f"  [{i}] {seg['start']:.2f}s - {seg['end']:.2f}s: {seg['text']}")

    return True


def test_synthetic_audio(engine):
    """Test transcription with synthetic audio (fallback)."""
    print("\n" + "=" * 60)
    print("SYNTHETIC AUDIO TEST")
    print("=" * 60)

    # Generate 3 seconds of silence (for testing pipeline)
    print("\nGenerating synthetic audio (3s of silence)...")
    sample_rate = 16000
    duration = 3
    audio_data = np.zeros(sample_rate * duration, dtype=np.float32)

    print("✓ Audio generated")

    # Transcribe
    print("\n🔄 Transcribing...")
    start_time = time.time()

    result = engine.transcribe(audio_data)

    elapsed = time.time() - start_time

    print(f"✓ Transcription complete in {elapsed:.2f}s")
    print(f"Result: {result['text'] if result['text'] else '(no speech detected)'}")

    return True


def main():
    """Run Whisper tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 18 + "WHISPER TESTS" + " " * 27 + "║")
    print("╚" + "=" * 58 + "╝")

    # Check availability
    if not test_whisper_availability():
        print("\nPlease install faster-whisper:")
        print("  pip install faster-whisper")
        return 1

    # Test engine
    engine = test_whisper_engine()
    if not engine:
        return 1

    # Choose test type
    print("\n" + "=" * 60)
    print("Select test:")
    print("  1. Test with real microphone audio (recommended)")
    print("  2. Test with synthetic audio (silent)")
    print("=" * 60)

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        success = test_transcription_with_audio(engine)
    elif choice == "2":
        success = test_synthetic_audio(engine)
    else:
        print("Invalid choice")
        return 1

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 60)
    print()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
