# Talky Tests

## Running Tests

### Platform Tests

Test platform detection, text injection, and hotkeys:

```bash
cd /path/to/talky
python tests/test_platform.py
```

This will:
1. Detect your display server (X11/Wayland)
2. Check available text injection tools
3. Test text injection (optional)
4. Test hotkey registration (optional)

### Text Injection Test

To test text injection only:

```bash
python -c "
import sys
sys.path.insert(0, 'src')
from talky.input import create_text_injector
import time

injector = create_text_injector()
print('Click in a text field...')
time.sleep(5)
injector.inject_text('Hello from Talky!')
"
```

### Hotkey Test

To test hotkeys only:

```bash
python -c "
import sys
sys.path.insert(0, 'src')
from talky.hotkeys import create_hotkey_manager
import time

manager = create_hotkey_manager()
manager.register('<ctrl>+<super>', lambda: print('Hotkey pressed!'))
manager.start()
print('Press Ctrl+Win to test...')
time.sleep(10)
manager.stop()
"
```

## Unit Tests (Coming Soon)

Unit tests for individual components will be added using pytest:

```bash
pip install pytest pytest-cov
pytest tests/
```

## Manual Testing Checklist

### X11 Testing
- [ ] Text injection in Firefox/Chrome
- [ ] Text injection in terminal
- [ ] Text injection in VS Code
- [ ] Hotkey Ctrl+Win works globally

### Wayland Testing
- [ ] Text injection with ydotool (if available)
- [ ] Text injection with clipboard fallback
- [ ] Hotkey setup instructions shown
- [ ] Manual hotkey configuration works

### Audio Testing
- [ ] Audio capture starts/stops
- [ ] Recording indicator visible
- [ ] Audio buffer captured correctly
