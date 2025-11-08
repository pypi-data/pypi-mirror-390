#!/usr/bin/env python3
"""Memory profiling for Talky."""

import sys
import time
import psutil
import gc
from pathlib import Path
from typing import List, Dict
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from talky.whisper import create_whisper_engine
from talky.audio import SoundDeviceCapture
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryProfiler:
    """Memory profiling for Talky components."""

    def __init__(self):
        """Initialize profiler."""
        self.process = psutil.Process()
        self.snapshots: List[Dict] = []
        self.baseline_memory = 0

    def get_memory_usage(self) -> Dict:
        """
        Get current memory usage.

        Returns:
            Dict with memory metrics
        """
        mem_info = self.process.memory_info()
        return {
            "rss_mb": mem_info.rss / (1024 ** 2),  # Resident Set Size
            "vms_mb": mem_info.vms / (1024 ** 2),  # Virtual Memory Size
            "percent": self.process.memory_percent(),
        }

    def take_snapshot(self, label: str):
        """
        Take memory snapshot.

        Args:
            label: Label for this snapshot
        """
        mem = self.get_memory_usage()
        snapshot = {
            "label": label,
            "timestamp": time.time(),
            **mem
        }

        if self.baseline_memory > 0:
            snapshot["delta_mb"] = mem["rss_mb"] - self.baseline_memory

        self.snapshots.append(snapshot)
        logger.info(f"[{label}] Memory: {mem['rss_mb']:.1f}MB "
                   f"({snapshot.get('delta_mb', 0):+.1f}MB)")

    def set_baseline(self):
        """Set baseline memory usage."""
        mem = self.get_memory_usage()
        self.baseline_memory = mem["rss_mb"]
        self.take_snapshot("Baseline")

    def profile_whisper_loading(self, model_name: str = "base"):
        """
        Profile memory usage during Whisper model loading.

        Args:
            model_name: Model to load
        """
        logger.info(f"\nProfiling Whisper model loading ({model_name})...")

        self.take_snapshot("Before model creation")

        # Create engine
        whisper_engine = create_whisper_engine(
            model_name=model_name,
            language=None,
            device="auto"
        )

        self.take_snapshot("After engine creation")

        # Load model
        whisper_engine.load_model()

        self.take_snapshot("After model loading")

        return whisper_engine

    def profile_transcription_cycles(
        self,
        whisper_engine,
        cycles: int = 10,
        audio_duration: float = 3.0
    ):
        """
        Profile memory during repeated transcription cycles.

        Args:
            whisper_engine: Whisper engine instance
            cycles: Number of transcription cycles
            audio_duration: Duration of test audio
        """
        logger.info(f"\nProfiling {cycles} transcription cycles...")

        sample_rate = 16000

        for i in range(cycles):
            # Generate test audio
            audio_data = np.random.randn(int(sample_rate * audio_duration)).astype(np.float32) * 0.01

            # Transcribe
            result = whisper_engine.transcribe(audio_data)

            # Take snapshot every few cycles
            if i % 2 == 0:
                self.take_snapshot(f"After cycle {i+1}/{cycles}")

            # Force garbage collection periodically
            if i % 5 == 0:
                gc.collect()

        # Final snapshot
        self.take_snapshot(f"After all {cycles} cycles")

    def profile_audio_capture_cycles(self, cycles: int = 5, duration: float = 2.0):
        """
        Profile memory during repeated audio capture cycles.

        Args:
            cycles: Number of capture cycles
            duration: Duration per capture
        """
        logger.info(f"\nProfiling {cycles} audio capture cycles...")

        audio_capture = SoundDeviceCapture()

        for i in range(cycles):
            audio_capture.start()
            time.sleep(duration)
            audio_capture.stop()
            audio_data = audio_capture.get_audio_data()

            if i % 2 == 0:
                self.take_snapshot(f"After audio cycle {i+1}/{cycles}")

            # Clear buffer
            audio_capture.clear_buffer()

            gc.collect()

        self.take_snapshot("After all audio cycles")

    def check_memory_leaks(self) -> Dict:
        """
        Check for potential memory leaks.

        Returns:
            Dict with leak analysis
        """
        logger.info("\nAnalyzing for memory leaks...")

        if len(self.snapshots) < 3:
            return {"error": "Not enough snapshots for analysis"}

        # Compare baseline to final
        baseline = self.snapshots[0]
        final = self.snapshots[-1]

        total_increase = final["rss_mb"] - baseline["rss_mb"]
        percent_increase = (total_increase / baseline["rss_mb"]) * 100

        # Calculate trend
        memory_values = [s["rss_mb"] for s in self.snapshots]
        avg_increase = (memory_values[-1] - memory_values[0]) / len(memory_values)

        analysis = {
            "baseline_mb": baseline["rss_mb"],
            "final_mb": final["rss_mb"],
            "total_increase_mb": total_increase,
            "percent_increase": percent_increase,
            "avg_increase_per_snapshot_mb": avg_increase,
            "snapshots_analyzed": len(self.snapshots),
        }

        # Determine if leak likely
        # Heuristic: >100MB increase or >50% increase suggests leak
        if total_increase > 100 or percent_increase > 50:
            analysis["leak_likely"] = True
            analysis["severity"] = "HIGH"
        elif total_increase > 50 or percent_increase > 25:
            analysis["leak_likely"] = True
            analysis["severity"] = "MEDIUM"
        elif total_increase > 20 or percent_increase > 10:
            analysis["leak_likely"] = True
            analysis["severity"] = "LOW"
        else:
            analysis["leak_likely"] = False
            analysis["severity"] = "NONE"

        logger.info(f"Total memory increase: {total_increase:.1f}MB ({percent_increase:.1f}%)")
        logger.info(f"Leak likelihood: {analysis['severity']}")

        return analysis

    def generate_report(self) -> str:
        """
        Generate memory profiling report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "=" * 70)
        report.append("TALKY MEMORY PROFILING REPORT")
        report.append("=" * 70)

        # System info
        system_mem = psutil.virtual_memory()
        report.append("\nSYSTEM MEMORY:")
        report.append(f"  Total: {system_mem.total / (1024**3):.1f}GB")
        report.append(f"  Available: {system_mem.available / (1024**3):.1f}GB")
        report.append(f"  Used: {system_mem.percent}%")

        # Snapshots
        report.append("\nMEMORY SNAPSHOTS:")
        report.append("-" * 70)
        report.append(f"{'Label':<40} {'Memory (MB)':>12} {'Delta (MB)':>12}")
        report.append("-" * 70)

        for snapshot in self.snapshots:
            label = snapshot["label"]
            memory = snapshot["rss_mb"]
            delta = snapshot.get("delta_mb", 0)
            report.append(f"{label:<40} {memory:>12.1f} {delta:>+12.1f}")

        # Leak analysis
        leak_analysis = self.check_memory_leaks()
        if "error" not in leak_analysis:
            report.append("\nMEMORY LEAK ANALYSIS:")
            report.append("-" * 70)
            report.append(f"  Baseline Memory: {leak_analysis['baseline_mb']:.1f}MB")
            report.append(f"  Final Memory: {leak_analysis['final_mb']:.1f}MB")
            report.append(f"  Total Increase: {leak_analysis['total_increase_mb']:.1f}MB "
                         f"({leak_analysis['percent_increase']:.1f}%)")
            report.append(f"  Snapshots Analyzed: {leak_analysis['snapshots_analyzed']}")
            report.append(f"  Leak Likelihood: {leak_analysis['severity']}")

            if leak_analysis['leak_likely']:
                report.append("\n  ⚠ WARNING: Potential memory leak detected!")
                report.append("  Recommendation: Investigate resource cleanup in long-running operations")
            else:
                report.append("\n  ✓ No significant memory leaks detected")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def save_report(self, filename: str = "memory_profile_report.txt"):
        """
        Save memory profiling report.

        Args:
            filename: Output filename
        """
        report = self.generate_report()

        output_path = Path(__file__).parent / filename
        output_path.write_text(report)

        logger.info(f"\n✓ Report saved to: {output_path}")


def main():
    """Run memory profiling."""
    print("\n" + "=" * 70)
    print("TALKY - MEMORY PROFILING SUITE")
    print("=" * 70)

    profiler = MemoryProfiler()

    try:
        # Set baseline
        profiler.set_baseline()

        # Profile Whisper loading
        whisper_engine = profiler.profile_whisper_loading(model_name="base")

        # Profile transcription cycles
        profiler.profile_transcription_cycles(
            whisper_engine,
            cycles=10,
            audio_duration=3.0
        )

        # Profile audio capture
        profiler.profile_audio_capture_cycles(cycles=5, duration=2.0)

        # Generate and display report
        print(profiler.generate_report())

        # Save report
        profiler.save_report()

        # Check for leaks and return appropriate exit code
        leak_analysis = profiler.check_memory_leaks()
        if leak_analysis.get("severity") in ["HIGH", "MEDIUM"]:
            logger.warning("⚠ Memory leak concerns detected")
            return 1

        return 0

    except Exception as e:
        logger.error(f"Memory profiling failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
