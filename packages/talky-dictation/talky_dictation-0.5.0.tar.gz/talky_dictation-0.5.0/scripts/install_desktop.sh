#!/bin/bash
# Install Talky desktop integration files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================"
echo "Talky Desktop Integration Setup"
echo "================================"
echo

# Check if running as root for system-wide install
INSTALL_TYPE="user"
if [ "$EUID" -eq 0 ]; then
    INSTALL_TYPE="system"
    echo -e "${YELLOW}Running as root - installing system-wide${NC}"
else
    echo -e "${GREEN}Running as user - installing to user directories${NC}"
fi
echo

# Set installation paths
if [ "$INSTALL_TYPE" = "system" ]; then
    DESKTOP_DIR="/usr/share/applications"
    ICON_BASE="/usr/share/icons/hicolor"
else
    DESKTOP_DIR="$HOME/.local/share/applications"
    ICON_BASE="$HOME/.local/share/icons/hicolor"
fi

# Create directories if they don't exist
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_BASE"

# Generate icons if they don't exist
if [ ! -d "$PROJECT_ROOT/icons" ] || [ -z "$(ls -A "$PROJECT_ROOT/icons" 2>/dev/null)" ]; then
    echo "Icons not found. Generating icons..."
    python3 "$SCRIPT_DIR/generate_icons.py"
    echo
fi

# Install desktop file
echo "Installing desktop file..."
if [ -f "$PROJECT_ROOT/desktop/talky.desktop" ]; then
    cp "$PROJECT_ROOT/desktop/talky.desktop" "$DESKTOP_DIR/"
    chmod 644 "$DESKTOP_DIR/talky.desktop"
    echo -e "${GREEN}✓${NC} Desktop file installed to: $DESKTOP_DIR/talky.desktop"
else
    echo -e "${RED}✗${NC} Desktop file not found: $PROJECT_ROOT/desktop/talky.desktop"
    exit 1
fi

# Install icons
echo
echo "Installing icons..."

# Icon size mappings
declare -A SIZES
SIZES=(
    ["16"]="16x16"
    ["22"]="22x22"
    ["24"]="24x24"
    ["32"]="32x32"
    ["48"]="48x48"
    ["64"]="64x64"
    ["128"]="128x128"
    ["256"]="256x256"
)

for size in "${!SIZES[@]}"; do
    SIZE_DIR="${SIZES[$size]}"
    ICON_DIR="$ICON_BASE/$SIZE_DIR/apps"

    mkdir -p "$ICON_DIR"

    ICON_FILE="$PROJECT_ROOT/icons/talky-${size}x${size}.png"

    if [ -f "$ICON_FILE" ]; then
        cp "$ICON_FILE" "$ICON_DIR/talky.png"
        chmod 644 "$ICON_DIR/talky.png"
        echo -e "${GREEN}✓${NC} Installed ${SIZE_DIR} icon"
    else
        echo -e "${YELLOW}⚠${NC} Icon not found: $ICON_FILE"
    fi
done

# Install scalable icon (if available)
if [ -f "$PROJECT_ROOT/icons/talky-scalable.png" ]; then
    SCALABLE_DIR="$ICON_BASE/scalable/apps"
    mkdir -p "$SCALABLE_DIR"
    cp "$PROJECT_ROOT/icons/talky-scalable.png" "$SCALABLE_DIR/talky.png"
    chmod 644 "$SCALABLE_DIR/talky.png"
    echo -e "${GREEN}✓${NC} Installed scalable icon"
fi

# Update icon cache
echo
echo "Updating icon cache..."
if [ "$INSTALL_TYPE" = "system" ]; then
    if command -v gtk-update-icon-cache &> /dev/null; then
        gtk-update-icon-cache -f -t "$ICON_BASE" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Icon cache updated"
    else
        echo -e "${YELLOW}⚠${NC} gtk-update-icon-cache not found (install gtk3 for better integration)"
    fi
else
    if command -v gtk-update-icon-cache &> /dev/null; then
        gtk-update-icon-cache -f -t "$ICON_BASE" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Icon cache updated"
    fi
fi

# Update desktop database
echo
echo "Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Desktop database updated"
else
    echo -e "${YELLOW}⚠${NC} update-desktop-database not found"
fi

echo
echo "================================"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo "================================"
echo
echo "Talky should now appear in your application menu."
echo
if [ "$INSTALL_TYPE" = "user" ]; then
    echo "Installed to: $HOME/.local/share/"
    echo "To uninstall: rm -rf $DESKTOP_DIR/talky.desktop $ICON_BASE/*/apps/talky.png"
else
    echo "Installed to: /usr/share/"
    echo "To uninstall: sudo rm -rf /usr/share/applications/talky.desktop /usr/share/icons/hicolor/*/apps/talky.png"
fi
echo
