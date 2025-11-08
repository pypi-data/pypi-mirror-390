"""Factory for creating Whisper engines."""

from typing import Optional
from .base import WhisperEngine
from .faster_whisper_engine import FasterWhisperEngine


def create_whisper_engine(
    model_name: str = "base",
    language: Optional[str] = None,
    device: str = "auto",
    compute_type: str = "default"
) -> Optional[WhisperEngine]:
    """
    Create a Whisper engine instance.

    Args:
        model_name: Model size (tiny, base, small, medium, large-v3)
        language: Language code or None for auto-detect
        device: Device ("auto", "cuda", "cpu")
        compute_type: Computation type ("default", "int8", "float16")

    Returns:
        WhisperEngine instance or None if unavailable
    """
    # Try faster-whisper first (recommended)
    engine = FasterWhisperEngine(
        model_name=model_name,
        language=language,
        device=device,
        compute_type=compute_type
    )

    if engine.is_available():
        print(f"Using faster-whisper engine")
        return engine

    print("Error: No Whisper engine available")
    print("Install faster-whisper: pip install faster-whisper")
    return None
