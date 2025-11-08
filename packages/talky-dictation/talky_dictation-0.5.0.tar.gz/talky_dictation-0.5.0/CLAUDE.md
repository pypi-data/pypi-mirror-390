# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Talky is a system-wide dictation application for Linux using OpenAI's Whisper AI for speech-to-text. It provides **push-to-talk** functionality similar to WisprFlow AI on Windows/Mac. Users hold a hotkey (default: Ctrl+Win), speak, then release to have text automatically transcribed and injected at their cursor position.

**Key Design Philosophy**: Platform-aware with graceful degradation. X11 is the primary target with full Wayland support implemented but requires additional setup due to Wayland's security model.

## Development Setup

### Prerequisites
```bash
# System dependencies (X11 - primary target)
sudo apt install xdotool  # or: dnf/pacman equivalent

# Python 3.10+ required
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# For GPU acceleration (recommended)
pip install faster-whisper[gpu]
```

### Hugging Face Authentication
Talky auto-loads environment variables from `.env` in the project root. Create a `.env` file with:
```
HF_TOKEN=hf_your_token_here
```

The token is needed on first run to download Whisper models from Hugging Face. See `HUGGINGFACE_SETUP.md` for details.

### Running the Application
```bash
# Run Talky
python -m talky.main

# Or if installed
talky
```

## Testing

### Run All Tests
```bash
# Comprehensive integration tests (non-interactive)
python tests/test_integration.py

# Platform-specific tests
python tests/test_noninteractive.py

# Individual component tests
python tests/test_platform.py  # Interactive, requires user input
python tests/test_whisper.py   # Interactive, requires microphone
```

### Test Individual Components
```python
# Test platform detection
python -c "from talky.utils.platform import get_platform_detector; print(get_platform_detector().get_platform_summary())"

# Test audio capture
python -c "from talky.audio import SoundDeviceCapture; c = SoundDeviceCapture(); c.start(); import time; time.sleep(1); c.stop(); print('OK')"

# Test text injection (X11 only - will type in 5 seconds)
python -c "from talky.input import create_text_injector; import time; i = create_text_injector(); time.sleep(5); i.inject_text('Test from Talky')"
```

## Architecture

### Core Design Pattern: Factory + Abstract Interfaces

The codebase uses **factory functions** that return platform-specific implementations of abstract base classes. This enables automatic platform detection and graceful fallback:

```
Factory Function → Platform Detection → Concrete Implementation
     ↓                    ↓                      ↓
create_text_injector() → X11? → X11TextInjector (xdotool → pynput)
                      → Wayland? → WaylandTextInjector (ydotool → clipboard)
```

### Key Architectural Components

#### 1. **Platform Detection** (`utils/platform.py`)
Runtime detection of:
- Display server (X11/Wayland) via `XDG_SESSION_TYPE`
- Desktop environment (GNOME/KDE/Sway/etc)
- Available tools (xdotool, ydotool, CUDA)

**Critical**: All platform-specific code must check `PlatformDetector` first.

#### 2. **Text Injection Pipeline** (`input/`)
Hierarchical fallback system:
- **X11**: `xdotool` (subprocess) → `pynput` (library) → clipboard
- **Wayland**: `ydotool` (subprocess, requires uinput perms) → clipboard + notification

Factory: `create_text_injector()` → auto-selects based on platform

#### 3. **Hotkey Management** (`hotkeys/`)
**Push-to-Talk Implementation**: Separate `on_press` and `on_release` callbacks
- **X11**: `pynput` tracks key combinations, fires callbacks on exact match
- **Wayland**: Limited support, requires manual compositor config or DE-specific APIs

**Critical Detail**: X11HotkeyManager tracks `_active_hotkeys` set to prevent callback repeat while holding keys.

#### 4. **Audio Pipeline** (`audio/`)
```
Microphone → sounddevice (16kHz mono) → ring buffer → Whisper → Text
```
- Uses **sounddevice** for cross-platform audio (detects PipeWire/PulseAudio automatically)
- Configured for Whisper's requirement: 16kHz, mono, float32

#### 5. **Whisper Integration** (`whisper/`)
**Implementation**: `faster-whisper` with CTranslate2 backend for 4x speed improvement

Key features:
- Automatic CUDA/CPU selection based on hardware
- Model caching in `~/.cache/talky/models/`
- Voice Activity Detection (VAD) to filter silence
- Models stay resident in memory for <1s transcription

**Device Selection Logic**:
```python
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
```

### Main Application Flow (`main.py`)

```
1. Load .env (for HF_TOKEN)
2. Initialize config from ~/.config/talky/config.yaml
3. Platform detection
4. Component initialization (audio, whisper, injector, hotkeys)
5. Register hotkey with on_press=start_recording, on_release=stop_recording
6. Main loop (listens for hotkey events)
```

**Push-to-Talk Workflow**:
```
Press Ctrl+Win → on_press() → start_recording()
    ↓
Hold & Speak → audio buffer fills
    ↓
Release → on_release() → stop_recording() → transcribe() → inject_text()
```

## Configuration System

**Location**: `~/.config/talky/config.yaml` (auto-created from `config/default.yaml`)

**Implementation**: Dataclass-based config with YAML serialization (`utils/config.py`)

Key settings:
- `whisper.model`: Model size (tiny/base/small/medium/large-v3)
- `whisper.device`: "auto" (CUDA if available, else CPU), "cuda", "cpu"
- `hotkeys.toggle_recording`: Hotkey string (e.g., `"<ctrl>+<super>"`)
- `platform.prefer_method`: Force injection method ("auto", "xdotool", "ydotool", "clipboard")

