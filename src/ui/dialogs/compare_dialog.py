"""Dialog for comparing skills."""

from __future__ import annotations

import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from typing import TYPE_CHECKING, List

import structlog

if TYPE_CHECKING:
    from services.settings_service import SettingsService
    from services.registry_service import RegistryService

logger = structlog.get_logger(__name__)


class CompareDialog(tk.Toplevel):
    """Dialog for configuring and launching a merge tool comparison."""

    def __init__(
        self,
        parent: tk.Misc,
        settings_service: SettingsService,
        registry_service: RegistryService,
        selected_files: List[Path],
    ):
        """
        Initialize the comparison dialog.

        Args:
            parent: Parent widget
            settings_service: Service to retrieve tool config
            registry_service: Service to resolve paths (if needed, or just pass full paths)
            selected_files: List of absolute paths to files to compare
        """
        super().__init__(parent)
        self.settings_service = settings_service
        self.registry_service = registry_service
        self.selected_files = selected_files

        # Validation
        if not (2 <= len(selected_files) <= 3):
            messagebox.showerror("Error", "Please select 2 or 3 files to compare.")
            self.destroy()
            return

        self.title("Compare Files")
        self.geometry("500x350")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

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

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        container = ttk.Frame(self, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Assign roles for comparison:",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 10))

        # We will use filenames for display, map back to paths
        self.file_map = {p.name: p for p in self.selected_files}
        filenames = list(self.file_map.keys())

        # Left File
        ttk.Label(container, text="Left (Local/Source):").pack(anchor=tk.W)
        self.left_var = tk.StringVar(value=filenames[0])
        left_cb = ttk.Combobox(
            container, textvariable=self.left_var, values=filenames, state="readonly"
        )
        left_cb.pack(fill=tk.X, pady=(0, 10))

        # Right File
        ttk.Label(container, text="Right (Remote/Target):").pack(anchor=tk.W)
        self.right_var = tk.StringVar(value=filenames[1])
        right_cb = ttk.Combobox(
            container, textvariable=self.right_var, values=filenames, state="readonly"
        )
        right_cb.pack(fill=tk.X, pady=(0, 10))

        # Base File (Optional/3-Way)
        ttk.Label(container, text="Base (Ancestor) - Optional for 2-way:").pack(
            anchor=tk.W
        )
        base_val = filenames[2] if len(filenames) > 2 else ""
        self.base_var = tk.StringVar(value=base_val)
        base_cb = ttk.Combobox(
            container,
            textvariable=self.base_var,
            values=[""] + filenames,
            state="readonly",
        )
        base_cb.pack(fill=tk.X, pady=(0, 10))

        # Info
        config = self.settings_service.get_merge_tool_config()
        tool_name = config.get("name", "Unknown")
        ttk.Label(container, text=f"Using Tool: {tool_name}", foreground="gray").pack(
            anchor=tk.W, pady=5
        )

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        ttk.Button(btn_frame, text="Launch Compare", command=self._launch).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def _launch(self) -> None:
        """Construct command and launch."""
        left_name = self.left_var.get()
        right_name = self.right_var.get()
        base_name = self.base_var.get()

        if not left_name or not right_name:
            messagebox.showwarning(
                "Validation", "Left and Right files must be selected."
            )
            return

        if left_name == right_name:
            messagebox.showwarning(
                "Validation", "Left and Right files must be different."
            )
            return

        left_path = str(self.file_map[left_name])
        right_path = str(self.file_map[right_name])
        base_path = str(self.file_map[base_name]) if base_name else ""

        config = self.settings_service.get_merge_tool_config()
        exe_path = config.get("path", "")

        if not exe_path:
            messagebox.showerror(
                "Configuration Error",
                "No merge tool path configured. Please go to Settings.",
            )
            return

        # Prepare arguments
        if base_path:
            # 3-Way
            args_template = config.get("args_3way", "")
            if not args_template:
                # Fallback to 2-way if 3-way not configured but base provided? Or error?
                # Better to error or warn.
                args_template = config.get("args_2way", "")  # Fallback attempt
        else:
            # 2-Way
            args_template = config.get("args_2way", "")

        if not args_template:
            messagebox.showerror(
                "Configuration Error", "Merge tool arguments not configured."
            )
            return

        # Format command
        # We need to be careful with quoting. subprocess.Popen with a list is best,
        # but the template is a string. We might need to parse it or use shell=True (risky but easier for user templates).
        # Actually, let's substitute python-style format strings.

        # NOTE: Users might put quotes in the template.
        # Best approach: replace placeholders, then split by shlex?
        # Or just format the whole string and pass as string with shell=False?
        # No, passing a single string requires shell=True on Windows usually, or careful splitting.
        # Let's try simple replacement and subprocess.Popen([exe, arg1, ...]) but we don't know where args split.

        # Simple approach: Replace in the full argument string, then run.
        # But if paths have spaces, they need quotes.
        # I will ensure paths are quoted if they contain spaces.

        def quote(s: str) -> str:
            return f'"{s}"' if " " in s else s

        # Actually, let's interpret the template.
        cmd_args = (
            args_template.replace("{left}", quote(left_path))
            .replace("{right}", quote(right_path))
            .replace("{base}", quote(base_path))
            .replace("{output}", quote(left_path))
        )  # Output usually overwrites left or asks

        # Full command
        full_cmd = f'"{exe_path}" {cmd_args}'

        logger.info("launching_merge_tool", command=full_cmd)

        try:
            subprocess.Popen(
                full_cmd, shell=True
            )  # shell=True to handle the command string parsing on Windows
            self.destroy()
        except Exception as e:
            logger.error("merge_tool_launch_failed", error=str(e))
            messagebox.showerror("Launch Error", f"Failed to launch tool:\n{e}")
