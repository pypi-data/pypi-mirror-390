# AUR Packaging for Talky

This directory contains the PKGBUILD for creating an **Arch User Repository (AUR)** package for Talky.

## Quick Start

### For Users (Installing from AUR)

```bash
# Clone AUR repository (once published)
git clone https://aur.archlinux.org/talky.git
cd talky

# Build and install
makepkg -si
```

Or use an AUR helper:

```bash
# With yay
yay -S talky

# With paru
paru -S talky

# With pikaur
pikaur -S talky
```

### For Maintainers (Publishing to AUR)

See [Publishing to AUR](#publishing-to-aur) section below.

## Prerequisites

### Build Dependencies

```bash
sudo pacman -S base-devel python python-build python-installer python-wheel python-setuptools
```

### Runtime Dependencies

Automatically installed by makepkg:
- `python` (>=3.10)
- `python-numpy`
- `python-pillow`
- `python-yaml`
- `python-sounddevice`
- `python-pystray`
- `python-pynput`
- `xdotool`

### Optional Dependencies

Install for additional features:

```bash
# GPU acceleration with CUDA
sudo pacman -S python-pytorch cuda

# Wayland text injection
sudo pacman -S ydotool

# Modern audio stack (recommended)
sudo pacman -S pipewire pipewire-pulse
```

## Building Locally

### Test Build

```bash
cd aur/

# Build package
makepkg

# Build and install
makepkg -si

# Build with clean chroot (recommended for testing)
makepkg -sc
```

### Clean Build in Chroot

For testing in a clean environment:

```bash
# Install devtools
sudo pacman -S devtools

# Create clean chroot
sudo mkarchroot /var/lib/archbuild/extra-x86_64/root base-devel

# Build in chroot
makechrootpkg -c -r /var/lib/archbuild/extra-x86_64
```

### Verify Package

```bash
# List package contents
tar -tzf talky-0.5.0-1-any.pkg.tar.zst

# Check package info
pacman -Qip talky-0.5.0-1-any.pkg.tar.zst

# Install locally
sudo pacman -U talky-0.5.0-1-any.pkg.tar.zst
```

## Package Structure

The package installs:

```
/usr/bin/talky                              # Main executable
/usr/lib/python3.X/site-packages/talky/    # Python package
/usr/share/applications/talky.desktop       # Desktop entry
/usr/lib/systemd/user/talky.service         # Systemd service
/usr/share/icons/hicolor/*/apps/talky.png   # Application icons
/usr/share/doc/talky/                       # Documentation
/usr/share/licenses/talky/                  # License
```

## Publishing to AUR

### Initial Setup

1. **Create AUR account**: https://aur.archlinux.org/register

2. **Add SSH key**:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   cat ~/.ssh/id_ed25519.pub
   # Add to https://aur.archlinux.org/account
   ```

3. **Test SSH connection**:
   ```bash
   ssh -T aur@aur.archlinux.org
   ```

### First Publish

1. **Clone AUR repository**:
   ```bash
   git clone ssh://aur@aur.archlinux.org/talky.git aur-talky
   cd aur-talky
   ```

2. **Copy files**:
   ```bash
   cp /path/to/talky/aur/PKGBUILD .
   cp /path/to/talky/aur/.SRCINFO .
   ```

3. **Update checksums**:
   ```bash
   # Download source and calculate checksum
   updpkgsums

   # Regenerate .SRCINFO
   makepkg --printsrcinfo > .SRCINFO
   ```

4. **Commit and push**:
   ```bash
   git add PKGBUILD .SRCINFO
   git commit -m "Initial import: talky 0.5.0"
   git push
   ```

### Updating Package

When releasing a new version:

1. **Update PKGBUILD**:
   ```bash
   # Change version
   pkgver=0.6.0
   pkgrel=1

   # Update checksums
   updpkgsums
   ```

2. **Update .SRCINFO**:
   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```

3. **Test build**:
   ```bash
   makepkg -sf
   ```

4. **Commit and push**:
   ```bash
   git add PKGBUILD .SRCINFO
   git commit -m "Update to 0.6.0"
   git push
   ```

### Release Checklist

Before publishing to AUR:

- [ ] Test build with `makepkg -sc`
- [ ] Verify installation with `makepkg -si`
- [ ] Check all dependencies are available in official repos or AUR
- [ ] Update checksums with `updpkgsums`
- [ ] Regenerate `.SRCINFO` with `makepkg --printsrcinfo > .SRCINFO`
- [ ] Test in clean chroot with `makechrootpkg`
- [ ] Run `namcap PKGBUILD` to check for issues
- [ ] Run `namcap *.pkg.tar.zst` on built package
- [ ] Create GitHub release with tag matching `pkgver`
- [ ] Update `source` URL to point to GitHub release

## Post-Installation

### Verify Installation

```bash
# Check if installed
pacman -Qi talky

# List installed files
pacman -Ql talky

# Run Talky
talky
```

### Enable Systemd Service

```bash
# Enable and start
systemctl --user enable --now talky

# Check status
systemctl --user status talky

# View logs
journalctl --user -u talky -f
```

### Wayland Setup

For Wayland users:

```bash
# Install ydotool
sudo pacman -S ydotool

# Check setup
talky --wayland-setup

# View full guide
talky --wayland-setup-guide
```

### GPU Setup

For CUDA acceleration:

```bash
# Install PyTorch with CUDA
sudo pacman -S python-pytorch cuda

# Verify CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Configure Talky to use CUDA (automatic by default)
talky
```

## Troubleshooting

### Build Errors

**Error: "Unknown option: --no-isolation"**
- Update python-build: `sudo pacman -S python-build`

**Error: "Failed to fetch source"**
- Check if GitHub release exists
- Verify URL in PKGBUILD `source` array
- Update checksums: `updpkgsums`

**Error: "Integrity checks failed"**
- Checksums don't match
- Run `updpkgsums` to regenerate

### Installation Errors

**Error: "python: No such file or directory"**
```bash
sudo pacman -S python
```

**Error: "ModuleNotFoundError: No module named 'faster_whisper'"**
- This is expected - faster-whisper installs on first run
- Or install manually: `pip install faster-whisper`

### Runtime Errors

**Error: "No CUDA available"**
- Install PyTorch with CUDA: `sudo pacman -S python-pytorch cuda`
- Or use CPU mode (automatic fallback)

**Error: "xdotool not found"**
```bash
sudo pacman -S xdotool
```

## Quality Checks

### namcap

namcap checks PKGBUILD for common issues:

```bash
# Check PKGBUILD
namcap PKGBUILD

# Check built package
namcap talky-0.5.0-1-any.pkg.tar.zst
```

### shellcheck

Check install scripts:

```bash
shellcheck -x PKGBUILD
```

### Manual Testing

Test in fresh Arch install:

```bash
# Using Docker
docker run -it --rm archlinux:latest
pacman -Sy base-devel git
useradd -m builder
su - builder
git clone https://aur.archlinux.org/talky.git
cd talky
makepkg -si
```

## Package Maintenance

### Responding to Issues

Users may report issues on AUR package page. Common scenarios:

1. **Dependency missing**: Add to `depends` or `optdepends`
2. **Build failure**: Test in clean chroot, update PKGBUILD
3. **Version outdated**: Update `pkgver`, checksums, and `.SRCINFO`

### Orphaning Package

If you can no longer maintain:

1. Leave comment on AUR page explaining
2. Click "Disown Package" button
3. Notify in comments to find new maintainer

### Flagging Out-of-Date

Users will flag package when new version released. To update:

1. Update `pkgver` in PKGBUILD
2. Run `updpkgsums`
3. Regenerate `.SRCINFO`
4. Test build
5. Commit and push

## AUR Guidelines

Follow [AUR Submission Guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines):

- Package name should be lowercase
- Use meaningful commit messages
- Test thoroughly before pushing
- Respond to comments promptly
- Keep `.SRCINFO` in sync with PKGBUILD
- Don't package pre-built binaries (use -bin suffix if necessary)
- Include all licenses

## Additional Resources

- [AUR Submission Guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- [PKGBUILD Manual](https://man.archlinux.org/man/PKGBUILD.5)
- [makepkg Manual](https://man.archlinux.org/man/makepkg.8)
- [namcap Manual](https://wiki.archlinux.org/title/Namcap)
- [Arch Package Guidelines](https://wiki.archlinux.org/title/Arch_package_guidelines)

## Contributing

When modifying the PKGBUILD:

1. Test in clean chroot
2. Run namcap checks
3. Verify all dependencies are correct
4. Update `.SRCINFO`
5. Document changes in commit message

## Support

For AUR packaging issues:
- Check [AUR package page comments](https://aur.archlinux.org/packages/talky)
- Open [GitHub Issue](https://github.com/ChrisKalahiki/talky/issues)
- Ask on [Arch Linux Forums](https://bbs.archlinux.org/)

---

**Note**: This package is not yet published to AUR. Maintainer should follow "Publishing to AUR" steps above after first stable release.
