"""Dialog for moving skills."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import TYPE_CHECKING


class MoveDialog(tk.Toplevel):
    """Modal dialog for moving skills to a folder.

    Attributes:
        result: The selected destination folder path (str, relative to repo_root)
               or None if cancelled.
    """

    def __init__(
        self,
        parent: tk.Misc,
        repo_root: Path,
        initial_dir: Path | None = None,
        count: int = 1,
    ) -> None:
        """Initialize move dialog.

        Args:
            parent: Parent widget
            repo_root: Root path of the repository
            initial_dir: Initial directory for browse dialog (optional)
            count: Number of items being moved (for display)
        """
        super().__init__(parent)
        self.repo_root = repo_root
        self.initial_dir = initial_dir
        self.count = count
        self.result: str | None = None

        self.title(f"Move {count} Skill{'s' if count > 1 else ''}")
        self.geometry("500x150")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)  # type: ignore[call-overload]
        self.grab_set()

        self._init_vars()
        self._setup_ui()

        # Center dialog
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
            y = (
                parent.winfo_rooty()
                + (parent.winfo_height() - self.winfo_height()) // 2
            )
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _init_vars(self) -> None:
        """Initialize tracking variables."""
        self.dest_var = tk.StringVar()

    def _setup_ui(self) -> None:
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Info Label
        msg = f"Move {self.count} item{'s' if self.count > 1 else ''} to folder:"
        ttk.Label(main_frame, text=msg, font=("", 10)).pack(anchor="w", pady=(0, 10))

        # Folder Selection Row
        row_frame = ttk.Frame(main_frame)
        row_frame.pack(fill=tk.X, pady=(0, 20))

        self.entry = ttk.Entry(row_frame, textvariable=self.dest_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(row_frame, text="Browse...", command=self._on_browse).pack(
            side=tk.LEFT
        )

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="Move", command=self._on_move).pack(side=tk.RIGHT)

    def _on_browse(self) -> None:
        """Open directory browser."""
        start_dir = self.initial_dir if self.initial_dir else self.repo_root

        selected = filedialog.askdirectory(
            parent=self,
            title="Select Destination Folder",
            initialdir=start_dir,
            mustexist=True,
        )

        if selected:
            try:
                # Convert to relative path
                abs_path = Path(selected)
                # Check if it's within repo_root
                if (
                    self.repo_root not in abs_path.parents
                    and abs_path != self.repo_root
                ):
                    # It's outside repo, this might be tricky.
                    # For now, let's allow it but the service expects relative path?
                    # The service uses: dest_path_root = self.repo_root / dest_folder
                    # So dest_folder MUST be relative.
                    # If user picks outside, we should warn.
                    messagebox.showwarning(
                        "Invalid Selection",
                        "Please select a folder inside the repository.",
                        parent=self,
                    )
                    return

                rel_path = abs_path.relative_to(self.repo_root)
                self.dest_var.set(str(rel_path))
            except ValueError:
                # Happens if relative_to fails (different drive, etc)
                messagebox.showwarning(
                    "Invalid Selection",
                    "Please select a folder inside the repository.",
                    parent=self,
                )

    def _on_move(self) -> None:
        """Validate and save result."""
        dest = self.dest_var.get().strip()
        if not dest:
            messagebox.showerror(
                "Error", "Please select a destination folder.", parent=self
            )
            return

        # Determine strict path validation?
        # Service expects relative path string.
        # We trust the entry content (user could edit manually).

        self.result = dest
        self.destroy()
