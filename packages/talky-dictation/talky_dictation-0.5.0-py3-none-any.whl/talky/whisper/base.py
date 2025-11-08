"""Abstract base class for Whisper speech recognition engines."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np


class WhisperEngine(ABC):
    """Abstract base class for Whisper implementations."""

    def __init__(
        self,
        model_name: str = "base",
        language: Optional[str] = None,
        device: str = "auto"
    ):
        """
        Initialize Whisper engine.

        Args:
            model_name: Model size (tiny, base, small, medium, large-v3)
            language: Language code (e.g., "en", "es") or None for auto-detect
            device: Device to use ("auto", "cuda", "cpu")
        """
        self.model_name = model_name
        self.language = language
        self.device = device
        self._model = None
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded

    @abstractmethod
    def load_model(self) -> bool:
        """
        Load the Whisper model.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def unload_model(self) -> None:
        """Unload the model from memory."""
        pass

    @abstractmethod
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
            Dictionary with:
                - text: Transcribed text
                - language: Detected/used language
                - segments: List of segments with timing info (optional)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this engine is available.

        Returns:
            True if engine can be used, False otherwise
        """
        pass
