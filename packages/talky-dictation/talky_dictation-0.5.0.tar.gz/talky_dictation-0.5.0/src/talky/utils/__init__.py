"""Utility modules (config, logging, platform detection)."""

from .platform import PlatformDetector
from .config import Config

__all__ = ["PlatformDetector", "Config"]
