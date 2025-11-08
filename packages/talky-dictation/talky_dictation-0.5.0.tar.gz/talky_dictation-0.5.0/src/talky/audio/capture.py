"""Audio capture implementation using sounddevice."""

import numpy as np
import sounddevice as sd
from typing import Optional, Callable
from .base import AudioCapture


class SoundDeviceCapture(AudioCapture):
    """Audio capture using sounddevice library."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1, buffer_size: int = 1024):
        """
        Initialize sounddevice audio capture.

        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
            buffer_size: Size of audio buffer
        """
        super().__init__(sample_rate, channels)
        self.buffer_size = buffer_size
        self._stream: Optional[sd.InputStream] = None
        self._callback_func: Optional[Callable[[np.ndarray], None]] = None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"Audio callback status: {status}")

        # Copy audio data to buffer
        audio_data = indata.copy()

        # Store in buffer
        self._audio_buffer.append(audio_data)

        # Call user callback if set
        if self._callback_func:
            self._callback_func(audio_data)

    def start(self) -> None:
        """Start audio capture."""
        if self._is_recording:
            return

        try:
            self._audio_buffer = []
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.buffer_size,
                callback=self._audio_callback,
                dtype=np.float32
            )
            self._stream.start()
            self._is_recording = True
        except Exception as e:
            print(f"Error starting audio capture: {e}")
            raise

    def stop(self) -> None:
        """Stop audio capture."""
        if not self._is_recording:
            return

        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            self._is_recording = False
        except Exception as e:
            print(f"Error stopping audio capture: {e}")
            raise

    def get_audio_data(self) -> Optional[np.ndarray]:
        """
        Get captured audio data as a single array.

        Returns:
            NumPy array of audio samples, or None if no data
        """
        if not self._audio_buffer:
            return None

        # Concatenate all audio chunks
        audio_data = np.concatenate(self._audio_buffer, axis=0)

        # Convert to 1D array if mono
        if self.channels == 1:
            audio_data = audio_data.flatten()

        return audio_data

    def set_callback(self, callback: Optional[Callable[[np.ndarray], None]]) -> None:
        """
        Set a callback for audio data streaming.

        Args:
            callback: Function to call with audio chunks
        """
        self._callback_func = callback

    @staticmethod
    def list_devices() -> list:
        """List available audio input devices."""
        try:
            devices = sd.query_devices()
            return [d for d in devices if d['max_input_channels'] > 0]
        except Exception as e:
            print(f"Error listing devices: {e}")
            return []

    @staticmethod
    def get_default_device():
        """Get default input device."""
        try:
            return sd.query_devices(kind='input')
        except Exception as e:
            print(f"Error getting default device: {e}")
            return None
