"""Dialog for renaming skills."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Any

from models.skill import Skill

if TYPE_CHECKING:
    from services.naming_service import NamingService


class RenameDialog(tk.Toplevel):
    """Modal dialog for renaming a skill.

    Allows changing Type, Version, and Basename with live preview
    of the resulting filename based on naming conventions.

    Attributes:
        result: Dictionary with new values (type, major, minor, basename)
               or None if cancelled.
    """

    def __init__(
        self,
        parent: tk.Misc,
        skill: Skill,
        naming_service: NamingService | None = None,
    ) -> None:
        """Initialize rename dialog.

        Args:
            parent: Parent widget
            skill: Skill to rename
            naming_service: Service for filename generation (optional)
        """
        super().__init__(parent)
        self.skill = skill
        self.naming_service = naming_service
        self.result: dict[str, Any] | None = None

        self.title("Rename Skill")
        self.geometry("500x350")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)  # type: ignore[call-overload]
        self.grab_set()

        self._init_vars()
        self._setup_ui()
        self._update_preview()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _init_vars(self) -> None:
        """Initialize tracking variables."""
        self.type_var = tk.StringVar(value=self.skill.type)
        self.major_var = tk.IntVar(value=self.skill.major)
        self.minor_var = tk.IntVar(value=self.skill.minor)
        self.basename_var = tk.StringVar(value=self.skill.basename)
        self.preview_var = tk.StringVar()

        # Trace changes for live preview
        self.type_var.trace_add("write", self._update_preview)
        self.major_var.trace_add("write", self._update_preview)
        self.minor_var.trace_add("write", self._update_preview)
        self.basename_var.trace_add("write", self._update_preview)

    def _setup_ui(self) -> None:
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Current Filename
        ttk.Label(main_frame, text="Current Filename:", font=("", 9, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        ttk.Label(main_frame, text=self.skill.path.name).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 15)
        )

        # Input Fields
        inputs_frame = ttk.LabelFrame(main_frame, text="New Properties", padding="10")
        inputs_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Type
        ttk.Label(inputs_frame, text="Type:").grid(row=0, column=0, sticky="w", pady=5)

        # If naming service available, try to use supported types for combobox
        supported_types = []
        if self.naming_service and self.naming_service.conventions:
            supported_types = (
                self.naming_service.conventions.file_naming.supported_types
            )

        if supported_types:
            type_combo = ttk.Combobox(
                inputs_frame,
                textvariable=self.type_var,
                values=supported_types,
                width=20,
            )
            type_combo.grid(row=0, column=1, sticky="w", padx=5)
        else:
            ttk.Entry(inputs_frame, textvariable=self.type_var, width=23).grid(
                row=0, column=1, sticky="w", padx=5
            )

        # Version
        ttk.Label(inputs_frame, text="Version:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        version_frame = ttk.Frame(inputs_frame)
        version_frame.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Spinbox(
            version_frame,
            from_=0,
            to=99,
            textvariable=self.major_var,
            width=3,
        ).pack(side=tk.LEFT)
        ttk.Label(version_frame, text=".").pack(side=tk.LEFT)
        ttk.Spinbox(
            version_frame,
            from_=0,
            to=99,
            textvariable=self.minor_var,
            width=3,
        ).pack(side=tk.LEFT)

        # Basename
        ttk.Label(inputs_frame, text="Name:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(inputs_frame, textvariable=self.basename_var, width=40).grid(
            row=2, column=1, sticky="w", padx=5
        )

        # Preview
        ttk.Label(main_frame, text="Preview New Filename:", font=("", 9, "bold")).grid(
            row=3, column=0, sticky="w", pady=(20, 5)
        )
        ttk.Label(
            main_frame,
            textvariable=self.preview_var,
            foreground="blue",
            font=("Consolas", 10),
        ).grid(row=4, column=0, columnspan=2, sticky="w")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky="e", pady=(20, 0))

        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="Rename", command=self._on_save).pack(
            side=tk.RIGHT
        )

    def _update_preview(self, *args: Any) -> None:
        """Update the filename preview label."""
        try:
            basename = self.basename_var.get()
            type_str = self.type_var.get()
            major = self.major_var.get()
            minor = self.minor_var.get()

            if not basename or not type_str:
                self.preview_var.set("(Invalid input)")
                return

            if self.naming_service:
                filename = self.naming_service.make_versioned(
                    basename=basename,
                    major=major,
                    minor=minor,
                    type_str=type_str,
                )
            else:
                filename = f"{type_str}-{major}-{minor}-{basename}.md"

            self.preview_var.set(filename)

        except (tk.TclError, ValueError):
            self.preview_var.set("(Invalid input)")

    def _on_save(self) -> None:
        """Validate and save result."""
        try:
            basename = self.basename_var.get().strip()
            type_str = self.type_var.get().strip()
            major = self.major_var.get()
            minor = self.minor_var.get()

            if not basename:
                messagebox.showerror("Error", "Name cannot be empty.", parent=self)
                return
            if not type_str:
                messagebox.showerror("Error", "Type cannot be empty.", parent=self)
                return

            self.result = {
                "type": type_str,
                "major": major,
                "minor": minor,
                "basename": basename,
            }
            self.destroy()

        except tk.TclError:
            messagebox.showerror("Error", "Invalid numeric values.", parent=self)
