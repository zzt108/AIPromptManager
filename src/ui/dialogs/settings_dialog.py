"""Settings dialog for configuring application preferences."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from services.settings_service import SettingsService


class SettingsDialog(tk.Toplevel):
    """Dialog for configuring application settings."""

    # Presets for common merge tools
    PRESETS = {
        "P4Merge": {
            "path": r"C:\Program Files\Perforce\p4merge.exe",
            "args_2way": "{left} {right}",
            "args_3way": "{base} {left} {right}",
        },
        "KDiff3": {
            "path": r"C:\Program Files\KDiff3\kdiff3.exe",
            "args_2way": "{left} {right}",
            "args_3way": "{base} {left} {right} -o {output}",
        },
        "WinMerge": {
            "path": r"C:\Program Files\WinMerge\WinMergeU.exe",
            "args_2way": "{left} {right}",
            "args_3way": "{left} {right} {base}",
        },
        "VS Code": {
            "path": "code",
            "args_2way": "--diff {left} {right}",
            "args_3way": "",  # VS Code doesn't robustly support 3-way merge from cmd line in the same way
        },
        "Custom": {"path": "", "args_2way": "", "args_3way": ""},
    }

    def __init__(self, parent: tk.Misc, settings_service: SettingsService):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent widget
            settings_service: Service to manage settings
        """
        super().__init__(parent)
        self.settings_service = settings_service

        self.title("Settings")
        self.geometry("500x450")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._load_current_settings()
        self._setup_ui()

        # Center the dialog
        self.update_idletasks()
        x = (
            parent.winfo_rootx()
            + (parent.winfo_width() // 2)
            - (self.winfo_width() // 2)
        )
        y = (
            parent.winfo_rooty()
            + (parent.winfo_height() // 2)
            - (self.winfo_height() // 2)
        )
        self.geometry(f"+{x}+{y}")

    def _load_current_settings(self) -> None:
        """Load current settings into memory."""
        self.merge_config = self.settings_service.get_merge_tool_config()

    def _setup_ui(self) -> None:
        """Create the UI elements."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # Merge Tool Section
        lf = ttk.LabelFrame(container, text="Merge Tool Configuration", padding="10")
        lf.pack(fill=tk.X, expand=True, pady=5)

        # Preset Selection
        ttk.Label(lf, text="Preset:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.preset_var = tk.StringVar()
        preset_cb = ttk.Combobox(
            lf,
            textvariable=self.preset_var,
            values=list(self.PRESETS.keys()),
            state="readonly",
        )
        preset_cb.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        preset_cb.bind("<<ComboboxSelected>>", self._on_preset_change)

        # Determine current preset
        current_name = self.merge_config.get("name", "Custom")
        if current_name in self.PRESETS:
            self.preset_var.set(current_name)
        else:
            self.preset_var.set("Custom")

        # Path
        ttk.Label(lf, text="Path:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.path_var = tk.StringVar(value=self.merge_config.get("path", ""))
        ttk.Entry(lf, textvariable=self.path_var).grid(
            row=1, column=1, sticky=tk.EW, padx=5, pady=2
        )
        ttk.Button(lf, text="...", width=3, command=self._browse_path).grid(
            row=1, column=2, pady=2
        )

        # 2-Way Args
        ttk.Label(lf, text="2-Way Args:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.args2_var = tk.StringVar(value=self.merge_config.get("args_2way", ""))
        ttk.Entry(lf, textvariable=self.args2_var).grid(
            row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2
        )

        # 3-Way Args
        ttk.Label(lf, text="3-Way Args:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.args3_var = tk.StringVar(value=self.merge_config.get("args_3way", ""))
        ttk.Entry(lf, textvariable=self.args3_var).grid(
            row=3, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2
        )

        # Help Text
        help_text = "Variables: {left}, {right}, {base}, {output}"
        ttk.Label(
            lf, text=help_text, font=("TkSmallCaptionFont", 8), foreground="gray"
        ).grid(row=4, column=1, sticky=tk.W, padx=5)

        lf.columnconfigure(1, weight=1)

        # Spacer
        ttk.Frame(container).pack(fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Save", command=self._save).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _on_preset_change(self, event: tk.Event[tk.Misc]) -> None:
        """Handle preset selection change."""
        selection = self.preset_var.get()
        if selection in self.PRESETS and selection != "Custom":
            preset = self.PRESETS[selection]
            self.path_var.set(preset["path"])
            self.args2_var.set(preset["args_2way"])
            self.args3_var.set(preset["args_3way"])

    def _browse_path(self) -> None:
        """Browse for the executable."""
        filename = filedialog.askopenfilename(
            title="Select Merge Tool Executable",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")],
        )
        if filename:
            self.path_var.set(filename)
            # Switch to custom if we change the path manually? Or keep preset?
            # User might be finding the path for the tool.
            # If current preset is "Custom", stay custom.
            # If current preset is a tool, usually we keep it as that tool but update path.

    def _save(self) -> None:
        """Save settings."""
        # Validate?
        config = {
            "name": self.preset_var.get(),
            "path": self.path_var.get(),
            "args_2way": self.args2_var.get(),
            "args_3way": self.args3_var.get(),
        }

        self.settings_service.set_merge_tool_config(config)
        self.destroy()
