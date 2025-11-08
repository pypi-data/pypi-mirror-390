Name:           talky
Version:        0.5.0
Release:        1%{?dist}
Summary:        System-wide dictation for Linux using Whisper AI

License:        MIT
URL:            https://github.com/ChrisKalahiki/talky
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip

# Core runtime dependencies
Requires:       python3 >= 3.10
Requires:       python3-numpy
Requires:       python3-pillow
Requires:       python3-pyyaml
Requires:       python3-sounddevice

# X11/Wayland tools
Requires:       xdotool
Suggests:       ydotool

# GUI dependencies
Requires:       python3-tkinter
Requires:       python3-pystray

# Hotkey support
Requires:       python3-pynput

# Optional GPU acceleration (user must install separately)
# Requires:       python3-torch

%description
Talky is a system-wide dictation application for Linux that uses OpenAI's
Whisper AI for accurate speech-to-text transcription. It provides push-to-talk
functionality similar to WisprFlow AI on Windows/Mac.

Features:
* Push-to-talk dictation (default: Ctrl+Super)
* 99 language support with auto-detection
* System tray with full GUI settings
* First-run setup wizard
* X11 primary support with Wayland compatibility
* Optional GPU acceleration with CUDA
* Systemd user service integration
* Desktop environment integration

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install

# Install desktop file
install -D -m 0644 desktop/talky.desktop \
    %{buildroot}%{_datadir}/applications/talky.desktop

# Install systemd user service
install -D -m 0644 systemd/talky.service \
    %{buildroot}%{_userunitdir}/talky.service

# Install icons (if generated)
if [ -d icons/hicolor ]; then
    for size in 16 22 24 32 48 64 128 256; do
        if [ -f icons/hicolor/${size}x${size}/apps/talky.png ]; then
            install -D -m 0644 icons/hicolor/${size}x${size}/apps/talky.png \
                %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/talky.png
        fi
    done
fi

%post
# Install faster-whisper via pip (not available in Fedora repos)
echo "Installing faster-whisper via pip..."
pip3 install --no-warn-script-location faster-whisper || true

# Update icon cache
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null || :
fi

# Update desktop database
if [ -x %{_bindir}/update-desktop-database ]; then
    update-desktop-database %{_datadir}/applications &>/dev/null || :
fi

echo ""
echo "Talky installed successfully!"
echo ""
echo "To get started:"
echo "  1. Run: talky"
echo "  2. Or launch from application menu: Sound & Video > Talky"
echo "  3. For Wayland users: talky --wayland-setup"
echo ""
echo "Enable autostart: talky --enable-autostart"
echo "Enable systemd service: systemctl --user enable --now talky"

%postun
# Update icon cache
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null || :
fi

# Update desktop database
if [ -x %{_bindir}/update-desktop-database ]; then
    update-desktop-database %{_datadir}/applications &>/dev/null || :
fi

# On complete removal, optionally clean up pip packages
if [ $1 -eq 0 ]; then
    echo "To remove pip-installed packages: pip3 uninstall faster-whisper"
fi

%files
%license LICENSE
%doc README.md CHANGELOG.md COMPATIBILITY_MATRIX.md
%{python3_sitelib}/talky/
%{python3_sitelib}/talky-%{version}-py%{python3_version}.egg-info/
%{_bindir}/talky
%{_datadir}/applications/talky.desktop
%{_userunitdir}/talky.service
%{_datadir}/icons/hicolor/*/apps/talky.png

%changelog
* Thu Nov 06 2025 Talky Contributors <talky@example.com> - 0.5.0-1
- Phase 5 release: Testing & Packaging
- Added test suites (quality, performance, memory)
- Added desktop integration (.desktop file, icons)
- Added systemd user service
- Added Debian and RPM packaging
- Updated documentation (README, CHANGELOG, COMPATIBILITY_MATRIX)

* Wed Nov 06 2025 Talky Contributors <talky@example.com> - 0.4.0-1
- Phase 4 release: UI & Integration
- Added system tray with language selection
- Added settings dialog (4 tabs: General, Whisper, Hotkeys, Platform)
- Added first-run setup wizard
- Added Wayland permission checker
- Added 99 language support with auto-detection
- Updated all documentation

* Tue Nov 05 2025 Talky Contributors <talky@example.com> - 0.3.0-1
- Phase 3 release: Main Application
- Implemented main application loop with push-to-talk
- Added configuration system (YAML-based)
- Added CLI argument parsing
- Basic tray integration

* Mon Nov 04 2025 Talky Contributors <talky@example.com> - 0.2.0-1
- Phase 2 release: Platform Backends
- Implemented X11 text injection (xdotool, pynput)
- Implemented X11 hotkey management
- Added Wayland stubs with clipboard fallback
- Platform detection system

* Sun Nov 03 2025 Talky Contributors <talky@example.com> - 0.1.0-1
- Initial release: Core Foundation
- Platform detection (X11/Wayland)
- Audio capture with sounddevice
- Whisper transcription with faster-whisper
- CUDA/CPU auto-detection
- Abstract interfaces and factory functions
