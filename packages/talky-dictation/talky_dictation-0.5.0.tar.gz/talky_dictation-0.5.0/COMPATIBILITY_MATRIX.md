# Talky Application Compatibility Matrix

This document tracks text injection compatibility across different applications on Linux.

## Testing Methodology

For each application, test the following:

1. **Launch application** and place cursor in text input field
2. **Hold Ctrl+Win** (or configured hotkey)
3. **Speak clearly**: "The quick brown fox jumps over the lazy dog"
4. **Release hotkey** and wait for transcription
5. **Verify**: Text appears correctly at cursor position
6. **Rate compatibility**:
   - ✅ **Works Perfect**: Text appears instantly, no issues
   - ⚠️ **Works with Issues**: Text appears but with delays/glitches
   - ❌ **Does Not Work**: Text fails to inject or appears in wrong location
   - 🔲 **Not Tested**: Needs testing

## Compatibility Status

### Web Browsers

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| Firefox | 🔲 | 🔲 | |
| Chrome | 🔲 | 🔲 | |
| Chromium | 🔲 | 🔲 | |
| Brave | 🔲 | 🔲 | |
| Edge | 🔲 | 🔲 | |

### Text Editors & IDEs

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| VS Code | 🔲 | 🔲 | Electron-based |
| VSCodium | 🔲 | 🔲 | Electron-based |
| Sublime Text | 🔲 | 🔲 | |
| Atom | 🔲 | 🔲 | Electron-based |
| gedit | 🔲 | 🔲 | GNOME default |
| Kate | 🔲 | 🔲 | KDE default |
| Geany | 🔲 | 🔲 | |
| vim (gvim) | 🔲 | 🔲 | GUI version |
| Emacs (GUI) | 🔲 | 🔲 | GUI version |
| Notepad++ (Wine) | 🔲 | 🔲 | Windows app via Wine |

### IDEs (Heavy)

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| PyCharm | 🔲 | 🔲 | JetBrains IDE |
| IntelliJ IDEA | 🔲 | 🔲 | JetBrains IDE |
| WebStorm | 🔲 | 🔲 | JetBrains IDE |
| Android Studio | 🔲 | 🔲 | JetBrains-based |
| Eclipse | 🔲 | 🔲 | |
| NetBeans | 🔲 | 🔲 | |

### Terminal Emulators

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| GNOME Terminal | 🔲 | 🔲 | |
| Konsole | 🔲 | 🔲 | KDE default |
| Alacritty | 🔲 | 🔲 | GPU-accelerated |
| Kitty | 🔲 | 🔲 | GPU-accelerated |
| Terminator | 🔲 | 🔲 | |
| Tilix | 🔲 | 🔲 | |
| xterm | 🔲 | 🔲 | Classic |
| rxvt | 🔲 | 🔲 | |
| Foot | 🔲 | 🔲 | Wayland-native |
| WezTerm | 🔲 | 🔲 | |

### Office Applications

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| LibreOffice Writer | 🔲 | 🔲 | Word processor |
| LibreOffice Calc | 🔲 | 🔲 | Spreadsheet |
| LibreOffice Impress | 🔲 | 🔲 | Presentations |
| OnlyOffice | 🔲 | 🔲 | |
| Google Docs | 🔲 | 🔲 | Web-based (in browser) |
| Microsoft Office (Wine) | 🔲 | 🔲 | Windows app via Wine |
| WPS Office | 🔲 | 🔲 | |

### Communication Apps

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| Discord | 🔲 | 🔲 | Electron-based |
| Slack | 🔲 | 🔲 | Electron-based |
| Teams | 🔲 | 🔲 | Electron-based |
| Telegram | 🔲 | 🔲 | Native Qt version |
| Signal | 🔲 | 🔲 | Electron-based |
| Element | 🔲 | 🔲 | Matrix client |
| Thunderbird | 🔲 | 🔲 | Email client |
| Evolution | 🔲 | 🔲 | GNOME email |
| Zoom | 🔲 | 🔲 | |

### Note-Taking Apps

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| Obsidian | 🔲 | 🔲 | Electron-based |
| Joplin | 🔲 | 🔲 | Electron-based |
| Standard Notes | 🔲 | 🔲 | |
| Notion (web) | 🔲 | 🔲 | Web-based |
| Simplenote | 🔲 | 🔲 | |
| Tomboy Notes | 🔲 | 🔲 | GNOME app |
| Zim Wiki | 🔲 | 🔲 | |

### Native GNOME Apps

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| GNOME Text Editor | 🔲 | 🔲 | New default editor |
| gedit | 🔲 | 🔲 | Legacy editor |
| Nautilus (rename) | 🔲 | 🔲 | File manager |
| GNOME Builder | 🔲 | 🔲 | IDE |
| GNOME Calculator | 🔲 | 🔲 | Limited input |

