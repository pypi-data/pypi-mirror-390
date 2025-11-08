# Debian Package Build Files

This directory contains files needed to build a Debian (.deb) package for Talky.

## Building the Package

### Prerequisites

Install build dependencies:

```bash
# Ubuntu/Debian
sudo apt install debhelper dh-python python3-all python3-setuptools \
                 python3-pip devscripts build-essential

# Also need runtime dependencies for testing
sudo apt install xdotool python3-pil python3-yaml python3-numpy
```

### Method 1: Quick Build (Recommended)

```bash
# From project root
./debian/build.sh
```

This creates: `../talky_0.5.0-1_all.deb`

### Method 2: Manual Build

```bash
# From project root
dpkg-buildpackage -us -uc -b

# Output:
#   ../talky_0.5.0-1_all.deb        (the package)
#   ../talky_0.5.0-1_amd64.changes  (changes file)
#   ../talky_0.5.0-1_amd64.buildinfo (build info)
```

### Method 3: Using debuild

```bash
# Clean build
debuild -us -uc -b

# With lintian checks
debuild -us -uc
```

## Installing the Package

```bash
# Install the built package
sudo apt install ../talky_0.5.0-1_all.deb

# Or using dpkg
sudo dpkg -i ../talky_0.5.0-1_all.deb

# Fix dependencies if needed
sudo apt --fix-broken install
```

## Testing the Package

```bash
# Check package contents
dpkg -c ../talky_0.5.0-1_all.deb

# Check package info
dpkg -I ../talky_0.5.0-1_all.deb

# Install in test VM/container
docker run -it ubuntu:22.04
apt update && apt install ../talky_0.5.0-1_all.deb
```

## Package Quality Checks

```bash
# Run lintian (Debian package checker)
lintian ../talky_0.5.0-1_all.deb

# Ignore certain warnings (if acceptable)
lintian -i ../talky_0.5.0-1_all.deb
```

## Uninstalling

```bash
# Remove package
sudo apt remove talky

# Remove package and configuration
sudo apt purge talky
```

## Package Structure

After installation, files are placed in:

```
/usr/bin/talky                          # Main executable
/usr/lib/python3/dist-packages/talky/  # Python package
/usr/share/applications/talky.desktop  # Desktop entry
/usr/share/icons/hicolor/*/apps/       # Icons
/usr/lib/systemd/user/talky.service    # Systemd service
/usr/share/doc/talky/                  # Documentation
```

## Troubleshooting

### Build fails with missing dependencies

```bash
# Install all build deps automatically
sudo apt build-dep ./
```

### Lintian warnings

Common warnings and fixes:

1. **no-changelog**: Fixed - debian/changelog exists
2. **no-copyright**: Fixed - debian/copyright exists
3. **binary-without-manpage**: Acceptable for GUI apps
4. **python-script-but-no-python-dep**: Fixed in control file

### Package won't install

```bash
# Check dependencies
apt-cache policy talky

# Install missing deps
sudo apt install -f
```

## File Descriptions

- **control**: Package metadata and dependencies
- **rules**: Build instructions (Makefile format)
- **copyright**: License information
- **changelog**: Version history (Debian format)
- **compat**: Debhelper compatibility level
- **postinst**: Post-installation script
- **postrm**: Post-removal script

## Creating a New Release

1. Update version in:
   - `src/talky/version.py`
   - `pyproject.toml`
   - `debian/changelog` (use `dch` command)

2. Update changelog:
   ```bash
   dch -v 0.6.0-1 "New release"
   # Edit the changelog entry
   ```

3. Build package:
   ```bash
   ./debian/build.sh
   ```

4. Test installation:
   ```bash
   sudo apt install ../talky_0.6.0-1_all.deb
   ```

5. Tag release:
   ```bash
   git tag -a v0.6.0 -m "Release v0.6.0"
   ```

## Uploading to PPA (Ubuntu)

To distribute via Ubuntu PPA:

1. Create Launchpad account
2. Set up GPG key
3. Create source package:
   ```bash
   debuild -S
   ```
4. Upload to PPA:
   ```bash
   dput ppa:your-name/talky ../talky_0.5.0-1_source.changes
   ```

## Advanced: Multi-Architecture

Currently builds as `Architecture: all` (architecture-independent).

If adding compiled components:
1. Change `Architecture: all` to `Architecture: any` in debian/control
2. Update build dependencies
3. Rebuild for each arch

## References

- [Debian New Maintainers' Guide](https://www.debian.org/doc/manuals/maint-guide/)
- [Debian Policy Manual](https://www.debian.org/doc/debian-policy/)
- [Ubuntu Packaging Guide](https://packaging.ubuntu.com/html/)
- [dh-python documentation](https://wiki.debian.org/Python/Pybuild)
