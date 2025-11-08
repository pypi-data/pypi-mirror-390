# Talky Systemd Service

This directory contains systemd user service files for running Talky as a background service.

## Installation

### Method 1: Automatic (via script)

```bash
./systemd/install_service.sh
```

### Method 2: Manual Installation

```bash
# Copy service file to user systemd directory
mkdir -p ~/.config/systemd/user/
cp systemd/talky.service ~/.config/systemd/user/

# Reload systemd user daemon
systemctl --user daemon-reload

# Enable service (start on login)
systemctl --user enable talky.service

# Start service now
systemctl --user start talky.service

# Check status
systemctl --user status talky.service
```

## Usage

```bash
# Start Talky service
systemctl --user start talky

# Stop Talky service
systemctl --user stop talky

# Restart Talky service
systemctl --user restart talky

# Check service status
systemctl --user status talky

# View logs
journalctl --user -u talky

# Follow logs in real-time
journalctl --user -u talky -f

# Enable autostart (on login)
systemctl --user enable talky

# Disable autostart
systemctl --user disable talky
```

## Configuration

### Custom Talky Path

If Talky is installed in a non-standard location, edit the service file:

```bash
# Edit service file
nano ~/.config/systemd/user/talky.service

# Change ExecStart line:
ExecStart=/path/to/your/talky

# Reload daemon
systemctl --user daemon-reload

# Restart service
systemctl --user restart talky
```

### Environment Variables

The service file includes common environment variables for X11 and Wayland.

To add custom environment variables:

```bash
# Edit service file
nano ~/.config/systemd/user/talky.service

# Add under [Service] section:
Environment="YOUR_VAR=value"

# For Hugging Face token:
Environment="HF_TOKEN=your_token_here"

# Reload and restart
systemctl --user daemon-reload
systemctl --user restart talky
```

### Resource Limits

To limit CPU or memory usage, uncomment and adjust these lines in the service file:

```ini
[Service]
# Limit memory to 2GB
MemoryMax=2G

# Limit CPU to 50% of one core
CPUQuota=50%
```

## Troubleshooting

### Service fails to start

```bash
# Check status for error messages
systemctl --user status talky

# View detailed logs
journalctl --user -u talky --no-pager

# Check if Talky runs manually
talky

# Verify Talky is in PATH
which talky
```

### Service starts but doesn't work

Common issues:

1. **Display server not accessible**:
   - Check DISPLAY environment variable
   - May need to adjust DISPLAY=:0 to match your setup
   - For Wayland, verify WAYLAND_DISPLAY

2. **Permissions issues** (Wayland):
   - Service runs with your user permissions
   - Ensure ydotool permissions are set up
   - Check: `groups | grep -E 'input|uinput'`

3. **Audio device not found**:
   - Service may start before audio system is ready
   - Increase RestartSec in service file
   - Or use traditional autostart instead

### Service won't stop

```bash
# Force stop
systemctl --user kill talky

# If still running, force kill
pkill -9 -f talky
```

## Comparison: Systemd vs XDG Autostart

### Systemd Service (this method)
**Pros**:
- Runs as proper background service
- Automatic restart on crashes
- Better logging (journalctl)
- Resource limits
- Start/stop/restart commands

**Cons**:
- More complex setup
- May start before desktop is fully ready
- Requires understanding of systemd

### XDG Autostart (built-in method)
**Pros**:
- Simple: `talky --enable-autostart`
- Starts after desktop is fully loaded
- Works across all desktop environments
- No systemd knowledge needed

**Cons**:
- No automatic restart
- No built-in logging
- Less control over service

**Recommendation**: For most users, use the built-in autostart (`talky --enable-autostart`).
Only use systemd service if you need the extra control and monitoring.

## Uninstallation

```bash
# Stop and disable service
systemctl --user stop talky
systemctl --user disable talky

# Remove service file
rm ~/.config/systemd/user/talky.service

# Reload daemon
systemctl --user daemon-reload
```

## Advanced: System-wide Service (All Users)

**Warning**: This runs Talky as a system service for all users. Only do this if you understand systemd well.

```bash
# Copy to system directory (requires root)
sudo cp systemd/talky.service /etc/systemd/system/talky@.service

# Edit to add user template
sudo nano /etc/systemd/system/talky@.service

# Change [Service] section:
[Service]
Type=simple
User=%i
ExecStart=/usr/bin/talky

# Enable for specific user
sudo systemctl enable talky@username.service
sudo systemctl start talky@username.service
```

## See Also

- `talky --enable-autostart` - Simple autostart method
- `~/.config/autostart/talky.desktop` - XDG autostart file
- Desktop integration: `./scripts/install_desktop.sh`
