"""Quick View dialog for displaying and editing skill details."""

from __future__ import annotations

import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable

import structlog

if TYPE_CHECKING:
    from services.registry_service import RegistryService

logger = structlog.get_logger(__name__)


class QuickViewDialog(tk.Toplevel):
    """Dialog for viewing and editing skill details."""

    def __init__(
        self,
        parent: tk.Misc,
        service: RegistryService,
        skill_name: str,
        on_update: Callable[[], None] | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            parent: Parent widget
            service: Registry service for data operations
            skill_name: Name of the skill to view
            on_update: Callback function to run after a successful update (e.g. refresh list)
        """
        super().__init__(parent)
        self.service = service
        self.skill_name = skill_name
        self.on_update = on_update

        self.title(f"Quick View: {skill_name}")
        self.geometry("600x500")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._load_and_show()

    def _load_and_show(self) -> None:
        """Load skill data and setup UI."""
        skill = self.service.get_skill(self.skill_name)
        if not skill:
            messagebox.showwarning(
                "Quick View", f"Skill '{self.skill_name}' not found."
            )
            self.destroy()
            return

        self.file_path = self.service.repo_root / skill.path
        if not self.file_path.exists():
            messagebox.showwarning("Quick View", f"File not found: {self.file_path}")
            self.destroy()
            return

        try:
            content = self.file_path.read_text(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Quick View", f"Error reading file: {e}")
            self.destroy()
            return

        h1, summary, toc = self._parse_markdown_preview(content)
        self._setup_ui(h1, summary, toc)

    def _parse_markdown_preview(self, content: str) -> tuple[str, str, list[str]]:
        """Parse markdown content for Quick View display."""
        lines = content.splitlines()
        h1 = ""
        summary = ""
        toc: list[str] = []
        in_summary = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("# ") and not h1:
                h1 = stripped[2:].strip()
                in_summary = True
                continue

            if in_summary:
                if stripped.startswith("#"):
                    in_summary = False
                elif stripped:
                    if not summary:
                        summary = stripped
                    else:
                        pass
                elif summary:
                    in_summary = False

            if stripped.startswith("## "):
                toc.append(stripped[3:].strip())

        return h1, summary, toc

    def _setup_ui(self, h1: str, summary: str, toc: list[str]) -> None:
        """Create UI elements."""
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # H1 Edit Frame
        h1_frame = ttk.Frame(container)
        h1_frame.pack(fill=tk.X, pady=(0, 10))

        self.h1_var = tk.StringVar(value=h1)
        h1_entry = ttk.Entry(
            h1_frame, textvariable=self.h1_var, font=("TkDefaultFont", 12, "bold")
        )
        h1_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        save_btn = ttk.Button(h1_frame, text="💾 Save", command=self._save_h1, width=8)
        save_btn.pack(side=tk.LEFT)

        # Summary
        if summary:
            summary_label = ttk.Label(container, text=summary, wraplength=550)
            summary_label.pack(anchor=tk.W, pady=(0, 10))

        # TOC
        if toc:
            toc_label = ttk.Label(
                container, text="Contents:", font=("TkDefaultFont", 10, "bold")
            )
            toc_label.pack(anchor=tk.W, pady=(5, 2))
            for heading in toc:
                h2_label = ttk.Label(container, text=f"  • {heading}")
                h2_label.pack(anchor=tk.W)

        # Spacer
        ttk.Frame(container).pack(fill=tk.BOTH, expand=True)

        # Action Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            btn_frame, text="📝 Open in Editor", command=self._open_with_editor
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame, text="📝 Open in Notepad", command=self._open_with_notepad
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)

        # Center popup
        self.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _save_h1(self) -> None:
        """Save the updated H1 to the file."""
        new_h1 = self.h1_var.get().strip()
        if not new_h1:
            messagebox.showwarning("Save H1", "Title cannot be empty.")
            return

        if self.service.update_skill_h1(self.skill_name, new_h1):
            if self.on_update:
                self.on_update()
            self.destroy()
        else:
            messagebox.showerror("Save H1", "Failed to update title.")

    def _open_with_editor(self) -> None:
        """Open file with default editor."""
        try:
            if platform.system() == "Windows":
                os.startfile(self.file_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", self.file_path], check=False)
            else:
                subprocess.run(["xdg-open", self.file_path], check=False)
            logger.info("quick_view_open_editor", path=str(self.file_path))
        except Exception as e:
            logger.error("quick_view_open_editor_error", error=str(e))
            messagebox.showerror("Error", f"Could not open file: {e}")

    def _open_with_notepad(self) -> None:
        """Open file with Notepad."""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["notepad.exe", str(self.file_path)])
            else:
                self._open_with_editor()
            logger.info("quick_view_open_notepad", path=str(self.file_path))
        except Exception as e:
            logger.error("quick_view_open_notepad_error", error=str(e))
            messagebox.showerror("Error", f"Could not open Notepad: {e}")
