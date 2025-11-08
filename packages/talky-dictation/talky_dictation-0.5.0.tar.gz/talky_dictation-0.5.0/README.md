# Talky 🎤

System-wide dictation for Linux using OpenAI's Whisper AI model.

## Overview

Talky is a system-wide dictation application for Linux, similar to WisprFlow AI on Windows/Mac. It uses OpenAI's Whisper model for accurate speech-to-text transcription and works across all applications.

**Status**: ✅ **Production Ready** | **7/7 Integration Tests Passing** | **Full GUI** | Phases 1-4 Complete

## Features

- 🎤 **Push-to-Talk**: Hold hotkey, speak, release - just like WisprFlow AI!
- 🎯 **System-wide**: Works in any application (browsers, editors, terminals, chat apps)
- ⚡ **Fast**: <1.5s latency with CUDA GPU acceleration
- 🌍 **Multi-language**: 99 languages supported with real-time switching
- 🖥️ **System Tray**: Full GUI with language selection, settings, and setup wizard
- 📝 **First-Run Wizard**: Easy configuration on first launch
- ⚙️ **Settings Dialog**: Complete GUI for all configuration options
- 🔧 **Wayland Helper**: Built-in permission checker and setup guide
- 🖥️ **X11 & Wayland**: Compatible with both display servers
- 🔒 **Privacy-focused**: Local processing, no cloud required
- 📦 **Easy Install**: Desktop integration and application menu entry

## Requirements

### System Requirements
- Linux (X11 or Wayland)
- Python 3.10+
- NVIDIA GPU with CUDA (recommended) or CPU

### External Tools
- **X11**: `xdotool` (for text injection)
- **Wayland**: `ydotool` (for text injection)

Install external tools:

```bash
# Ubuntu/Debian
sudo apt install xdotool ydotool

# Fedora
sudo dnf install xdotool ydotool

# Arch
sudo pacman -S xdotool ydotool
```

### Wayland Permissions Setup

For Wayland users, `ydotool` requires special permissions:

```bash
# Add your user to input and uinput groups
sudo usermod -aG input,uinput $USER

# Load uinput kernel module
sudo modprobe uinput

# Create udev rule for persistent access
echo 'KERNEL=="uinput", MODE="0660", GROUP="uinput", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/80-uinput.rules

# Reload udev rules
sudo udevadm control --reload-rules && sudo udevadm trigger

# Log out and back in for group changes to take effect
```

## Installation

### Option 1: Install from PyPI (Recommended - Coming Soon)

```bash
# Basic installation
pip install talky-dictation

# With GPU support
pip install talky-dictation[gpu]

# Install desktop integration (optional)
talky-install-desktop
```

### Option 2: Install from Source (Development)

```bash
# Clone repository
git clone https://github.com/ChrisKalahiki/talky.git
cd talky

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For NVIDIA GPU support
pip install faster-whisper[gpu]

# Install in editable mode
pip install -e .
```

### Desktop Integration (Optional)

Add Talky to your application menu:

```bash
# Generate icons (run once)
python scripts/generate_icons.py

# Install desktop entry and icons
./scripts/install_desktop.sh

# For system-wide installation (all users)
sudo ./scripts/install_desktop.sh
```

This installs:
- Desktop entry file (`.desktop`)
- Icons at multiple resolutions (16x16 to 256x256)
- Appears in application menu under "AudioVideo > Utility"

## Configuration

Configuration file location: `~/.config/talky/config.yaml`

Default configuration:

```yaml
audio:
  sample_rate: 16000
  channels: 1
  buffer_size: 1024

whisper:
  model: base           # tiny, base, small, medium, large-v3
  language: en          # Language code or "auto"
  device: auto          # auto, cuda, cpu
  compute_type: default

hotkeys:
  toggle_recording: "<ctrl>+<super>"  # Ctrl+Win (push-to-talk)

platform:
  prefer_method: auto   # auto, xdotool, ydotool, clipboard
  typing_delay_ms: 0
```

### Whisper Models

| Model | Size | VRAM | Speed | Accuracy |
|-------|------|------|-------|----------|
| tiny | 39MB | ~1GB | Fastest | Good |
| base | 74MB | ~1GB | Very Fast | Better |
| small | 244MB | ~2GB | Fast | High |
| medium | 769MB | ~5GB | Moderate | Very High |
| large-v3 | 1.5GB | ~10GB | Slow | Highest |

**Recommended**: Start with `base` for balanced performance.

## Usage

### Running Talky