## Platform-Specific Considerations

### X11 (Primary Target)
- **Text Injection**: Uses `xdotool` subprocess by default, falls back to `pynput`
- **Hotkeys**: Native global hotkey support via `pynput.keyboard.Listener`
- **No special permissions needed**

### Wayland (Secondary Support)
- **Text Injection**: `ydotool` requires user in `input`/`uinput` groups + udev rules
- **Hotkeys**: No universal solution. Implementations:
  - Manual: Add bindings to Sway/i3/Hyprland config
  - GNOME/KDE: D-Bus integration (stub implemented, needs completion)
  - Fallback: System tray button (not yet implemented)

**Critical**: Wayland support is functional but requires user setup. Always provide clear error messages with setup instructions.

## Common Development Tasks

### Adding a New Whisper Language
Languages are defined in `whisper/languages.py`:
1. Add to `WHISPER_LANGUAGES` dict with language code and name
2. Optionally add to `POPULAR_LANGUAGES` for quick access
3. Automatically appears in tray menu and settings dialog

### Adding a New Whisper Model Size
1. Add model name to `SettingsDialog.WHISPER_MODELS` in `ui/settings.py`
2. User can select it from settings dialog or edit config directly
3. Model downloads automatically on first use

### Supporting a New Desktop Environment
1. Add enum to `DesktopEnvironment` in `utils/platform.py`
2. Update `_detect_desktop_environment()` detection logic
3. If Wayland: Add manual setup instructions to `hotkeys/wayland.py`
4. Update platform info tab in `ui/settings.py` if needed

### Debugging Audio Issues
```bash
# List audio devices
python -c "from talky.audio import SoundDeviceCapture; print(SoundDeviceCapture.list_devices())"

# Check default device
python -c "from talky.audio import SoundDeviceCapture; print(SoundDeviceCapture.get_default_device())"
```

### Debugging Hotkey Issues
The `on_press`/`on_release` callbacks are the critical path. Add debug prints in:
- `hotkeys/x11.py`: `_on_press()` and `_on_release()` methods
- Check `_current_keys` set and `_active_hotkeys` set for state tracking

### Using the Settings GUI
The Settings dialog (`ui/settings.py`) provides a tabbed interface for configuration:
- **General**: Version info, config file location
- **Whisper**: Model selection, language, device (CUDA/CPU)
- **Hotkeys**: Push-to-talk hotkey configuration
- **Platform**: Display server, DE, available tools

Access via:
1. System tray menu → Settings
2. First-run wizard (automatic on first launch)

### Language Selection
99 Whisper languages supported via `whisper/languages.py`:
- Popular languages listed first in tray menu
- All languages sorted alphabetically
- Real-time switching without restart
- Language persisted in config

### Wayland Setup Verification
Check Wayland permissions and dependencies:
```bash
# Check setup status
python -m talky --wayland-setup

# Show complete setup guide
python -m talky --wayland-setup-guide
```

The checker validates:
- ydotool installation
- Group membership (input, uinput)
- udev rules configuration
- uinput kernel module

## Critical Implementation Details

### Why Push-to-Talk?
Original design was toggle (press once to start, press again to stop). Changed to match WisprFlow AI's UX:
- More intuitive for dictation
- Prevents accidentally leaving mic on
- Better for quick insertions

Implementation requires tracking hotkey state to fire callbacks only once per press/release cycle.

### Why Factory Functions?
Direct imports would require conditional logic at every call site. Factories centralize platform detection:
```python
# Good (one detection point)
injector = create_text_injector()  # Auto-detects platform

# Bad (scattered detection)
from talky.utils.platform import is_x11
if is_x11():
    from talky.input.x11 import X11TextInjector
    injector = X11TextInjector()
```

### Model Caching Strategy
Whisper models (140MB-1.5GB) are cached in `~/.cache/talky/models/`. The `FasterWhisperEngine` keeps the model **resident in memory** between transcriptions for sub-second latency. Only unloaded on app shutdown.

### Error Handling Philosophy
**Fail gracefully with actionable error messages**. Examples:
- Missing xdotool → "Install with: sudo apt install xdotool"
- No CUDA → Auto-fallback to CPU with message
- Wayland without ydotool → Show clipboard fallback option

## Performance Targets

- Audio capture latency: <50ms ✓
- Whisper inference (base model, CUDA): 0.5-1s ✓
- Text injection: <100ms ✓
- **Total end-to-end: <1.5s** (measured from hotkey release to text appearance)

## Known Limitations

1. **Wayland global hotkeys**: No universal solution due to security model. Compositor-specific workarounds required. Use `--wayland-setup` to check configuration.
2. **Model download**: Requires Hugging Face token on first run if using private/gated models (public models work without auth after clearing stale tokens).
3. **Voice commands**: Not implemented (e.g., "new line", "delete that"). Pure transcription only.
4. **Hotkey changes**: Require restarting Talky to take effect (limitation of pynput library).

## Project Status

**Current Phase**: Phase 4 Complete (All 7 integration tests passing + Full GUI)
- ✅ Core foundation (config, platform detection, abstract interfaces)
- ✅ Platform backends (X11 text injection, X11 hotkeys, Wayland stubs)
- ✅ Whisper integration (faster-whisper, CUDA support, model caching)
- ✅ Main application (push-to-talk workflow)
- ✅ Phase 4: System tray UI with full settings and setup wizard
- ⏳ Phase 5: Testing & Packaging (not started)

**Production Ready**: Yes, for X11 systems with GPU. Full GUI with tray, settings, and wizard. Wayland requires user setup.
