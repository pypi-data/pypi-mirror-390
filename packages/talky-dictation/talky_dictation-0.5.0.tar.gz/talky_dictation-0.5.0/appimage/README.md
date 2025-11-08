# AppImage Packaging for Talky

This directory contains the build script for creating an **AppImage** package for Talky. AppImage is a universal Linux package format that runs on most distributions without installation.

## What is AppImage?

AppImage is a format for distributing portable software on Linux:
- **No installation required** - just download and run
- **Works on most distributions** - Ubuntu, Fedora, Arch, Debian, openSUSE, etc.
- **Self-contained** - bundles all dependencies
- **No root access needed** - runs from user directory
- **Distribution agnostic** - one file works everywhere

## Quick Start

### For Users (Downloading Pre-built AppImage)

```bash
# Download AppImage (from GitHub Releases)
wget https://github.com/ChrisKalahiki/talky/releases/download/v0.5.0/Talky-0.5.0-x86_64.AppImage

# Make executable
chmod +x Talky-0.5.0-x86_64.AppImage

# Run
./Talky-0.5.0-x86_64.AppImage
```

### For Developers (Building AppImage)

```bash
cd appimage/
./build-appimage.sh
```

## Prerequisites

### For Building

**appimagetool** (required):
```bash
# Download latest release
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage

# Make executable and install
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

**Build dependencies**:
```bash
# Ubuntu/Debian
sudo apt install python3 python3-venv python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

### For Running

**System dependencies** (usually already installed):
- X11 or Wayland display server
- glibc 2.31+ (most modern distributions)
- gtk3 (for system tray)

## Building the AppImage

### Automated Build

```bash
cd appimage/
./build-appimage.sh
```

This script will:
1. Create AppDir structure
2. Install Python virtual environment
3. Install Talky and all dependencies
4. Copy external tools (xdotool)
5. Generate icons
6. Create AppRun launcher script
7. Build AppImage with appimagetool

### Build Output

After successful build:
```
appimage/Talky-0.5.0-x86_64.AppImage  (~300-500MB)
```

The AppImage is self-contained with:
- Python 3.10+ interpreter
- All Python dependencies (faster-whisper, torch, sounddevice, etc.)
- Talky application
- xdotool (for X11 text injection)
- Icons and desktop file

## Using the AppImage

### Running

```bash
# Direct execution
./Talky-0.5.0-x86_64.AppImage

# With arguments
./Talky-0.5.0-x86_64.AppImage --help
./Talky-0.5.0-x86_64.AppImage --wayland-setup
```

### Installing to System

```bash
# Copy to local bin
mkdir -p ~/.local/bin
cp Talky-0.5.0-x86_64.AppImage ~/.local/bin/Talky.AppImage
chmod +x ~/.local/bin/Talky.AppImage

# Add to PATH (if not already)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Run from anywhere
Talky.AppImage
```

### Desktop Integration

AppImages can integrate with application menus:

**Method 1: AppImageLauncher (Recommended)**
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:appimagelauncher-team/stable
sudo apt update
sudo apt install appimagelauncher

# After installation, double-click AppImage
# AppImageLauncher will prompt to integrate
```

**Method 2: Manual Integration**
```bash
# Extract desktop file and icon
./Talky-0.5.0-x86_64.AppImage --appimage-extract

# Copy to user directories
cp squashfs-root/talky.desktop ~/.local/share/applications/
cp squashfs-root/talky.png ~/.local/share/icons/hicolor/256x256/apps/

# Update desktop entry to point to AppImage
sed -i "s|Exec=talky|Exec=$HOME/.local/bin/Talky.AppImage|g" \
    ~/.local/share/applications/talky.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications
```

### First Run Setup

On first run, Talky will show setup wizard:

1. **Welcome** - Features overview
2. **Platform Detection** - X11/Wayland detection
3. **Whisper Configuration** - Model and language selection
4. **Summary** - Review settings

Configuration is stored in `~/.config/talky/config.yaml`.

## AppImage Features

### Advantages

- **Universal** - One file works on Ubuntu, Fedora, Arch, etc.
- **No installation** - No package manager required
- **Portable** - Can run from USB drive
- **Rollback** - Keep multiple versions, switch easily
- **No conflicts** - Dependencies bundled, no system pollution

### Limitations

- **Large file size** - ~300-500MB (includes Python + all dependencies)
- **No automatic updates** - Must manually download new versions
- **System integration** - Requires manual setup for desktop entries
- **Resource usage** - Slightly higher memory usage vs native packages

## Configuration

### Data Directories

AppImage respects standard XDG directories:

```
~/.config/talky/              # Configuration
  ├── config.yaml             # Settings
  └── .setup_complete         # Setup wizard marker

~/.cache/talky/               # Cache
  └── models/                 # Whisper models

~/.local/share/talky/         # Application data
```

### Environment Variables

Override defaults:

```bash
# Custom config location
XDG_CONFIG_HOME=/path/to/config ./Talky.AppImage

# Custom cache location
XDG_CACHE_HOME=/path/to/cache ./Talky.AppImage

