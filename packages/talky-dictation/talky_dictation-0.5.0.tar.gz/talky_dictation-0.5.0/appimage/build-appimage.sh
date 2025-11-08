#!/bin/bash
# AppImage build script for Talky
# Builds a self-contained AppImage that runs on most Linux distributions
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION=$(grep "^VERSION = " "$PROJECT_ROOT/src/talky/version.py" | cut -d'"' -f2)
APPDIR="$SCRIPT_DIR/Talky.AppDir"

echo "========================================"
echo "Talky AppImage Builder"
echo "========================================"
echo "Version: $VERSION"
echo "AppDir: $APPDIR"
echo ""

# Check for appimagetool
if ! command -v appimagetool &> /dev/null; then
    echo "Error: appimagetool not found!"
    echo ""
    echo "Download from: https://github.com/AppImage/AppImageKit/releases"
    echo ""
    echo "Quick install:"
    echo "  wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "  chmod +x appimagetool-x86_64.AppImage"
    echo "  sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
    exit 1
fi

# Clean previous build
if [ -d "$APPDIR" ]; then
    echo "Cleaning previous build..."
    rm -rf "$APPDIR"
fi

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Install Python and Talky
echo "Installing Talky with dependencies..."
cd "$PROJECT_ROOT"

# Create virtual environment in AppDir
python3 -m venv "$APPDIR/usr"
source "$APPDIR/usr/bin/activate"

# Install Talky and dependencies
pip install --upgrade pip
pip install .
pip install faster-whisper torch sounddevice pystray pynput numpy pillow pyyaml

# Copy external tools
echo "Copying external tools..."
# xdotool (if available)
if command -v xdotool &> /dev/null; then
    cp "$(which xdotool)" "$APPDIR/usr/bin/"
    # Copy xdotool dependencies
    for lib in $(ldd "$(which xdotool)" | grep "=> /" | awk '{print $3}'); do
        cp -n "$lib" "$APPDIR/usr/lib/" 2>/dev/null || true
    done
fi

# Create AppRun script
echo "Creating AppRun launcher..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
# AppRun script for Talky AppImage

# Get AppImage directory
APPDIR="$(dirname "$(readlink -f "$0")")"

# Set up environment
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$APPDIR/usr/lib/python3.10/site-packages:$PYTHONPATH"
export PYTHONHOME="$APPDIR/usr"

# Run Talky
exec "$APPDIR/usr/bin/python3" -m talky.main "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Copy desktop file
echo "Installing desktop file..."
cp "$PROJECT_ROOT/desktop/talky.desktop" "$APPDIR/usr/share/applications/"
cp "$APPDIR/usr/share/applications/talky.desktop" "$APPDIR/"

# Generate and copy icon
echo "Generating icon..."
cd "$PROJECT_ROOT"
python3 scripts/generate_icons.py 2>/dev/null || true

if [ -f "$PROJECT_ROOT/icons/hicolor/256x256/apps/talky.png" ]; then
    cp "$PROJECT_ROOT/icons/hicolor/256x256/apps/talky.png" \
        "$APPDIR/usr/share/icons/hicolor/256x256/apps/"
    cp "$PROJECT_ROOT/icons/hicolor/256x256/apps/talky.png" "$APPDIR/"
else
    echo "Warning: Icon not found, AppImage will use default icon"
fi

# Copy documentation
echo "Installing documentation..."
mkdir -p "$APPDIR/usr/share/doc/talky"
cp "$PROJECT_ROOT/README.md" "$APPDIR/usr/share/doc/talky/"
cp "$PROJECT_ROOT/LICENSE" "$APPDIR/usr/share/doc/talky/"
cp "$PROJECT_ROOT/CHANGELOG.md" "$APPDIR/usr/share/doc/talky/" 2>/dev/null || true

# Build AppImage
echo ""
echo "Building AppImage..."
echo "========================================"
cd "$SCRIPT_DIR"
ARCH=x86_64 appimagetool "$APPDIR" "Talky-${VERSION}-x86_64.AppImage"

# Check if build succeeded
if [ -f "Talky-${VERSION}-x86_64.AppImage" ]; then
    echo ""
    echo "========================================"
    echo "Build successful!"
    echo "========================================"
    echo ""
    echo "AppImage: $SCRIPT_DIR/Talky-${VERSION}-x86_64.AppImage"
    echo "Size: $(du -h "Talky-${VERSION}-x86_64.AppImage" | cut -f1)"
    echo ""
    echo "To test:"
    echo "  ./Talky-${VERSION}-x86_64.AppImage"
    echo ""
    echo "To install:"
    echo "  mkdir -p ~/.local/bin"
    echo "  cp Talky-${VERSION}-x86_64.AppImage ~/.local/bin/Talky.AppImage"
    echo "  chmod +x ~/.local/bin/Talky.AppImage"
    echo ""
    echo "Desktop integration:"
    echo "  ./Talky-${VERSION}-x86_64.AppImage --appimage-extract"
    echo "  cp squashfs-root/talky.desktop ~/.local/share/applications/"
    echo "  cp squashfs-root/talky.png ~/.local/share/icons/"
else
    echo ""
    echo "========================================"
    echo "Build failed!"
    echo "========================================"
    echo "Check the output above for errors."
    exit 1
fi
