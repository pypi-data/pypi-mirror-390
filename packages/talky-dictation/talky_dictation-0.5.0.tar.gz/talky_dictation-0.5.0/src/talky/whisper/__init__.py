"""Whisper speech recognition integration."""

from .base import WhisperEngine
from .faster_whisper_engine import FasterWhisperEngine
from .factory import create_whisper_engine
from .languages import (
    WHISPER_LANGUAGES,
    POPULAR_LANGUAGES,
    get_language_name,
    get_all_languages,
    get_popular_languages,
    is_valid_language,
)

__all__ = [
    "WhisperEngine",
    "FasterWhisperEngine",
    "create_whisper_engine",
    "WHISPER_LANGUAGES",
    "POPULAR_LANGUAGES",
    "get_language_name",
    "get_all_languages",
    "get_popular_languages",
    "is_valid_language",
]