```bash
# Run from terminal
talky

# Or if installed in development mode
python -m talky.main
```

### Basic Workflow (Push-to-Talk)

1. **Launch**: Start Talky
2. **Hold Hotkey**: Press and hold `Ctrl+Win` (or your configured hotkey)
3. **Speak**: Recording starts immediately - speak while holding
4. **Release**: Let go of the hotkey when finished speaking
5. **Wait**: Brief processing (<1.5s with GPU)
6. **Text Appears**: Transcribed text automatically inserted at cursor

**Just like WisprFlow AI** - hold to talk, release to transcribe!

### GUI Features

#### System Tray
- **Visual Status Indicators**: Icon changes color based on state (idle/recording/processing)
- **Language Selection**: Quick-switch between 99 languages via tray menu
- **Settings**: Access full configuration GUI from tray
- **About**: View version and current configuration
- **Desktop Notifications**: Get notified on transcription completion

#### First-Run Setup Wizard
On first launch, Talky guides you through:
1. Welcome and features overview
2. Platform detection and Wayland setup (if needed)
3. Whisper model and language selection
4. Configuration summary and autostart option

Skip with: `talky --skip-setup-wizard`

#### Settings Dialog
Access via tray menu → Settings:
- **General Tab**: Version info, config file location
- **Whisper Tab**: Model selection, language, device (CUDA/CPU)
- **Hotkeys Tab**: Configure push-to-talk hotkey
- **Platform Tab**: View system info (display server, DE, tools)

### CLI Options

```bash
# Standard usage
talky

# Disable system tray (headless mode)
talky --no-tray

# Check Wayland setup status
talky --wayland-setup

# Show complete Wayland setup guide
talky --wayland-setup-guide

# Autostart management
talky --enable-autostart
talky --disable-autostart
talky --autostart-status

# Skip first-run wizard
talky --skip-setup-wizard
```

## Platform Support

### X11 Support ✅
- Global hotkeys: Native support via `pynput`
- Text injection: `xdotool` (primary) or clipboard
- Works on: GNOME (X11), KDE (X11), XFCE, MATE, etc.

### Wayland Support ⚠️
- Global hotkeys: Desktop-specific (GNOME, KDE) or manual config
- Text injection: `ydotool` (requires setup) or clipboard
- Works on: GNOME (Wayland), KDE (Wayland), Sway, Hyprland

