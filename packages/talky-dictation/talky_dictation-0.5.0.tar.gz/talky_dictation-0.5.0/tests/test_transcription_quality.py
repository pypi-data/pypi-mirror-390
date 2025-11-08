#!/usr/bin/env python3
"""Real-world transcription quality tests for Talky."""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from talky.whisper import create_whisper_engine
from talky.audio import SoundDeviceCapture
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionQualityTest:
    """Test suite for real-world transcription quality."""

    def __init__(self):
        """Initialize test suite."""
        self.results: List[Dict] = []
        self.whisper_engine = None

    def setup(self, model_name: str = "base", device: str = "auto"):
        """
        Set up Whisper engine for testing.

        Args:
            model_name: Whisper model to use
            device: Device to use (auto/cuda/cpu)
        """
        logger.info(f"Setting up Whisper engine: model={model_name}, device={device}")

        self.whisper_engine = create_whisper_engine(
            model_name=model_name,
            language=None,  # Auto-detect
            device=device
        )

        if not self.whisper_engine.load_model():
            raise RuntimeError("Failed to load Whisper model")

        logger.info("✓ Whisper engine ready")

    def test_sentence(
        self,
        audio_data: np.ndarray,
        expected_text: str,
        language: str = None,
        test_name: str = "Test"
    ) -> Dict:
        """
        Test transcription of a sentence.

        Args:
            audio_data: Audio data as numpy array
            expected_text: Expected transcription
            language: Language code (optional)
            test_name: Name of the test

        Returns:
            Dict with test results
        """
        logger.info(f"\nRunning: {test_name}")
        logger.info(f"Expected: '{expected_text}'")

        # Transcribe
        start_time = time.time()
        result = self.whisper_engine.transcribe(audio_data, language=language)
        elapsed = time.time() - start_time

        # Extract result
        transcribed_text = result.get("text", "").strip()
        detected_language = result.get("language", "unknown")
        error = result.get("error")

        logger.info(f"Transcribed: '{transcribed_text}'")
        logger.info(f"Language: {detected_language}")
        logger.info(f"Time: {elapsed:.2f}s")

        # Calculate similarity (simple word-based)
        similarity = self._calculate_similarity(expected_text, transcribed_text)
        logger.info(f"Similarity: {similarity:.1f}%")

        # Result
        test_result = {
            "test_name": test_name,
            "expected": expected_text,
            "transcribed": transcribed_text,
            "language": detected_language,
            "time": elapsed,
            "similarity": similarity,
            "passed": similarity >= 80.0,  # 80% threshold
            "error": error
        }

        self.results.append(test_result)

        if test_result["passed"]:
            logger.info("✓ PASSED")
        else:
            logger.info("✗ FAILED")

        return test_result

    def test_live_recording(
        self,
        duration: float = 5.0,
        expected_text: str = None,
        language: str = None,
        test_name: str = "Live Recording Test"
    ) -> Dict:
        """
        Test with live microphone recording.

        Args:
            duration: Recording duration in seconds
            expected_text: Expected text (optional, for validation)
            language: Language code (optional)
            test_name: Name of the test

        Returns:
            Dict with test results
        """
        logger.info(f"\n{test_name}")
        logger.info(f"Recording for {duration}s... Speak now!")

        # Record
        audio_capture = SoundDeviceCapture()
        audio_capture.start()
        time.sleep(duration)
        audio_capture.stop()

        audio_data = audio_capture.get_audio_data()

        if audio_data is None or len(audio_data) == 0:
            logger.warning("No audio captured")
            return {
                "test_name": test_name,
                "error": "No audio captured",
                "passed": False
            }

        # Transcribe
        start_time = time.time()
        result = self.whisper_engine.transcribe(audio_data, language=language)
        elapsed = time.time() - start_time

        transcribed_text = result.get("text", "").strip()
        detected_language = result.get("language", "unknown")

        logger.info(f"Transcribed: '{transcribed_text}'")
        logger.info(f"Language: {detected_language}")
        logger.info(f"Time: {elapsed:.2f}s")

        # Calculate similarity if expected text provided
        similarity = None
        passed = None
        if expected_text:
            similarity = self._calculate_similarity(expected_text, transcribed_text)
            passed = similarity >= 80.0
            logger.info(f"Expected: '{expected_text}'")
            logger.info(f"Similarity: {similarity:.1f}%")
            logger.info("✓ PASSED" if passed else "✗ FAILED")

        test_result = {
            "test_name": test_name,
            "expected": expected_text,
            "transcribed": transcribed_text,
            "language": detected_language,
            "time": elapsed,
            "similarity": similarity,
            "passed": passed,
            "audio_duration": len(audio_data) / 16000.0
        }

        self.results.append(test_result)
        return test_result

    def test_multi_language(self, audio_samples: List[Tuple[np.ndarray, str, str]]):
        """
        Test transcription across multiple languages.

        Args:
            audio_samples: List of (audio_data, expected_text, language_code)
        """
        logger.info("\n" + "=" * 60)
        logger.info("Multi-Language Transcription Test")
        logger.info("=" * 60)

        for audio_data, expected_text, language in audio_samples:
            from talky.whisper.languages import get_language_name
            lang_name = get_language_name(language)

            self.test_sentence(
                audio_data,
                expected_text,
                language=language,
                test_name=f"{lang_name} ({language})"
            )

    def _calculate_similarity(self, expected: str, actual: str) -> float:
        """
        Calculate similarity between expected and actual text.

        Simple word-based similarity metric.

        Args:
            expected: Expected text
            actual: Actual transcribed text

        Returns:
            Similarity percentage (0-100)
        """
        if not expected or not actual:
            return 0.0

        # Normalize
        expected_words = expected.lower().split()
        actual_words = actual.lower().split()

        if not expected_words:
            return 0.0

        # Count matching words
        matches = sum(1 for word in expected_words if word in actual_words)

        # Calculate similarity
        similarity = (matches / len(expected_words)) * 100.0
        return similarity

    def generate_report(self) -> str:
        """
        Generate test report.

        Returns:
            Formatted report string
        """
        if not self.results:
            return "No test results available"

        report = []
        report.append("\n" + "=" * 70)
        report.append("TRANSCRIPTION QUALITY TEST REPORT")
        report.append("=" * 70)

        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("passed") is True)
        failed = sum(1 for r in self.results if r.get("passed") is False)
        skipped = sum(1 for r in self.results if r.get("passed") is None)

        report.append(f"\nTotal Tests: {total}")
        report.append(f"Passed: {passed}")
        report.append(f"Failed: {failed}")
        report.append(f"Skipped: {skipped}")

        # Calculate average metrics
        times = [r["time"] for r in self.results if "time" in r]
        similarities = [r["similarity"] for r in self.results if r.get("similarity") is not None]

        if times:
            avg_time = sum(times) / len(times)
            report.append(f"\nAverage Transcription Time: {avg_time:.2f}s")
            report.append(f"Min Time: {min(times):.2f}s")
            report.append(f"Max Time: {max(times):.2f}s")

        if similarities:
            avg_similarity = sum(similarities) / len(similarities)
            report.append(f"\nAverage Similarity: {avg_similarity:.1f}%")
            report.append(f"Min Similarity: {min(similarities):.1f}%")
            report.append(f"Max Similarity: {max(similarities):.1f}%")

        # Detailed results
        report.append("\n" + "-" * 70)
        report.append("DETAILED RESULTS")
        report.append("-" * 70)

        for i, result in enumerate(self.results, 1):
            report.append(f"\n{i}. {result['test_name']}")

            if result.get("error"):
                report.append(f"   ERROR: {result['error']}")
                continue

            report.append(f"   Expected:    '{result.get('expected', 'N/A')}'")
            report.append(f"   Transcribed: '{result.get('transcribed', 'N/A')}'")
            report.append(f"   Language:    {result.get('language', 'N/A')}")
            report.append(f"   Time:        {result.get('time', 0):.2f}s")

            if result.get("similarity") is not None:
                report.append(f"   Similarity:  {result['similarity']:.1f}%")

            status = result.get("passed")
            if status is True:
                report.append("   Status:      ✓ PASSED")
            elif status is False:
                report.append("   Status:      ✗ FAILED")
            else:
                report.append("   Status:      ⊘ SKIPPED")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def save_report(self, filename: str = "transcription_test_report.txt"):
        """
        Save test report to file.

        Args:
            filename: Output filename
        """
        report = self.generate_report()

        output_path = Path(__file__).parent / filename
        output_path.write_text(report)

        logger.info(f"\n✓ Report saved to: {output_path}")


