# RPM Packaging for Talky

This directory contains the RPM package specification for building Talky packages for **Fedora**, **RHEL**, **CentOS**, **openSUSE**, and other RPM-based Linux distributions.

## Quick Start

```bash
# Install build dependencies
sudo dnf install rpm-build rpmdevtools python3-devel

# Build the package
cd rpm/
./build.sh

# Install
sudo dnf install ~/rpmbuild/RPMS/noarch/talky-0.5.0-1.*.noarch.rpm
```

## Prerequisites

### Build Dependencies

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install rpm-build rpmdevtools python3-devel python3-setuptools python3-pip
```

**openSUSE:**
```bash
sudo zypper install rpm-build python3-devel python3-setuptools python3-pip
```

### Runtime Dependencies

The spec file declares the following runtime dependencies (automatically installed):
- `python3 >= 3.10`
- `python3-numpy`
- `python3-pillow`
- `python3-pyyaml`
- `python3-sounddevice`
- `python3-tkinter`
- `python3-pystray`
- `python3-pynput`
- `xdotool`

**Optional dependencies** (installed separately by user):
- `python3-torch` - For GPU acceleration (CUDA)
- `ydotool` - For Wayland text injection

## Building the Package

### Automated Build

Use the provided build script:

```bash
cd rpm/
./build.sh
```

This script will:
1. Check for required build tools
2. Create rpmbuild directory structure
3. Generate source tarball
4. Build both binary and source RPMs
5. Display installation instructions

### Manual Build

If you prefer manual control:

```bash
# Setup directories
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create source tarball
VERSION="0.5.0"
cd /path/to/talky/parent/
tar czf ~/rpmbuild/SOURCES/talky-${VERSION}.tar.gz \
    --exclude='.git' --exclude='__pycache__' --exclude='venv' talky/

# Copy spec file
cp talky/rpm/talky.spec ~/rpmbuild/SPECS/

# Build package
cd ~/rpmbuild/SPECS
rpmbuild -ba talky.spec
```

## Output Packages

After successful build:

**Binary RPM:**
```
~/rpmbuild/RPMS/noarch/talky-0.5.0-1.*.noarch.rpm
```

**Source RPM:**
```
~/rpmbuild/SRPMS/talky-0.5.0-1.*.src.rpm
```

## Installation

### Install with DNF (Fedora/RHEL)

```bash
# Install binary package
sudo dnf install ~/rpmbuild/RPMS/noarch/talky-0.5.0-1.*.noarch.rpm

# Or install with automatic dependency resolution
sudo dnf install ~/rpmbuild/RPMS/noarch/talky-*.noarch.rpm
```

### Install with Zypper (openSUSE)

```bash
sudo zypper install ~/rpmbuild/RPMS/noarch/talky-0.5.0-1.*.noarch.rpm
```

### Install with RPM (Manual)

```bash
# Install dependencies first
sudo dnf install python3-numpy python3-pillow python3-pyyaml \
    python3-sounddevice python3-tkinter python3-pystray python3-pynput xdotool

# Install Talky
sudo rpm -ivh ~/rpmbuild/RPMS/noarch/talky-0.5.0-1.*.noarch.rpm
```

## Post-Installation

### Verify Installation

```bash
# Check package contents
rpm -ql talky

# Verify package information
rpm -qi talky

# Run Talky
talky
```

### Optional GPU Setup

For CUDA acceleration:

```bash
# Install PyTorch with CUDA (Fedora/RHEL)
pip3 install torch --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA availability
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Enable Systemd Service

```bash
# Enable and start as user service
systemctl --user enable --now talky

# Check status
systemctl --user status talky

# View logs
journalctl --user -u talky -f
```

### Wayland Setup

If using Wayland:

```bash
# Check setup requirements
talky --wayland-setup

# View full setup guide
talky --wayland-setup-guide
```

## Testing the Package

### Inspect Package Contents

```bash
# List all files in package
rpm -qlp ~/rpmbuild/RPMS/noarch/talky-*.noarch.rpm

# Show package metadata
rpm -qip ~/rpmbuild/RPMS/noarch/talky-*.noarch.rpm

# Check package dependencies
rpm -qRp ~/rpmbuild/RPMS/noarch/talky-*.noarch.rpm
```

### Quality Checks

