"""Settings dialog for Talky."""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from ..whisper.languages import get_all_languages

if TYPE_CHECKING:
    from ..main import TalkyApp

logger = logging.getLogger(__name__)


class SettingsDialog:
    """Settings dialog window."""

    # Available Whisper models
    WHISPER_MODELS = [
        "tiny",
        "tiny.en",
        "base",
        "base.en",
        "small",
        "small.en",
        "medium",
        "medium.en",
        "large-v1",
        "large-v2",
        "large-v3",
    ]

    # Device options
    DEVICE_OPTIONS = [
        ("auto", "Auto-detect (CUDA if available, else CPU)"),
        ("cuda", "CUDA (GPU)"),
        ("cpu", "CPU only"),
    ]

    def __init__(self, app: 'TalkyApp'):
        """
        Initialize settings dialog.

        Args:
            app: TalkyApp instance
        """
        self.app = app
        self.window = None
        self.modified = False

        # Setting variables
        self.model_var = None
        self.language_var = None
        self.device_var = None
        self.hotkey_var = None

    def show(self):
        """Show settings dialog."""
        try:
            self._create_window()
        except Exception as e:
            logger.error(f"Failed to create settings window: {e}")
            if self.app.tray_manager:
                self.app.tray_manager.notify_error(f"Failed to open settings: {e}")

    def _create_window(self):
        """Create settings window."""
        self.window = tk.Tk()
        self.window.title("Talky Settings")
        self.window.geometry("600x500")
        self.window.resizable(False, False)

        # Create notebook (tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs
        general_tab = ttk.Frame(notebook)
        whisper_tab = ttk.Frame(notebook)
        hotkeys_tab = ttk.Frame(notebook)
        platform_tab = ttk.Frame(notebook)

        notebook.add(general_tab, text="General")
        notebook.add(whisper_tab, text="Whisper")
        notebook.add(hotkeys_tab, text="Hotkeys")
        notebook.add(platform_tab, text="Platform")

        # Populate tabs
        self._create_general_tab(general_tab)
        self._create_whisper_tab(whisper_tab)
        self._create_hotkeys_tab(hotkeys_tab)
        self._create_platform_tab(platform_tab)

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        ttk.Button(
            button_frame,
            text="Save",
            command=self._on_save
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Apply",
            command=self._on_apply
        ).pack(side=tk.RIGHT, padx=5)

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

        self.window.mainloop()

    def _create_general_tab(self, parent):
        """Create general settings tab."""
        frame = ttk.LabelFrame(parent, text="General Settings", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Version info
        try:
            from ..version import __version__
            version = __version__
        except ImportError:
            version = "unknown"

        ttk.Label(
            frame,
            text=f"Talky Version: {version}",
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor=tk.W, pady=5)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Config file location
        config_path = self.app.config.config_path
        ttk.Label(frame, text="Configuration File:").pack(anchor=tk.W, pady=5)
        config_entry = ttk.Entry(frame, width=70)
        config_entry.insert(0, str(config_path))
        config_entry.config(state="readonly")
        config_entry.pack(anchor=tk.W, pady=5)

        ttk.Label(
            frame,
            text="Note: Some changes require restarting Talky to take effect.",
            foreground="gray"
        ).pack(anchor=tk.W, pady=10)

    def _create_whisper_tab(self, parent):
        """Create Whisper settings tab."""
        frame = ttk.LabelFrame(parent, text="Whisper Configuration", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Model selection
        ttk.Label(frame, text="Model:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, pady=(5, 2))
        self.model_var = tk.StringVar(value=self.app.config.whisper.model)

        model_frame = ttk.Frame(frame)
        model_frame.pack(fill=tk.X, pady=5)

        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=self.WHISPER_MODELS,
            state="readonly",
            width=20
        )
        model_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(
            model_frame,
            text="(tiny=fast, large=accurate)",
            foreground="gray"
        ).pack(side=tk.LEFT)

        # Language selection
        ttk.Label(frame, text="Language:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, pady=(15, 2))
        current_lang = self.app.config.whisper.language or "auto"
        self.language_var = tk.StringVar(value=current_lang)

        all_languages = get_all_languages()
        language_options = [f"{code} - {name}" for code, name in sorted(all_languages.items(), key=lambda x: x[1])]

        language_combo = ttk.Combobox(
            frame,
            textvariable=self.language_var,
            values=language_options,
            state="readonly",
            width=30
        )
        # Set current value
        for opt in language_options:
            if opt.startswith(f"{current_lang} -"):
                language_combo.set(opt)
                break
        language_combo.pack(anchor=tk.W, pady=5)

        # Device selection
        ttk.Label(frame, text="Device:", font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, pady=(15, 2))
        current_device = self.app.config.whisper.device
        self.device_var = tk.StringVar(value=current_device)

        for device_code, device_name in self.DEVICE_OPTIONS:
            ttk.Radiobutton(
                frame,
                text=device_name,
                variable=self.device_var,
                value=device_code
            ).pack(anchor=tk.W, pady=2)

        # CUDA availability
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                cuda_name = torch.cuda.get_device_name(0)
                status_text = f"✓ CUDA Available: {cuda_name}"
                status_color = "green"
            else:
                status_text = "✗ CUDA not available (CPU only)"
                status_color = "orange"
        except ImportError:
            status_text = "PyTorch not installed (CUDA detection unavailable)"
            status_color = "gray"

        ttk.Label(
            frame,
            text=status_text,
            foreground=status_color
        ).pack(anchor=tk.W, pady=10)

    def _create_hotkeys_tab(self, parent):
        """Create hotkeys settings tab."""
        frame = ttk.LabelFrame(parent, text="Hotkey Configuration", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(
            frame,
            text="Push-to-Talk Hotkey:",
            font=("TkDefaultFont", 9, "bold")
        ).pack(anchor=tk.W, pady=5)

        self.hotkey_var = tk.StringVar(value=self.app.config.hotkeys.toggle_recording)

        hotkey_entry = ttk.Entry(frame, textvariable=self.hotkey_var, width=30)
        hotkey_entry.pack(anchor=tk.W, pady=5)

        ttk.Label(
            frame,
            text="Examples: <ctrl>+<super>, <ctrl>+<alt>+r, <shift>+<ctrl>+space",
            foreground="gray"
        ).pack(anchor=tk.W, pady=5)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        ttk.Label(
            frame,
            text="Note: Hotkey changes require restarting Talky.",
            foreground="orange"
        ).pack(anchor=tk.W, pady=5)

    def _create_platform_tab(self, parent):
        """Create platform information tab."""
        frame = ttk.LabelFrame(parent, text="Platform Information", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        platform = self.app.platform

        # Display server
        ttk.Label(
            frame,
            text=f"Display Server: {platform.display_server.value}",
            font=("TkDefaultFont", 9)
        ).pack(anchor=tk.W, pady=5)

        # Desktop environment
        ttk.Label(
            frame,
            text=f"Desktop Environment: {platform.desktop_environment.value}",
            font=("TkDefaultFont", 9)
        ).pack(anchor=tk.W, pady=5)

        # CUDA support
        cuda_status = "✓ Available" if platform.has_cuda else "✗ Not available"
        ttk.Label(
            frame,
            text=f"CUDA: {cuda_status}",
            font=("TkDefaultFont", 9)
        ).pack(anchor=tk.W, pady=5)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Available tools
        ttk.Label(
            frame,
            text="Available Tools:",
            font=("TkDefaultFont", 9, "bold")
        ).pack(anchor=tk.W, pady=5)

        tools_frame = ttk.Frame(frame)
        tools_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Check for tools
        tools = {
            "xdotool": platform.has_tool("xdotool"),
            "ydotool": platform.has_tool("ydotool"),
        }

        for tool, available in tools.items():
            status = "✓" if available else "✗"
            color = "green" if available else "red"
            ttk.Label(
                tools_frame,
                text=f"{status} {tool}",
                foreground=color
            ).pack(anchor=tk.W, pady=2)

    def _on_apply(self):
        """Apply settings without closing."""
        try:
            self._save_settings()
            messagebox.showinfo("Success", "Settings applied successfully!\n\nNote: Some changes require restarting Talky.")
            self.modified = True
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            messagebox.showerror("Error", f"Failed to apply settings:\n{e}")

    def _on_save(self):
        """Save settings and close."""
        try:
            self._save_settings()
            self.window.destroy()
            if self.app.tray_manager:
                self.app.tray_manager.notify_info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")

    def _on_cancel(self):
        """Cancel and close without saving."""
        self.window.destroy()

    def _save_settings(self):
        """Save current settings to config."""
        # Update Whisper settings
        self.app.config.whisper.model = self.model_var.get()

        # Extract language code from selection
        lang_selection = self.language_var.get()
        if " - " in lang_selection:
            lang_code = lang_selection.split(" - ")[0]
        else:
            lang_code = lang_selection

        self.app.config.whisper.language = None if lang_code == "auto" else lang_code
        self.app.config.whisper.device = self.device_var.get()

        # Update hotkey
        self.app.config.hotkeys.toggle_recording = self.hotkey_var.get()

        # Save config file
        self.app.config.save()

        # Update runtime whisper engine language
        if self.app.whisper_engine:
            self.app.whisper_engine.language = self.app.config.whisper.language

        logger.info("Settings saved successfully")