**Note**: Wayland has security restrictions that require additional setup. See [Wayland Permissions Setup](#wayland-permissions-setup) above.

## Testing & Development

### Test Suites

Comprehensive test suites are available for quality assurance:

#### Transcription Quality Tests
```bash
# Interactive tests with live microphone
python tests/test_transcription_quality.py
```

Features:
- Live recording tests with similarity metrics
- Multi-language validation
- Pass/fail criteria (80% similarity threshold)
- Automated report generation

#### Performance Benchmarking
```bash
# Benchmark all components
python tests/benchmark_performance.py
```

Measures:
- Audio capture latency (<50ms target)
- Whisper inference time by duration
- End-to-end workflow (<1.5s target)
- Memory usage tracking
- Real-time factor (RTF) calculations

#### Memory Profiling
```bash
# Profile memory usage
python tests/profile_memory.py
```

Analyzes:
- Model loading memory footprint
- Memory usage during repeated transcriptions
- Memory leak detection
- Component-level profiling

#### Integration Tests
```bash
# Run all integration tests
python tests/test_integration.py
```

Status: **7/7 tests passing** ✅

### Contributing

See `CLAUDE.md` for development guidelines and architecture overview.

## Autostart

To launch Talky automatically when you log in:

```bash
# Enable autostart
talky --enable-autostart

# Disable autostart
talky --disable-autostart

# Check status
talky --autostart-status
```

Or edit your config file (`~/.config/talky/config.yaml`):

```yaml
autostart:
  enabled: true
  delay_seconds: 5  # Wait 5 seconds after login before starting
```

**How it works:**
- Creates a `.desktop` file in `~/.config/autostart/`
- Uses the standard XDG Autostart specification
- Works across all Linux desktop environments (GNOME, KDE, XFCE, etc.)
- You can also manage it via your desktop's "Startup Applications" settings

**Notes:**
- Autostart is **disabled by default** (opt-in)
- Requires system tray mode (autostart won't work with `--no-tray`)
- Desktop file automatically updates when you upgrade Talky

## Troubleshooting

### No audio capture
```bash
# Check audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test PipeWire/PulseAudio
pactl list sources
```

### Text not injecting (X11)
```bash
# Install xdotool
sudo apt install xdotool

# Test manually
xdotool type "test"
```

### Text not injecting (Wayland)
```bash
# Check ydotool service
systemctl --user status ydotool

# Verify permissions
groups | grep -E 'input|uinput'

# Test manually
ydotool type "test"
```

### CUDA not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Verify CUDA installation
python -c "import torch; print(torch.cuda.is_available())"
```

## Project Structure

```
talky/
├── src/talky/
│   ├── audio/          # Audio capture
│   ├── whisper/        # Whisper integration
│   ├── input/          # Text injection
│   ├── hotkeys/        # Hotkey management
│   ├── ui/             # System tray & UI
│   └── utils/          # Config, logging, platform
├── config/             # Default configuration
├── tests/              # Test suite
├── PROJECT_PLAN.md     # Development roadmap
└── README.md           # This file
```

## Development Status

### Phase 1: Core Foundation ✅ **Complete**
- [x] Project structure w/ modular architecture
- [x] Platform detection (X11/Wayland/DE/CUDA)
- [x] Abstract interfaces (AudioCapture, TextInjector, HotkeyManager)
- [x] YAML configuration system
- [x] Audio capture (sounddevice, 16kHz mono)

### Phase 2: Platform Backends ✅ **Complete**
- [x] X11 text injection (xdotool → pynput → clipboard fallback)
- [x] Wayland text injection (ydotool → clipboard fallback)
- [x] X11 hotkeys (pynput global listener)
- [x] Wayland hotkeys (DE-specific + manual compositor config)
- [x] Push-to-talk implementation (on_press/on_release callbacks)

### Phase 3: Whisper Integration ✅ **Complete**
- [x] faster-whisper engine w/ CUDA support
- [x] Multi-language support (99 languages)
- [x] Model management & caching (~/.cache/talky/models/)
- [x] Voice Activity Detection (VAD)
- [x] Main application orchestrator (main.py)
- [x] Full end-to-end pipeline working

**Integration Tests**: ✅ **7/7 Passing**
1. Configuration System ✓
2. Platform Detection ✓
3. Audio Capture ✓
4. Whisper Engine ✓
5. Text Injector ✓
6. Hotkey Manager (Push-to-Talk) ✓
7. End-to-End Workflow ✓

### Phase 4: UI & Polish ⏳ **Not Started**
- [ ] System tray interface (pystray)
- [ ] Desktop notifications
- [ ] Settings GUI
- [ ] Visual recording state indicator

### Phase 5: Packaging ⏳ **Not Started**
- [ ] PyPI distribution
- [ ] AppImage build
- [ ] Distribution packages (deb/rpm/AUR)
- [ ] Systemd user service

## Contributing

Contributions welcome! See [PROJECT_PLAN.md](PROJECT_PLAN.md) for development roadmap.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- Inspired by [WisprFlow AI](https://www.wisprflow.ai/)

## Project Status

### Development Phases

- ✅ **Phase 1**: Core Foundation (Config, Platform Detection, Interfaces)
- ✅ **Phase 2**: Platform Backends (X11/Wayland Text Injection & Hotkeys)
- ✅ **Phase 3**: Whisper Integration (faster-whisper, Multi-language, CUDA)
- ✅ **Phase 4**: UI & Integration (System Tray, Settings GUI, Setup Wizard)
- 🚧 **Phase 5**: Testing & Packaging (In Progress - High-priority items complete)

### What's Working

- ✅ Push-to-talk dictation on X11 and Wayland
- ✅ 99 language support with real-time switching
- ✅ CUDA GPU acceleration (<1.5s transcription)
- ✅ System tray with visual indicators
- ✅ Complete settings GUI and first-run wizard
- ✅ Desktop integration (app menu, icons)
- ✅ Wayland setup checker and guide
- ✅ Comprehensive test suites (quality, performance, memory)
- ✅ 7/7 integration tests passing
- ✅ PyPI-ready packaging (pyproject.toml)

### What's Next

- ⏳ Cross-platform validation (Ubuntu, Fedora, Arch)
- ⏳ Application compatibility testing
- ⏳ Native packages (.deb, .rpm, AUR)
- ⏳ AppImage build
- ⏳ PyPI publication

See `PROJECT_PLAN.md` for detailed roadmap.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ChrisKalahiki/talky/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ChrisKalahiki/talky/discussions)
- 📧 **Email**: your.email@example.com

---

Made with ❤️ for the Linux community
