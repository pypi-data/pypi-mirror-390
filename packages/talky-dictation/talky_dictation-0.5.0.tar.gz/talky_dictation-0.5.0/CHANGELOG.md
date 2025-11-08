# Changelog

All notable changes to Talky will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- PyPI publication
- .deb package for Debian/Ubuntu
- .rpm package for Fedora/RHEL
- AUR package for Arch Linux
- AppImage build
- Systemd user service template
- Cross-platform testing (Ubuntu, Fedora, Arch)
- Application compatibility matrix

## [0.5.0] - 2025-11-06

### Added - Phase 5: Testing & Packaging (High-Priority Items)
- **Test Suites**:
  - Real-world transcription quality test suite (`test_transcription_quality.py`)
  - Performance benchmarking suite (`benchmark_performance.py`)
  - Memory profiling suite (`profile_memory.py`)
  - All test suites generate detailed reports

- **PyPI Packaging**:
  - Modern `pyproject.toml` configuration (PEP 517/518 compliant)
  - Simplified `setup.py` for backward compatibility
  - `MANIFEST.in` for package data inclusion
  - Complete PyPI publishing guide (`PYPI_PUBLISHING.md`)
  - Package name: `talky-dictation`
  - Optional dependencies: `[gpu]`, `[dev]`, `[test]`

- **Desktop Integration**:
  - FreeDesktop-compliant desktop entry file (`talky.desktop`)
  - Icon generation script (`generate_icons.py`) - creates 8 standard sizes
  - Desktop installation script (`install_desktop.sh`)
  - Application menu integration
  - Icons follow hicolor icon theme structure

### Changed
- Package configuration migrated from setup.py to pyproject.toml
- setup.py simplified (delegates to pyproject.toml)
- Updated PROJECT_PLAN.md with Phase 5 progress
- Updated README.md with new features and installation methods

## [0.4.0] - 2025-11-06

### Added - Phase 4: UI & Integration
- **Language System**:
  - Comprehensive language definitions for 99 Whisper languages (`languages.py`)
  - Popular languages section in tray menu
  - Real-time language switching without restart

- **System Tray**:
  - Enhanced tray menu with language selection submenu
  - Settings menu option
  - About dialog with current configuration
  - Visual state indicators (idle, recording, processing)

- **Settings GUI**:
  - Full settings dialog with 4 tabs (`settings.py`):
    - General: Version info, config location
    - Whisper: Model, language, device selection
    - Hotkeys: Hotkey configuration
    - Platform: System information and available tools
  - Apply/Save/Cancel button workflow
  - Live configuration updates

- **First-Run Setup Wizard**:
  - 4-page guided setup (`setup_wizard.py`):
    - Welcome and features overview
    - Platform detection and Wayland warnings
    - Whisper configuration
    - Final summary and autostart option
  - Setup completion marker (`.setup_complete`)
  - Skip option: `--skip-setup-wizard`

- **Wayland Support Tools**:
  - Comprehensive permission checker (`wayland_setup.py`)
  - Validates: ydotool, groups, udev rules, kernel module
  - CLI options: `--wayland-setup`, `--wayland-setup-guide`
  - Detailed setup guide with actionable instructions

### Changed
- Version bumped to 0.4.0
- Hotkey default changed from `<ctrl>+<shift>+space` to `<ctrl>+<super>` (Ctrl+Win)
- Tray menu restructured with new options
- Updated CLAUDE.md with UI usage documentation
- Updated PROJECT_PLAN.md marking Phase 4 complete

### Fixed
- Language configuration now properly persists to config file
- Whisper engine language updates in real-time

## [0.3.0] - 2025-10-28

### Added - Phase 3: Whisper Integration
- **Whisper Engine**:
  - FasterWhisperEngine with CTranslate2 backend (4x speed improvement)
  - Automatic CUDA/CPU selection based on hardware
  - Model caching in `~/.cache/talky/models/`
  - Voice Activity Detection (VAD) to filter silence
  - Models stay resident in memory for <1s transcription

