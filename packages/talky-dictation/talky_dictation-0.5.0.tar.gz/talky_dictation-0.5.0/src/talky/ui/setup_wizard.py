"""First-run setup wizard for Talky."""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional
from pathlib import Path

from ..whisper.languages import get_all_languages, get_popular_languages

if TYPE_CHECKING:
    from ..main import TalkyApp

logger = logging.getLogger(__name__)


class SetupWizard:
    """First-run setup wizard."""

    def __init__(self, app: 'TalkyApp'):
        """
        Initialize setup wizard.

        Args:
            app: TalkyApp instance
        """
        self.app = app
        self.window = None
        self.current_page = 0

        # Setting variables
        self.model_var = None
        self.language_var = None
        self.autostart_var = None

    def show(self) -> bool:
        """
        Show setup wizard.

        Returns:
            True if setup completed, False if cancelled
        """
        try:
            return self._create_window()
        except Exception as e:
            logger.error(f"Setup wizard error: {e}")
            return False

    def _create_window(self) -> bool:
        """Create and show setup wizard window."""
        self.window = tk.Tk()
        self.window.title("Talky - First Run Setup")
        self.window.geometry("700x550")
        self.window.resizable(False, False)

        # Make modal
        self.window.grab_set()

        self.completed = False

        # Create pages
        self.pages = [
            self._create_welcome_page,
            self._create_platform_page,
            self._create_whisper_page,
            self._create_final_page,
        ]

        # Container for pages
        self.page_container = ttk.Frame(self.window)
        self.page_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Navigation buttons
        nav_frame = ttk.Frame(self.window)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        self.back_btn = ttk.Button(
            nav_frame,
            text="< Back",
            command=self._previous_page,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT)

        self.next_btn = ttk.Button(
            nav_frame,
            text="Next >",
            command=self._next_page
        )
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        self.cancel_btn = ttk.Button(
            nav_frame,
            text="Cancel",
            command=self._on_cancel
        )
        self.cancel_btn.pack(side=tk.RIGHT)

        # Show first page
        self._show_page(0)

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

        self.window.mainloop()

        return self.completed

    def _show_page(self, page_index: int):
        """Show specific page."""
        # Clear container
        for widget in self.page_container.winfo_children():
            widget.destroy()

        # Create page
        self.pages[page_index]()

        # Update buttons
        self.current_page = page_index
        self.back_btn.config(state=tk.NORMAL if page_index > 0 else tk.DISABLED)

        if page_index == len(self.pages) - 1:
            self.next_btn.config(text="Finish", command=self._on_finish)
        else:
            self.next_btn.config(text="Next >", command=self._next_page)

    def _next_page(self):
        """Go to next page."""
        if self.current_page < len(self.pages) - 1:
            self._show_page(self.current_page + 1)

    def _previous_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self._show_page(self.current_page - 1)

    def _create_welcome_page(self):
        """Create welcome page."""
        frame = ttk.Frame(self.page_container)
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            frame,
            text="Welcome to Talky!",
            font=("TkDefaultFont", 18, "bold")
        ).pack(pady=20)

        # Description
        desc_text = (
            "Talky is a system-wide dictation application for Linux\n"
            "using OpenAI's Whisper AI for speech-to-text.\n\n"
            "This wizard will help you configure Talky for first use.\n\n"
            "Features:\n"
            "  • Push-to-talk hotkey (default: Ctrl+Win)\n"
            "  • Multi-language support (99 languages)\n"
            "  • Fast transcription with CUDA acceleration\n"
            "  • Works in any application\n"
        )

        ttk.Label(
            frame,
            text=desc_text,
            justify=tk.LEFT,
            font=("TkDefaultFont", 10)
        ).pack(pady=20, padx=40)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        ttk.Label(
            frame,
            text="Click 'Next' to continue",
            foreground="gray"
        ).pack()

    def _create_platform_page(self):
        """Create platform detection page."""
        frame = ttk.Frame(self.page_container)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="Platform Detection",
            font=("TkDefaultFont", 16, "bold")
        ).pack(pady=20)

        platform = self.app.platform

        # Platform info
        info_frame = ttk.LabelFrame(frame, text="System Information", padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        info_text = f"""
Display Server: {platform.display_server.value}
Desktop Environment: {platform.desktop_environment.value}
CUDA Available: {'Yes' if platform.has_cuda else 'No'}
xdotool: {'Available' if platform.has_tool('xdotool') else 'Not found'}
ydotool: {'Available' if platform.has_tool('ydotool') else 'Not found'}
"""

        ttk.Label(
            info_frame,
            text=info_text,
            justify=tk.LEFT,
            font=("TkDefaultFont", 10)
        ).pack()

        # Warnings for Wayland
        if platform.display_server.value == "wayland":
            warning_frame = ttk.LabelFrame(frame, text="⚠️ Wayland Setup Required", padding=20)
            warning_frame.pack(fill=tk.X, pady=10)

            warning_text = (
                "Wayland requires additional setup:\n\n"
                "1. For text injection, install ydotool:\n"
                "   sudo apt install ydotool  # Debian/Ubuntu\n"
                "   sudo dnf install ydotool  # Fedora\n\n"
                "2. Add your user to input/uinput groups:\n"
                "   sudo usermod -aG input,uinput $USER\n\n"
                "3. Configure udev rules (see documentation)\n\n"
                "Note: Logout/login required after group changes"
            )

            ttk.Label(
                warning_frame,
                text=warning_text,
                justify=tk.LEFT,
                foreground="orange",
                font=("TkDefaultFont", 9)
            ).pack()

    def _create_whisper_page(self):
        """Create Whisper configuration page."""
        frame = ttk.Frame(self.page_container)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="Whisper Configuration",
            font=("TkDefaultFont", 16, "bold")
        ).pack(pady=20)

        config_frame = ttk.Frame(frame)
        config_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Model selection
        ttk.Label(
            config_frame,
            text="Select Whisper Model:",
            font=("TkDefaultFont", 11, "bold")
        ).pack(anchor=tk.W, pady=(10, 5))

        ttk.Label(
            config_frame,
            text="Larger models are more accurate but slower",
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0, 10))

        self.model_var = tk.StringVar(value="base")

        models = [
            ("tiny", "Tiny - Fastest, least accurate"),
            ("base", "Base - Recommended for most users"),
            ("small", "Small - Good balance"),
            ("medium", "Medium - More accurate, slower"),
            ("large-v3", "Large - Most accurate, requires powerful GPU"),
        ]

        for value, label in models:
            ttk.Radiobutton(
                config_frame,
                text=label,
                variable=self.model_var,
                value=value
            ).pack(anchor=tk.W, pady=2)

        ttk.Separator(config_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # Language selection
        ttk.Label(
            config_frame,
            text="Select Language:",
            font=("TkDefaultFont", 11, "bold")
        ).pack(anchor=tk.W, pady=(5, 10))

        self.language_var = tk.StringVar(value="auto")

        language_combo = ttk.Combobox(
            config_frame,
            textvariable=self.language_var,
            state="readonly",
            width=30
        )

        # Populate with popular languages
        all_languages = get_all_languages()
        popular = get_popular_languages()

        language_options = []
        for code in popular[:10]:  # Top 10 popular
            language_options.append(f"{code} - {all_languages[code]}")

        language_combo['values'] = language_options
        language_combo.set("auto - Auto-detect")
        language_combo.pack(anchor=tk.W)

        ttk.Label(
            config_frame,
            text="You can change this later in settings",
            foreground="gray"
        ).pack(anchor=tk.W, pady=5)

    def _create_final_page(self):
        """Create final configuration page."""
        frame = ttk.Frame(self.page_container)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="Setup Complete!",
            font=("TkDefaultFont", 16, "bold")
        ).pack(pady=20)

        # Summary
        summary_frame = ttk.LabelFrame(frame, text="Configuration Summary", padding=20)
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        model = self.model_var.get() if self.model_var else "base"
        lang = self.language_var.get() if self.language_var else "auto"

        summary_text = f"""
Whisper Model: {model}
Language: {lang}
Hotkey: {self.app.config.hotkeys.toggle_recording}

Platform: {self.app.platform.display_server.value}
"""

        ttk.Label(
            summary_frame,
            text=summary_text,
            justify=tk.LEFT,
            font=("TkDefaultFont", 10)
        ).pack()

        # Autostart option
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        self.autostart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="Start Talky automatically on login",
            variable=self.autostart_var
        ).pack(pady=10)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        ttk.Label(
            frame,
            text="Click 'Finish' to complete setup and start Talky",
            foreground="gray"
        ).pack()

    def _on_finish(self):
        """Finish setup and save configuration."""
        try:
            # Apply settings
            if self.model_var:
                self.app.config.whisper.model = self.model_var.get()

            if self.language_var:
                lang = self.language_var.get()
                if " - " in lang:
                    lang = lang.split(" - ")[0]
                self.app.config.whisper.language = None if lang == "auto" else lang

            # Save config
            self.app.config.save()

            # Handle autostart
            if self.autostart_var and self.autostart_var.get():
                try:
                    from ..autostart import AutostartManager
                    autostart = AutostartManager()
                    autostart.enable()
                except Exception as e:
                    logger.warning(f"Failed to enable autostart: {e}")

            # Mark setup as complete
            self._mark_setup_complete()

            self.completed = True
            self.window.destroy()

        except Exception as e:
            logger.error(f"Failed to complete setup: {e}")
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")

    def _on_cancel(self):
        """Cancel setup."""
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel setup?"):
            self.completed = False
            self.window.destroy()

    def _mark_setup_complete(self):
        """Mark first-run setup as complete."""
        try:
            # Create marker file in config directory
            config_dir = Path(self.app.config.config_path).parent
            marker_file = config_dir / ".setup_complete"
            marker_file.touch()
            logger.info("Setup marked as complete")
        except Exception as e:
            logger.warning(f"Failed to create setup marker: {e}")

    @staticmethod
    def should_show(config_path: Optional[Path] = None) -> bool:
        """
        Check if setup wizard should be shown.

        Args:
            config_path: Path to config file

        Returns:
            True if wizard should be shown
        """
        try:
            from ..utils.config import Config

            if config_path is None:
                config_path = Config.get_default_config_path()

            config_dir = Path(config_path).parent
            marker_file = config_dir / ".setup_complete"

            # Show if marker doesn't exist
            return not marker_file.exists()

        except Exception as e:
            logger.warning(f"Failed to check setup status: {e}")
            return False
