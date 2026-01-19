"""Dialogs for file synchronization conflict resolution."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable

from models.sync_types import SyncAction, SyncTask


@dataclass
class DialogResult:
    """Result from a sync dialog."""

    action: SyncAction
    apply_to_all: bool = False


class BaseSyncDialog(tk.Toplevel):
    """Base class for sync conflict dialogs."""

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        message: str,
        task: SyncTask,
    ) -> None:
        """Initialize dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Main message text
            task: The sync task causing the conflict
        """
        super().__init__(parent)
        self.title(title)
        self.task = task
        self.result: DialogResult | None = None

        self._setup_window()
        self._setup_ui(message)

        # Make modal
        self.transient(parent)  # type: ignore

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.geometry("600x400")
        self.resizable(False, False)

        # Center on parent
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - 600) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")

    def _setup_ui(self, message: str) -> None:
        """Setup common UI elements."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Icon/Title (Placeholder for icon)
        title_lbl = ttk.Label(
            main_frame, text=f"⚠️ {self.title()}", font=("Segoe UI", 12, "bold")
        )
        title_lbl.pack(anchor=tk.W, pady=(0, 10))

        # File Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="File Details", padding=10)
        info_frame.pack(fill=tk.X, pady=10)

        grid_opts = {"sticky": "w", "pady": 2}
        ttk.Label(info_frame, text="File:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, **grid_opts)  # type: ignore
        ttk.Label(info_frame, text=self.task.target_filename).grid(row=0, column=1, **grid_opts)  # type: ignore

        ttk.Label(info_frame, text="Ingredient:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, **grid_opts)  # type: ignore
        ttk.Label(info_frame, text=self.task.ingredient.name).grid(row=1, column=1, **grid_opts)  # type: ignore

        # Custom Message
        msg_lbl = ttk.Label(main_frame, text=message, wraplength=550)
        msg_lbl.pack(fill=tk.X, pady=10)

        # Buttons Frame
        self.btn_frame = ttk.Frame(main_frame)
        self.btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

    def _finish(self, action: SyncAction) -> None:
        """Close dialog and set result."""
        self.result = DialogResult(action=action)
        self.destroy()


class UpdateAvailableDialog(BaseSyncDialog):
    """Dialog shown when source file is newer than target."""

    def __init__(self, parent: tk.Widget, task: SyncTask) -> None:
        super().__init__(
            parent,
            title="Update Available",
            message=(
                "A newer version of this file exists in the source library.\n\n"
                f"Source: {task.source_path}\n"
                f"Target: {task.target_path}\n\n"
                "Do you want to overwrite your local file with the newer version?"
            ),
            task=task,
        )

    def _setup_ui(self, message: str) -> None:
        super()._setup_ui(message)

        # Actions
        ttk.Button(
            self.btn_frame,
            text="Overwrite Target (Update)",
            command=lambda: self._finish(SyncAction.COPY),
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            self.btn_frame, text="Skip", command=lambda: self._finish(SyncAction.SKIP)
        ).pack(side=tk.RIGHT, padx=5)


class LocalChangesDialog(BaseSyncDialog):
    """Dialog shown when target file is newer than source."""

    def __init__(self, parent: tk.Widget, task: SyncTask) -> None:
        super().__init__(
            parent,
            title="Local Changes Detected",
            message=(
                "Your local file is newer than the source in the library.\n"
                "This usually means you have made local modifications.\n\n"
                f"Target (Local): {task.target_path}\n"
                f"Source (Repo):  {task.source_path}\n\n"
                "How would you like to proceed?"
            ),
            task=task,
        )

    def _setup_ui(self, message: str) -> None:
        super()._setup_ui(message)

        # Actions
        ttk.Button(
            self.btn_frame,
            text="Update Source (Push)",
            command=lambda: self._finish(SyncAction.UPDATE_SOURCE),
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            self.btn_frame,
            text="Keep Local (Skip)",
            command=lambda: self._finish(SyncAction.SKIP),
        ).pack(side=tk.RIGHT, padx=5)