- **Multi-Language Support**:
  - Language selection in config (99 languages supported)
  - Auto-detect mode available
  - Per-transcription language override

- **Main Application**:
  - Complete orchestrator (`main.py`)
  - Push-to-talk workflow implementation
  - End-to-end pipeline: Audio → Whisper → Text Injection
  - Autostart management (enable/disable/status)

- **Testing**:
  - Comprehensive integration test suite (`test_integration.py`)
  - 7/7 tests passing:
    1. Configuration System
    2. Platform Detection
    3. Audio Capture
    4. Whisper Engine
    5. Text Injector
    6. Hotkey Manager (Push-to-Talk)
    7. End-to-End Workflow Simulation

### Performance
- Audio capture latency: <50ms ✓
- Whisper inference: 0.5-1s (base model, CUDA) ✓
- Text injection: <100ms ✓
- Total end-to-end: <1.5s target achieved ✓

## [0.2.0] - 2025-10-28

### Added - Phase 2: Platform-Specific Backends
- **X11 Text Injection**:
  - xdotool subprocess wrapper (primary)
  - pynput keyboard controller fallback
  - Factory function with automatic fallback

- **Wayland Text Injection**:
  - ydotool subprocess wrapper (primary)
  - Permission checking for uinput
  - Clipboard + paste notification fallback
  - Unified WaylandTextInjector with auto-fallback

- **X11 Hotkey Management**:
  - Global hotkey listener using pynput
  - Default hotkey: Ctrl+Win (Super)
  - Configurable via YAML
  - Key combination parsing

- **Wayland Hotkey Management**:
  - Setup instructions for compositor-based WMs
  - Framework for GNOME/KDE integration (D-Bus stubs)
  - Manual configuration guide generator
  - Notification system for setup requirements

- **Testing**:
  - Platform-specific test scripts
  - Clipboard injection with automatic paste simulation

## [0.1.0] - 2025-10-28

### Added - Phase 1: Core Foundation
- **Project Structure**:
  - Complete directory structure (audio, whisper, input, hotkeys, ui, utils)
  - Python package setup with src/ layout
  - requirements.txt and setup.py

- **Platform Detection**:
  - Runtime detection of display server (X11/Wayland)
  - Desktop environment detection (GNOME/KDE/Sway/etc)
  - Available tools detection (xdotool, ydotool, CUDA)

- **Abstract Interfaces**:
  - AudioCapture base class
  - TextInjector base class
  - HotkeyManager base class
  - Factory pattern for platform-specific implementations

- **Configuration System**:
  - Dataclass-based config with YAML serialization
  - Default config in `config/default.yaml`
  - User config in `~/.config/talky/config.yaml`
  - Auto-creation from defaults

- **Audio Capture**:
  - SoundDeviceCapture implementation
  - 16kHz mono capture (Whisper requirement)
  - Ring buffer for audio storage
  - PipeWire/PulseAudio support

- **Documentation**:
  - Comprehensive README.md
  - CLAUDE.md for development guidance
  - PROJECT_PLAN.md with phase breakdown
  - HUGGINGFACE_SETUP.md for model authentication

### Infrastructure
- Environment variable loading from .env (HF_TOKEN support)
- Logging configuration
- Error handling framework

---

## Version History Summary

- **0.5.0**: Testing & packaging (high-priority items)
- **0.4.0**: Full GUI with system tray, settings, wizard
- **0.3.0**: Whisper integration, end-to-end pipeline working
- **0.2.0**: Platform backends (X11/Wayland support)
- **0.1.0**: Core foundation, platform detection, abstractions

[Unreleased]: https://github.com/ChrisKalahiki/talky/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/ChrisKalahiki/talky/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/ChrisKalahiki/talky/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ChrisKalahiki/talky/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ChrisKalahiki/talky/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ChrisKalahiki/talky/releases/tag/v0.1.0
