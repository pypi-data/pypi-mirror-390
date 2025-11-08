"""faster-whisper implementation for speech recognition."""

import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
from .base import WhisperEngine


class FasterWhisperEngine(WhisperEngine):
    """Whisper engine using faster-whisper library."""

    def __init__(
        self,
        model_name: str = "base",
        language: Optional[str] = None,
        device: str = "auto",
        compute_type: str = "default"
    ):
        """
        Initialize faster-whisper engine.

        Args:
            model_name: Model size (tiny, base, small, medium, large-v3)
            language: Language code or None for auto-detect
            device: Device ("auto", "cuda", "cpu")
            compute_type: Computation type ("default", "int8", "float16")
        """
        super().__init__(model_name, language, device)
        self.compute_type = compute_type
        self._actual_device = None
        self._actual_compute_type = None

    def _determine_device_and_compute_type(self) -> tuple[str, str]:
        """Determine actual device and compute type to use."""
        if self.device == "auto":
            # Check for CUDA availability
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"
                    compute_type = "float16" if self.compute_type == "default" else self.compute_type
                else:
                    device = "cpu"
                    compute_type = "int8" if self.compute_type == "default" else self.compute_type
            except ImportError:
                device = "cpu"
                compute_type = "int8"
        else:
            device = self.device
            if self.compute_type == "default":
                compute_type = "float16" if device == "cuda" else "int8"
            else:
                compute_type = self.compute_type

        return device, compute_type

    def load_model(self) -> bool:
        """
        Load the faster-whisper model.

        Returns:
            True if successful, False otherwise
        """
        if self._is_loaded:
            return True

        try:
            from faster_whisper import WhisperModel

            # Determine device and compute type
            device, compute_type = self._determine_device_and_compute_type()
            self._actual_device = device
            self._actual_compute_type = compute_type

            print(f"Loading Whisper model: {self.model_name}")
            print(f"  Device: {device}")
            print(f"  Compute Type: {compute_type}")

            # Load model
            self._model = WhisperModel(
                self.model_name,
                device=device,
                compute_type=compute_type,
                download_root=self._get_model_cache_dir(),
                local_files_only=False  # Allow downloading models
            )

            self._is_loaded = True
            print(f"✓ Model loaded successfully")
            return True

        except ImportError as e:
            print(f"Error: faster-whisper not installed: {e}")
            print("Install with: pip install faster-whisper")
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def unload_model(self) -> None:
        """Unload the model from memory."""
        if self._model:
            # faster-whisper doesn't have explicit unload
            # Just delete the reference and let garbage collection handle it
            self._model = None
            self._is_loaded = False
            print("Model unloaded")

    def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Args:
            audio: Audio data as numpy array (float32, 16kHz)
            language: Override language for this transcription

        Returns:
            Dictionary with transcription results
        """
        if not self._is_loaded:
            if not self.load_model():
                return {"text": "", "language": "en", "error": "Model not loaded"}

        try:
            # Use provided language or instance language
            lang = language or self.language

            # Transcribe
            segments, info = self._model.transcribe(
                audio,
                language=lang,
                beam_size=5,
                vad_filter=True,  # Voice activity detection
                vad_parameters={
                    "threshold": 0.5,
                    "min_speech_duration_ms": 250,
                    "min_silence_duration_ms": 100,
                }
            )

            # Collect all segments
            text_segments = []
            full_text = []

            for segment in segments:
                text_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                })
                full_text.append(segment.text.strip())

            # Combine text
            transcribed_text = " ".join(full_text)

            return {
                "text": transcribed_text,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": text_segments,
            }

        except Exception as e:
            print(f"Transcription error: {e}")
            return {"text": "", "language": "en", "error": str(e)}

    def is_available(self) -> bool:
        """
        Check if faster-whisper is available.

        Returns:
            True if available, False otherwise
        """
        try:
            import faster_whisper
            return True
        except ImportError:
            return False

    def _get_model_cache_dir(self) -> Path:
        """Get the directory for caching models."""
        import os

        # Use XDG_CACHE_HOME if available
        cache_home = os.environ.get("XDG_CACHE_HOME")
        if cache_home:
            cache_dir = Path(cache_home)
        else:
            cache_dir = Path.home() / ".cache"

        model_cache = cache_dir / "talky" / "models"
        model_cache.mkdir(parents=True, exist_ok=True)

        return model_cache

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "device": self._actual_device,
            "compute_type": self._actual_compute_type,
            "is_loaded": self._is_loaded,
            "language": self.language,
        }