def main():
    """Run transcription quality tests."""
    print("\n" + "=" * 70)
    print("TALKY - TRANSCRIPTION QUALITY TEST SUITE")
    print("=" * 70)

    # Initialize
    test_suite = TranscriptionQualityTest()

    try:
        # Setup Whisper engine
        test_suite.setup(model_name="base", device="auto")

        # Interactive live tests
        print("\n" + "-" * 70)
        print("INTERACTIVE LIVE RECORDING TESTS")
        print("-" * 70)
        print("\nThese tests require you to speak into the microphone.")
        print("Press Enter when ready to continue, or Ctrl+C to skip...")

        try:
            input()

            # Test 1: English
            print("\nTest 1: English")
            print("Speak this sentence: 'The quick brown fox jumps over the lazy dog'")
            input("Press Enter to start recording...")
            test_suite.test_live_recording(
                duration=5.0,
                expected_text="the quick brown fox jumps over the lazy dog",
                language="en",
                test_name="English - Common Phrase"
            )

            # Test 2: Free-form English
            print("\nTest 2: Free-form English")
            print("Say anything you like for 5 seconds...")
            input("Press Enter to start recording...")
            test_suite.test_live_recording(
                duration=5.0,
                language="en",
                test_name="English - Free-form"
            )

            # Test 3: Different language (if multilingual)
            print("\nTest 3: Multi-language (Optional)")
            print("Speak in any non-English language, or press Enter to skip...")
            choice = input("Enter language code (e.g., es, fr, de) or press Enter to skip: ").strip()

            if choice:
                input("Press Enter to start recording...")
                test_suite.test_live_recording(
                    duration=5.0,
                    language=choice,
                    test_name=f"{choice.upper()} - Free-form"
                )

        except KeyboardInterrupt:
            print("\n\nSkipping interactive tests...")

        # Generate and display report
        print(test_suite.generate_report())

        # Save report
        test_suite.save_report()

        # Exit code based on results
        failed = sum(1 for r in test_suite.results if r.get("passed") is False)
        return 0 if failed == 0 else 1

    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
