#!/bin/bash
# Install Talky systemd user service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/talky.service"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================"
echo "Talky Systemd Service Installer"
echo "================================"
echo

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}✗ Service file not found: $SERVICE_FILE${NC}"
    exit 1
fi

# Check if talky is installed
if ! command -v talky &> /dev/null; then
    echo -e "${YELLOW}⚠ Warning: 'talky' command not found in PATH${NC}"
    echo "  Make sure Talky is installed before enabling the service."
    echo
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create systemd user directory if it doesn't exist
mkdir -p "$USER_SYSTEMD_DIR"

# Copy service file
echo "Installing service file..."
cp "$SERVICE_FILE" "$USER_SYSTEMD_DIR/talky.service"
echo -e "${GREEN}✓${NC} Service file copied to: $USER_SYSTEMD_DIR/talky.service"

# Reload systemd daemon
echo
echo "Reloading systemd daemon..."
systemctl --user daemon-reload
echo -e "${GREEN}✓${NC} Systemd daemon reloaded"

# Ask if user wants to enable autostart
echo
read -p "Enable Talky to start automatically on login? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$  ]] || [[ -z $REPLY ]]; then
    systemctl --user enable talky.service
    echo -e "${GREEN}✓${NC} Service enabled for autostart"
fi

# Ask if user wants to start now
echo
read -p "Start Talky service now? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$  ]] || [[ -z $REPLY ]]; then
    systemctl --user start talky.service
    echo -e "${GREEN}✓${NC} Service started"

    # Wait a moment for service to start
    sleep 2

    # Check status
    if systemctl --user is-active --quiet talky.service; then
        echo -e "${GREEN}✓${NC} Service is running"
    else
        echo -e "${RED}✗${NC} Service failed to start"
        echo
        echo "Check status with: systemctl --user status talky"
        echo "View logs with: journalctl --user -u talky"
        exit 1
    fi
fi

echo
echo "================================"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo "================================"
echo
echo "Useful commands:"
echo "  systemctl --user status talky    # Check service status"
echo "  systemctl --user stop talky      # Stop service"
echo "  systemctl --user restart talky   # Restart service"
echo "  journalctl --user -u talky -f    # View live logs"
echo "  systemctl --user disable talky   # Disable autostart"
echo
echo "To uninstall:"
echo "  systemctl --user stop talky"
echo "  systemctl --user disable talky"
echo "  rm ~/.config/systemd/user/talky.service"
echo "  systemctl --user daemon-reload"
echo
