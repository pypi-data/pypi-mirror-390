"""Abstract base class for audio capture."""

from abc import ABC, abstractmethod
from typing import Optional, Callable
import numpy as np


class AudioCapture(ABC):
    """Abstract base class for audio capture implementations."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        Initialize audio capture.

        Args:
            sample_rate: Audio sample rate in Hz (default 16000 for Whisper)
            channels: Number of audio channels (default 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self._is_recording = False
        self._audio_buffer = []

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording

    @abstractmethod
    def start(self) -> None:
        """Start audio capture."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop audio capture."""
        pass

    @abstractmethod
    def get_audio_data(self) -> Optional[np.ndarray]:
        """
        Get captured audio data.

        Returns:
            NumPy array of audio samples, or None if no data
        """
        pass

    def clear_buffer(self) -> None:
        """Clear the audio buffer."""
        self._audio_buffer = []

    def set_callback(self, callback: Optional[Callable[[np.ndarray], None]]) -> None:
        """
        Set a callback for audio data (for streaming).

        Args:
            callback: Function to call with audio chunks
        """
        pass
