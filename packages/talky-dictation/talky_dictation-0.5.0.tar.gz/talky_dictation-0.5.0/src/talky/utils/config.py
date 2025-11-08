"""Configuration management for Talky."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class AudioConfig:
    """Audio configuration."""
    sample_rate: int = 16000
    channels: int = 1
    buffer_size: int = 1024


@dataclass
class WhisperConfig:
    """Whisper model configuration."""
    model: str = "base"
    language: str = "en"
    device: str = "auto"  # auto, cuda, cpu
    compute_type: str = "default"  # default, int8, float16


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""
    toggle_recording: str = "<ctrl>+<super>"


@dataclass
class PlatformConfig:
    """Platform-specific configuration."""
    prefer_method: str = "auto"  # auto, xdotool, ydotool, clipboard
    typing_delay_ms: int = 0


@dataclass
class AutostartConfig:
    """Autostart configuration."""
    enabled: bool = False
    delay_seconds: int = 5


@dataclass
class Config:
    """Main configuration class."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    hotkeys: HotkeyConfig = field(default_factory=HotkeyConfig)
    platform: PlatformConfig = field(default_factory=PlatformConfig)
    autostart: AutostartConfig = field(default_factory=AutostartConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        return cls(
            audio=AudioConfig(**data.get("audio", {})),
            whisper=WhisperConfig(**data.get("whisper", {})),
            hotkeys=HotkeyConfig(**data.get("hotkeys", {})),
            platform=PlatformConfig(**data.get("platform", {})),
            autostart=AutostartConfig(**data.get("autostart", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "audio": asdict(self.audio),
            "whisper": asdict(self.whisper),
            "hotkeys": asdict(self.hotkeys),
            "platform": asdict(self.platform),
            "autostart": asdict(self.autostart),
        }

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from file.

        Args:
            config_path: Path to config file. If None, uses default location.

        Returns:
            Config instance
        """
        if config_path is None:
            config_path = cls.get_default_config_path()

        if not config_path.exists():
            # Return default config
            return cls()

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                return cls.from_dict(data or {})
        except Exception as e:
            print(f"Error loading config: {e}")
            return cls()

    def save(self, config_path: Optional[Path] = None) -> bool:
        """
        Save configuration to file.

        Args:
            config_path: Path to save config. If None, uses default location.

        Returns:
            True if successful, False otherwise
        """
        if config_path is None:
            config_path = self.get_default_config_path()

        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    @staticmethod
    def get_default_config_path() -> Path:
        """Get default configuration file path."""
        # Use XDG_CONFIG_HOME if available, otherwise ~/.config
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            config_dir = Path(config_home)
        else:
            config_dir = Path.home() / ".config"

        return config_dir / "talky" / "config.yaml"

    @staticmethod
    def get_default_config_content() -> str:
        """Get default configuration file content as YAML string."""
        default_config = Config()
        return yaml.dump(default_config.to_dict(), default_flow_style=False)