### Native KDE Apps

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| Kate | 🔲 | 🔲 | Text editor |
| KWrite | 🔲 | 🔲 | Simple editor |
| Dolphin (rename) | 🔲 | 🔲 | File manager |
| KDevelop | 🔲 | 🔲 | IDE |
| Kile | 🔲 | 🔲 | LaTeX editor |

### Command Line Editors (in terminal)

| Application | X11 | Wayland | Notes |
|------------|-----|---------|-------|
| vim | 🔲 | 🔲 | Terminal-based |
| neovim | 🔲 | 🔲 | Terminal-based |
| emacs (terminal) | 🔲 | 🔲 | Terminal-based |
| nano | 🔲 | 🔲 | Terminal-based |
| micro | 🔲 | 🔲 | Terminal-based |

**Note**: Terminal-based editors typically don't work with xdotool/ydotool. Use GUI versions (gvim, emacs GUI) or clipboard fallback.

### Form Fields & Special Cases

| Test Case | X11 | Wayland | Notes |
|-----------|-----|---------|-------|
| Search bars (browser) | 🔲 | 🔲 | |
| URL/address bar | 🔲 | 🔲 | |
| Password fields | 🔲 | 🔲 | Should work but sensitive |
| Multi-line textareas | 🔲 | 🔲 | |
| Rich text editors (WYSIWYG) | 🔲 | 🔲 | Like Confluence, WordPress |
| Search dialogs (Ctrl+F) | 🔲 | 🔲 | |
| File open dialogs | 🔲 | 🔲 | |
| Rename dialogs | 🔲 | 🔲 | |

## Known Issues & Workarounds

### Issue: Text doesn't appear in application X
**Workarounds**:
1. Try clipboard fallback method (set `prefer_method: clipboard` in config)
2. For Wayland: Check ydotool permissions
3. For terminal apps: Use GUI version or copy from clipboard manually

### Issue: Special characters missing
**Possible causes**:
- Language/locale mismatch
- Application filters certain characters

### Issue: Text appears in wrong location
**Common in**:
- Rich text editors (TinyMCE, CKEditor)
- Some Electron apps

**Workaround**: Click in field first, then use Talky

## How to Test

### Quick Test (5 minutes)
1. Pick 3 apps you use daily
2. Test each with the standard test phrase
3. Mark results in this document
4. Submit PR with your findings!

### Comprehensive Test (30 minutes)
1. Test your desktop environment's native apps
2. Test your primary browser
3. Test your code editor/IDE
4. Test 1-2 communication apps
5. Submit PR with all findings!

## Contributing Test Results

When submitting compatibility results:

1. **Fork** this repository
2. **Edit** `COMPATIBILITY_MATRIX.md`
3. **Update** the matrix with your findings
4. **Include** in PR description:
   - Your distribution (e.g., Ubuntu 22.04)
   - Desktop environment (GNOME/KDE/etc.)
   - Display server (X11/Wayland)
   - Text injection method used (xdotool/ydotool/clipboard)
5. **Submit PR** with title: "Compatibility: [App Name] on [Platform]"

### Example PR Description
```
Distribution: Ubuntu 22.04 LTS
Desktop: GNOME 42
Display Server: Wayland
Text Injection: ydotool

Tested Applications:
- Firefox: ✅ Works Perfect
- VS Code: ✅ Works Perfect
- GNOME Terminal: ⚠️ Works with minor lag (~0.5s delay)
- Discord: ❌ Does Not Work (Electron app, text appears in wrong field)

Additional Notes:
Firefox and VS Code work flawlessly. Terminal has slight delay but reliable.
Discord failed with ydotool but worked with clipboard fallback method.
```

## Test Automation (Future)

We're working on automated compatibility testing. See `tests/test_compatibility.py` (planned).

## Platform-Specific Notes

### X11
- **xdotool** works with most applications
- **pynput** fallback for xdotool failures
- Clipboard method as last resort

### Wayland
- **ydotool** requires proper permissions (see README)
- Some apps (especially Electron) may have issues
- Clipboard fallback more reliable on Wayland

### Electron Apps
Many apps use Electron (VS Code, Discord, Slack, etc.). Compatibility varies:
- Some work perfectly with xdotool/ydotool
- Some require clipboard fallback
- Some have focus issues (text appears in wrong field)

**Tip**: If an Electron app fails, try:
1. Click in the text field first
2. Wait 0.5s, then use Talky
3. Or use clipboard fallback method

## Getting Help

If Talky doesn't work in your application:

1. Check if it's tested in this matrix
2. Try different text injection methods (config: `prefer_method`)
3. See `README.md` troubleshooting section
4. Open an issue with details about the app and your setup

---

**Last Updated**: 2025-11-06
**Total Apps Documented**: 70+
**Apps Tested**: 0 (community testing needed!)

**Help us complete this matrix! Your contributions are valuable!** 🙏