```bash
# Run rpmlint on spec file
rpmlint ~/rpmbuild/SPECS/talky.spec

# Run rpmlint on binary package
rpmlint ~/rpmbuild/RPMS/noarch/talky-*.noarch.rpm

# Run rpmlint on source package
rpmlint ~/rpmbuild/SRPMS/talky-*.src.rpm
```

### Test in Clean Environment

Using a container:

```bash
# Fedora
podman run -it --rm -v ~/rpmbuild/RPMS:/rpms fedora:latest
dnf install /rpms/noarch/talky-*.noarch.rpm
talky --version

# RHEL 9
podman run -it --rm -v ~/rpmbuild/RPMS:/rpms registry.access.redhat.com/ubi9/ubi:latest
dnf install /rpms/noarch/talky-*.noarch.rpm
talky --version
```

## Uninstallation

```bash
# Uninstall with DNF (recommended)
sudo dnf remove talky

# Or with RPM
sudo rpm -e talky

# Clean up pip-installed packages
pip3 uninstall faster-whisper
```

## Package Structure

The RPM package installs:

```
/usr/bin/talky                              # Main executable
/usr/lib/python3.X/site-packages/talky/    # Python package
/usr/share/applications/talky.desktop       # Desktop entry
/usr/lib/systemd/user/talky.service         # Systemd service
/usr/share/icons/hicolor/*/apps/talky.png   # Application icons
/usr/share/doc/talky/                       # Documentation
/usr/share/licenses/talky/                  # License file
```

## Troubleshooting

### Build Errors

**Error: "python3-devel not found"**
```bash
sudo dnf install python3-devel
```

**Error: "rpmbuild command not found"**
```bash
sudo dnf install rpm-build rpmdevtools
```

**Error: "Bad exit status from /var/tmp/rpm-tmp.XXX"**
- Check if all source files exist in the tarball
- Verify Python package structure is correct
- Review build log for specific errors

### Installation Errors

**Error: "nothing provides python3-pystray"**
- This package may not be in official repos
- Install via pip: `pip3 install pystray`
- Or modify spec to include as pip dependency

**Error: "nothing provides python3-pynput"**
- Install via pip: `pip3 install pynput`
- Or modify spec to include as pip dependency

### Runtime Errors

**Error: "ModuleNotFoundError: No module named 'faster_whisper'"**
```bash
pip3 install faster-whisper
```

**Error: "No CUDA available, falling back to CPU"**
- This is a warning, not an error
- Install PyTorch with CUDA for GPU acceleration

## Distribution-Specific Notes

### Fedora

Fedora has the most up-to-date Python packages. All dependencies should install cleanly.

```bash
sudo dnf install talky-*.noarch.rpm
```

### RHEL/CentOS

RHEL 9+ includes Python 3.9+. You may need EPEL for some dependencies:

```bash
# Enable EPEL
sudo dnf install epel-release

# Install Talky
sudo dnf install talky-*.noarch.rpm
```

### openSUSE

openSUSE uses different package names:

```bash
# Install dependencies
sudo zypper install python3-numpy python3-Pillow python3-PyYAML \
    python3-tk xdotool

# Install Talky
sudo zypper install talky-*.noarch.rpm
```

## Creating a New Release

When releasing a new version:

1. **Update version.py**:
   ```python
   VERSION = "0.6.0"
   ```

2. **Update spec file** (`rpm/talky.spec`):
   ```spec
   Version:        0.6.0
   ```

3. **Add changelog entry** in spec file:
   ```spec
   %changelog
   * Fri Nov 15 2025 Talky Contributors - 0.6.0-1
   - New feature description
   - Bug fixes
   ```

4. **Build and test**:
   ```bash
   cd rpm/
   ./build.sh
   ```

5. **Create GitHub release** with binary and source RPMs attached

## Contributing

When modifying the RPM package:

1. Test on multiple distributions (Fedora, RHEL, openSUSE)
2. Run `rpmlint` to catch common issues
3. Verify installation in clean containers
4. Document any changes in this README

## Additional Resources

- [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/)
- [RPM Packaging Guide](https://rpm-packaging-guide.github.io/)
- [rpmlint Documentation](https://github.com/rpm-software-management/rpmlint)
- [Mock for Package Testing](https://github.com/rpm-software-management/mock)

## Support

For RPM packaging issues:
- Check existing [GitHub Issues](https://github.com/ChrisKalahiki/talky/issues)
- Open a new issue with:
  - Distribution name and version
  - RPM build log
  - rpmlint output
  - Error messages