# Enable debug output
TALKY_DEBUG=1 ./Talky.AppImage
```

## Troubleshooting

### Build Issues

**Error: "appimagetool not found"**
- Install appimagetool (see Prerequisites)

**Error: "python3: command not found"**
- Install Python 3.10+: `sudo apt install python3`

**Error: "No module named 'talky'"**
- Run from project root directory
- Ensure `src/talky/` exists

**Build succeeds but AppImage is huge (>1GB)**
- This is normal if CUDA is included
- CPU-only builds are ~300MB
- GPU builds can be 800MB-1.5GB

### Runtime Issues

**Error: "GLIBC_X.XX not found"**
- Your system glibc is too old
- AppImage requires glibc 2.31+ (2020+)
- Update your distribution or use native package (.deb/.rpm)

**Error: "No protocol specified" / "Cannot open display"**
- X11 authentication issue
- Run: `xhost +local:`
- Or use native package for proper desktop integration

**Error: "ModuleNotFoundError: No module named 'faster_whisper'"**
- Should not happen (bundled in AppImage)
- Try rebuilding AppImage

**AppImage won't run (permission denied)**
```bash
chmod +x Talky-0.5.0-x86_64.AppImage
```

**System tray icon doesn't appear**
- Install system tray extension for your desktop:
  - GNOME: TopIconPlus or AppIndicator extension
  - KDE: Built-in support
  - Others: Usually work out of the box

### Performance Issues

**Slow transcription**
- AppImage includes CPU-only PyTorch by default
- For GPU acceleration, use native package (.deb/.rpm) instead
- Or rebuild AppImage with CUDA support (large file size)

**High memory usage**
- Normal - AppImage bundles Python + dependencies
- Whisper models are large (140MB-1.5GB)
- Consider smaller model: tiny (39MB) vs large (1.5GB)

## Advanced Usage

### Extracting AppImage

```bash
# Extract to squashfs-root/
./Talky-0.5.0-x86_64.AppImage --appimage-extract

# Run extracted version
./squashfs-root/AppRun

# Inspect contents
ls -lh squashfs-root/usr/
```

### Custom Build Options

Edit `build-appimage.sh` to customize:

```bash
# CPU-only (smaller size)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# GPU with CUDA (larger size)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Minimal build (exclude optional deps)
pip install . --no-deps
pip install faster-whisper numpy pillow pyyaml
```

### Continuous Integration

Build AppImages in CI:

```yaml
# GitHub Actions example
- name: Install appimagetool
  run: |
    wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
    sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool

- name: Build AppImage
  run: |
    cd appimage/
    ./build-appimage.sh

- name: Upload AppImage
  uses: actions/upload-artifact@v3
  with:
    name: Talky-AppImage
    path: appimage/Talky-*.AppImage
```

## Distribution

### GitHub Releases

```bash
# Create release with AppImage
gh release create v0.5.0 \
  appimage/Talky-0.5.0-x86_64.AppImage \
  --title "Talky 0.5.0" \
  --notes "See CHANGELOG.md"
```

### AppImageHub

Submit to AppImageHub for discoverability:
1. Fork https://github.com/AppImage/appimage.github.io
2. Add Talky to `apps/` directory
3. Submit pull request

### appimagehub.com

List on appimagehub.com:
1. Create account at https://www.appimagehub.com
2. Upload AppImage and metadata
3. Users can discover and download

## Updating

### For Users

```bash
# Download new version
wget https://github.com/ChrisKalahiki/talky/releases/download/v0.6.0/Talky-0.6.0-x86_64.AppImage

# Replace old version
mv Talky-0.6.0-x86_64.AppImage ~/.local/bin/Talky.AppImage
chmod +x ~/.local/bin/Talky.AppImage
```

### With AppImageUpdate

```bash
# Install AppImageUpdate
wget https://github.com/AppImage/AppImageUpdate/releases/download/continuous/appimageupdatetool-x86_64.AppImage
chmod +x appimageupdatetool-x86_64.AppImage

# Update Talky
./appimageupdatetool-x86_64.AppImage Talky-0.5.0-x86_64.AppImage
```

## Comparison with Other Formats

| Feature | AppImage | .deb | .rpm | AUR |
|---------|----------|------|------|-----|
| Universal | ✅ All distros | ❌ Debian/Ubuntu | ❌ Fedora/RHEL | ❌ Arch only |
| Installation | None | `apt install` | `dnf install` | `makepkg -si` |
| Root required | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Auto updates | ❌ Manual | ✅ Yes | ✅ Yes | ✅ Yes |
| File size | 300-500MB | 10-50KB | 10-50KB | 10-50KB |
| Desktop integration | Manual | Automatic | Automatic | Automatic |

**Recommendation**: Use native packages (.deb/.rpm/AUR) when possible for better integration and updates. Use AppImage for portability or testing.

## Additional Resources

- [AppImage Documentation](https://docs.appimage.org/)
- [AppImageKit GitHub](https://github.com/AppImage/AppImageKit)
- [AppImage Best Practices](https://docs.appimage.org/packaging-guide/index.html)
- [AppImageHub](https://www.appimagehub.com/)
- [Awesome AppImage](https://github.com/AppImage/awesome-appimage)

## Contributing

When modifying the AppImage build:

1. Test on multiple distributions (Ubuntu, Fedora, Arch)
2. Keep file size reasonable (exclude unnecessary dependencies)
3. Ensure AppRun script works on all platforms
4. Update documentation with any changes
5. Test desktop integration

## Support

For AppImage-specific issues:
- Check [AppImage documentation](https://docs.appimage.org/)
- Open [GitHub Issue](https://github.com/ChrisKalahiki/talky/issues) with:
  - Distribution name and version
  - AppImage version
  - Error messages or logs
  - Output of `./Talky.AppImage --version`
