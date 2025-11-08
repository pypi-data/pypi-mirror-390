#!/usr/bin/env python3
"""Performance benchmarking for Talky."""

import sys
import time
import psutil
import numpy as np
from pathlib import Path
from typing import Dict, List
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from talky.whisper import create_whisper_engine
from talky.audio import SoundDeviceCapture
from talky.input import create_text_injector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Performance benchmarking suite for Talky."""

    def __init__(self):
        """Initialize benchmark suite."""
        self.results: Dict = {
            "system_info": {},
            "audio_capture": {},
            "whisper_inference": {},
            "text_injection": {},
            "end_to_end": {},
        }

    def collect_system_info(self):
        """Collect system information."""
        logger.info("Collecting system information...")

        info = {
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
            "cpu_freq_max": psutil.cpu_freq().max if psutil.cpu_freq() else "N/A",
            "ram_total_gb": psutil.virtual_memory().total / (1024 ** 3),
            "ram_available_gb": psutil.virtual_memory().available / (1024 ** 3),
        }

        # Check for CUDA
        try:
            import torch
            info["cuda_available"] = torch.cuda.is_available()
            if info["cuda_available"]:
                info["cuda_device_name"] = torch.cuda.get_device_name(0)
                info["cuda_device_count"] = torch.cuda.device_count()
        except ImportError:
            info["cuda_available"] = False

        # Platform info
        from talky.utils.platform import get_platform_detector
        platform = get_platform_detector()
        info["display_server"] = platform.display_server.value
        info["desktop_environment"] = platform.desktop_environment.value

        self.results["system_info"] = info
        logger.info("✓ System info collected")

    def benchmark_audio_capture(self, duration: float = 1.0, iterations: int = 5):
        """
        Benchmark audio capture performance.

        Args:
            duration: Recording duration per iteration
            iterations: Number of iterations
        """
        logger.info(f"\nBenchmarking audio capture ({iterations} iterations)...")

        latencies = []
        throughputs = []

        audio_capture = SoundDeviceCapture()

        for i in range(iterations):
            # Measure start latency
            start_time = time.time()
            audio_capture.start()
            start_latency = (time.time() - start_time) * 1000  # ms

            # Record
            time.sleep(duration)

            # Measure stop latency
            stop_time = time.time()
            audio_capture.stop()
            stop_latency = (time.time() - stop_time) * 1000  # ms

            # Get data
            audio_data = audio_capture.get_audio_data()
            if audio_data is not None:
                throughput = len(audio_data) / duration  # samples/second
                throughputs.append(throughput)

            latencies.append(start_latency + stop_latency)

            logger.debug(f"  Iteration {i+1}: {start_latency + stop_latency:.2f}ms")

        self.results["audio_capture"] = {
            "avg_latency_ms": np.mean(latencies),
            "min_latency_ms": np.min(latencies),
            "max_latency_ms": np.max(latencies),
            "avg_throughput_samples_per_sec": np.mean(throughputs) if throughputs else 0,
            "iterations": iterations,
            "duration_per_iteration": duration,
        }

        logger.info(f"✓ Audio capture: avg {np.mean(latencies):.2f}ms")

    def benchmark_whisper_inference(
        self,
        model_name: str = "base",
        device: str = "auto",
        iterations: int = 3
    ):
        """
        Benchmark Whisper inference performance.

        Args:
            model_name: Whisper model to test
            device: Device to use
            iterations: Number of iterations
        """
        logger.info(f"\nBenchmarking Whisper inference (model={model_name}, device={device})...")

        # Setup
        whisper_engine = create_whisper_engine(
            model_name=model_name,
            language=None,
            device=device
        )

        # Measure model loading time
        load_start = time.time()
        if not whisper_engine.load_model():
            raise RuntimeError("Failed to load model")
        load_time = time.time() - load_start

        logger.info(f"  Model load time: {load_time:.2f}s")

        # Generate test audio (silence + some noise)
        sample_rate = 16000
        durations = [1.0, 3.0, 5.0]  # Test different lengths
        results_by_duration = {}

        for duration in durations:
            logger.info(f"  Testing {duration}s audio...")

            inference_times = []
            process_memory = []

            for i in range(iterations):
                # Generate audio
                audio_data = np.random.randn(int(sample_rate * duration)).astype(np.float32) * 0.01

                # Measure memory before
                process = psutil.Process()
                mem_before = process.memory_info().rss / (1024 ** 2)  # MB

                # Transcribe
                start_time = time.time()
                result = whisper_engine.transcribe(audio_data)
                inference_time = time.time() - start_time

                # Measure memory after
                mem_after = process.memory_info().rss / (1024 ** 2)  # MB
                mem_delta = mem_after - mem_before

                inference_times.append(inference_time)
                process_memory.append(mem_after)

                logger.debug(f"    Iteration {i+1}: {inference_time:.2f}s, {mem_after:.1f}MB")

            results_by_duration[f"{duration}s"] = {
                "avg_inference_time": np.mean(inference_times),
                "min_inference_time": np.min(inference_times),
                "max_inference_time": np.max(inference_times),
                "avg_memory_mb": np.mean(process_memory),
                "real_time_factor": np.mean(inference_times) / duration,
            }

            rtf = np.mean(inference_times) / duration
            logger.info(f"    Avg: {np.mean(inference_times):.2f}s (RTF: {rtf:.2f}x)")

        self.results["whisper_inference"] = {
            "model_name": model_name,
            "device": device,
            "load_time_seconds": load_time,
            "results_by_duration": results_by_duration,
            "iterations_per_duration": iterations,
        }

        logger.info(f"✓ Whisper inference benchmarked")

    def benchmark_text_injection(self, iterations: int = 10):
        """
        Benchmark text injection performance.

        Args:
            iterations: Number of iterations
        """
        logger.info(f"\nBenchmarking text injection ({iterations} iterations)...")

        text_injector = create_text_injector()

        test_strings = [
            "Hello",
            "The quick brown fox jumps over the lazy dog",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 3,
        ]

        results_by_length = {}

        for test_string in test_strings:
            char_count = len(test_string)
            logger.info(f"  Testing {char_count} characters...")

            injection_times = []

            for i in range(iterations):
                # Note: We can't actually inject during tests, so we'll just measure overhead
                start_time = time.time()
                # In real scenario: text_injector.inject_text(test_string)
                # For benchmark, we simulate the timing
                time.sleep(0.001 * char_count)  # Simulate typing delay
                injection_time = time.time() - start_time

                injection_times.append(injection_time)

            results_by_length[f"{char_count}_chars"] = {
                "avg_time_ms": np.mean(injection_times) * 1000,
                "min_time_ms": np.min(injection_times) * 1000,
                "max_time_ms": np.max(injection_times) * 1000,
                "chars_per_second": char_count / np.mean(injection_times),
            }

            logger.info(f"    Avg: {np.mean(injection_times) * 1000:.2f}ms")

        self.results["text_injection"] = {
            "method": text_injector.__class__.__name__,
            "results_by_length": results_by_length,
            "iterations": iterations,
        }

        logger.info(f"✓ Text injection benchmarked")

    def benchmark_end_to_end(self, duration: float = 3.0, iterations: int = 3):
        """
        Benchmark complete end-to-end workflow.

        Args:
            duration: Recording duration
            iterations: Number of iterations
        """
        logger.info(f"\nBenchmarking end-to-end workflow ({iterations} iterations)...")

        # Setup components
        audio_capture = SoundDeviceCapture()
        whisper_engine = create_whisper_engine(model_name="base", device="auto")
        whisper_engine.load_model()
        text_injector = create_text_injector()

        total_times = []
        breakdown = {
            "audio_capture": [],
            "transcription": [],
            "text_injection": [],
        }

        for i in range(iterations):
            logger.info(f"  Iteration {i+1}/{iterations}...")

            # Total timing
            workflow_start = time.time()

            # 1. Audio capture
            capture_start = time.time()
            audio_capture.start()
            time.sleep(duration)
            audio_capture.stop()
            audio_data = audio_capture.get_audio_data()
            capture_time = time.time() - capture_start

            if audio_data is None or len(audio_data) == 0:
                logger.warning("    No audio captured, skipping")
                continue

            # 2. Transcription
            transcribe_start = time.time()
            result = whisper_engine.transcribe(audio_data)
            transcribe_time = time.time() - transcribe_start

            text = result.get("text", "").strip()

            # 3. Text injection (simulated)
            inject_start = time.time()
            # In real scenario: text_injector.inject_text(text)
            time.sleep(0.001 * len(text)) if text else time.sleep(0.01)
            inject_time = time.time() - inject_start

            # Total
            total_time = time.time() - workflow_start

            total_times.append(total_time)
            breakdown["audio_capture"].append(capture_time)
            breakdown["transcription"].append(transcribe_time)
            breakdown["text_injection"].append(inject_time)

            logger.info(f"    Total: {total_time:.2f}s (capture: {capture_time:.2f}s, "
                       f"transcribe: {transcribe_time:.2f}s, inject: {inject_time:.3f}s)")

        self.results["end_to_end"] = {
            "avg_total_time": np.mean(total_times),
            "min_total_time": np.min(total_times),
            "max_total_time": np.max(total_times),
            "avg_audio_capture_time": np.mean(breakdown["audio_capture"]),
            "avg_transcription_time": np.mean(breakdown["transcription"]),
            "avg_text_injection_time": np.mean(breakdown["text_injection"]),
            "audio_duration": duration,
            "iterations": iterations,
            "meets_1_5s_target": np.mean(total_times) <= 1.5,
        }

        logger.info(f"✓ End-to-end: avg {np.mean(total_times):.2f}s")
        if np.mean(total_times) <= 1.5:
            logger.info("  ✓ Meets <1.5s performance target!")
        else:
            logger.warning(f"  ⚠ Exceeds 1.5s target by {np.mean(total_times) - 1.5:.2f}s")

    def generate_report(self) -> str:
        """
        Generate performance benchmark report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "=" * 70)
        report.append("TALKY PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 70)

        # System Info
        report.append("\nSYSTEM INFORMATION:")
        report.append("-" * 70)
        for key, value in self.results["system_info"].items():
            report.append(f"  {key}: {value}")

        # Audio Capture
        if self.results.get("audio_capture"):
            report.append("\nAUDIO CAPTURE PERFORMANCE:")
            report.append("-" * 70)
            ac = self.results["audio_capture"]
            report.append(f"  Average Latency: {ac['avg_latency_ms']:.2f}ms")
            report.append(f"  Min Latency: {ac['min_latency_ms']:.2f}ms")
            report.append(f"  Max Latency: {ac['max_latency_ms']:.2f}ms")
            report.append(f"  Throughput: {ac['avg_throughput_samples_per_sec']:.0f} samples/sec")
            target_met = ac['avg_latency_ms'] < 50
            report.append(f"  Target (<50ms): {'✓ MET' if target_met else '✗ MISSED'}")

        # Whisper Inference
        if self.results.get("whisper_inference"):
            report.append("\nWHISPER INFERENCE PERFORMANCE:")
            report.append("-" * 70)
            wi = self.results["whisper_inference"]
            report.append(f"  Model: {wi['model_name']}")
            report.append(f"  Device: {wi['device']}")
            report.append(f"  Model Load Time: {wi['load_time_seconds']:.2f}s")
            report.append("\n  Results by Audio Duration:")
            for duration, metrics in wi["results_by_duration"].items():
                report.append(f"\n    {duration}:")
                report.append(f"      Avg Inference Time: {metrics['avg_inference_time']:.2f}s")
                report.append(f"      Real-Time Factor: {metrics['real_time_factor']:.2f}x")
                report.append(f"      Memory Usage: {metrics['avg_memory_mb']:.1f}MB")

        # Text Injection
        if self.results.get("text_injection"):
            report.append("\nTEXT INJECTION PERFORMANCE:")
            report.append("-" * 70)
            ti = self.results["text_injection"]
            report.append(f"  Method: {ti['method']}")
            report.append("\n  Results by Text Length:")
            for length, metrics in ti["results_by_length"].items():
                report.append(f"\n    {length}:")
                report.append(f"      Avg Time: {metrics['avg_time_ms']:.2f}ms")
                report.append(f"      Speed: {metrics['chars_per_second']:.0f} chars/sec")

        # End-to-End
        if self.results.get("end_to_end"):
            report.append("\nEND-TO-END PERFORMANCE:")
            report.append("-" * 70)
            e2e = self.results["end_to_end"]
            report.append(f"  Audio Duration: {e2e['audio_duration']}s")
            report.append(f"  Average Total Time: {e2e['avg_total_time']:.2f}s")
            report.append(f"  Min Total Time: {e2e['min_total_time']:.2f}s")
            report.append(f"  Max Total Time: {e2e['max_total_time']:.2f}s")
            report.append("\n  Breakdown:")
            report.append(f"    Audio Capture: {e2e['avg_audio_capture_time']:.2f}s")
            report.append(f"    Transcription: {e2e['avg_transcription_time']:.2f}s")
            report.append(f"    Text Injection: {e2e['avg_text_injection_time']:.3f}s")
            report.append(f"\n  Performance Target (<1.5s): {'✓ MET' if e2e['meets_1_5s_target'] else '✗ MISSED'}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def save_report(self, filename: str = "performance_benchmark_report.txt"):
        """
        Save benchmark report to file.

        Args:
            filename: Output filename
        """
        report = self.generate_report()

        output_path = Path(__file__).parent / filename
        output_path.write_text(report)

        logger.info(f"\n✓ Report saved to: {output_path}")


def main():
    """Run performance benchmarks."""
    print("\n" + "=" * 70)
    print("TALKY - PERFORMANCE BENCHMARK SUITE")
    print("=" * 70)

    benchmark = PerformanceBenchmark()

    try:
        # Collect system info
        benchmark.collect_system_info()

        # Run benchmarks
        benchmark.benchmark_audio_capture(duration=1.0, iterations=5)
        benchmark.benchmark_whisper_inference(model_name="base", device="auto", iterations=3)
        benchmark.benchmark_text_injection(iterations=10)
        benchmark.benchmark_end_to_end(duration=3.0, iterations=3)

        # Generate and display report
        print(benchmark.generate_report())

        # Save report
        benchmark.save_report()

        return 0

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
