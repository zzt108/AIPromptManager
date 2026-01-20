"""Registry panel for viewing and managing skills."""

from __future__ import annotations

import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable

import structlog

from ui.dialogs.rename_dialog import RenameDialog

if TYPE_CHECKING:
    from services.registry_service import RegistryService

logger = structlog.get_logger(__name__)


class RegistryPanel(ttk.Frame):
    """Panel for displaying and managing registry skills.

    Shows a treeview of all skills with columns for
    Type, Name, Version, and Path. Supports filtering, visibility toggle,
    Quick View popup, and context menu actions.

    Attributes:
        service: Registry service for data operations
        tree: Treeview widget for skill display
    """

    def __init__(
        self,
        parent: tk.Misc,
        service: RegistryService,
        status_callback: Callable[[str], None],
    ) -> None:
        """Initialize registry panel.

        Args:
            parent: Parent widget (notebook)
            service: Registry service for operations
            status_callback: Function to update status bar
        """
        super().__init__(parent)
        self._service = service
        self._status_callback = status_callback
        self._all_items: list[tuple[str, str, str, str, bool]] = (
            []
        )  # Cache for filtering

        self._setup_ui()
        self._setup_context_menu()
        self._setup_bindings()
        self.refresh_list()

    def _setup_ui(self) -> None:
        """Setup panel layout and widgets."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Toolbar frame
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        refresh_btn = ttk.Button(
            toolbar,
            text="🔄 Refresh Knowledge Base",
            command=self._on_refresh_click,
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)

        # Filter UI
        filter_label = ttk.Label(toolbar, text="🔍")
        filter_label.pack(side=tk.LEFT, padx=(20, 5))

        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(toolbar, textvariable=self.filter_var, width=30)
        self.filter_entry.pack(side=tk.LEFT, padx=2)

        clear_btn = ttk.Button(
            toolbar,
            text="✕",
            width=3,
            command=self._clear_filter,
        )
        clear_btn.pack(side=tk.LEFT, padx=2)

        # Show Hidden Toggle
        self.show_hidden_var = tk.BooleanVar(value=True)
        show_hidden_chk = ttk.Checkbutton(
            toolbar,
            text="Show Hidden Skills",
            variable=self.show_hidden_var,
            command=self._apply_filter,
        )
        show_hidden_chk.pack(side=tk.LEFT, padx=(20, 5))

        # Treeview with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("type", "name", "version", "path")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended",  # Enable multi-selection
        )

        self.tree.column("type", width=80, minwidth=60)
        self.tree.column("name", width=200, minwidth=100)
        self.tree.column("version", width=80, minwidth=50, anchor=tk.CENTER)
        self.tree.column("path", width=400, minwidth=200)

        # Configure sortable headings
        for col in columns:
            self.tree.heading(
                col,
                text=col.capitalize(),
                anchor=tk.W if col != "version" else tk.CENTER,
                command=lambda c=col: self._sort_column(c, False),
            )

        # Configure tag styles for hidden items
        self.tree.tag_configure("hidden", foreground="gray")

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

    def _setup_context_menu(self) -> None:
        """Set up right-click context menu."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label="Quick View",
            command=self._show_quick_view,
        )
        self.context_menu.add_command(
            label="Rename Intelligently...",
            command=self._on_rename_click,
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Hide Selected",
            command=lambda: self._toggle_visibility(False),
        )
        self.context_menu.add_command(
            label="Show Selected",
            command=lambda: self._toggle_visibility(True),
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Show in Explorer",
            command=self._show_in_explorer,
        )
        self.context_menu.add_command(
            label="Open with Editor",
            command=self._open_with_editor,
        )

    def _setup_bindings(self) -> None:
        """Set up event bindings."""
        # Right-click context menu
        self.tree.bind("<Button-3>", self._show_context_menu)

        # Filter on key release
        self.filter_entry.bind("<KeyRelease>", lambda e: self._apply_filter())

        # Selection change
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)

    def _show_context_menu(self, event: tk.Event[tk.Misc]) -> None:
        """Show context menu at cursor position."""
        # Select item under cursor if not already selected
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def refresh_list(self) -> None:
        """Reload skill list from service."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load skills
        skills = self._service.list_all()

        # Cache for filtering
        self._all_items = []
        for skill in skills:
            version_str = f"{skill.major}.{skill.minor}"
            self._all_items.append(
                (
                    skill.type,
                    skill.name,
                    version_str,
                    str(skill.path),
                    skill.is_enabled,
                )
            )

        # Apply current filter
        self._apply_filter()

        count = len(skills)
        self._status_callback(f"Loaded {count} skills")
        logger.info("registry_list_refreshed", count=count)

    def _apply_filter(self) -> None:
        """Apply filter to treeview based on filter entry text."""
        filter_text = self.filter_var.get().lower()

        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Re-populate with filtered items
        show_hidden = self.show_hidden_var.get()
        for type_val, name, version, path, is_enabled in self._all_items:
            # Respect "Show Hidden" toggle
            if not is_enabled and not show_hidden:
                continue

            # Filter on name AND path
            if (
                filter_text
                and filter_text not in name.lower()
                and filter_text not in path.lower()
            ):
                continue

            tags = () if is_enabled else ("hidden",)
            self.tree.insert(
                "",
                tk.END,
                iid=name,
                values=(type_val, name, version, path),
                tags=tags,
            )

    def _clear_filter(self) -> None:
        """Clear the filter entry and refresh view."""
        self.filter_var.set("")
        self._apply_filter()
        self._status_callback("Filter cleared")

    def _sort_column(self, col: str, reverse: bool) -> None:
        """Sort treeview by a specific column.

        Args:
            col: Column identifier to sort by
            reverse: Sort order (True for descending)
        """
        # Fetch all items currently in the list
        data = [
            (self.tree.set(child, col), child) for child in self.tree.get_children("")
        ]

        # Sorting logic
        if col == "version":
            # Sort by version numbers (e.g., "1.10" > "1.2")
            def version_key(item: tuple[str, str]) -> list[int]:
                try:
                    return [int(x) for x in item[0].split(".")]
                except (ValueError, AttributeError):
                    return [0]

            data.sort(key=version_key, reverse=reverse)
        else:
            # Standard string sort
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)

        # Rearrange items in treeview
        for index, (_, child) in enumerate(data):
            self.tree.move(child, "", index)

        # Update heading command to toggle sort order
        self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))
        order = "descending" if reverse else "ascending"
        self._status_callback(f"Sorted by {col} ({order})")
        logger.debug("column_sorted", column=col, order=order)

    def _on_refresh_click(self) -> None:
        """Handle refresh button click."""
        self._status_callback("Refreshing knowledge base...")
        logger.info("refresh_button_clicked")

        # Scan default directories
        scan_dirs = ["core", "platform", "domain", "workflows"]
        result = self._service.refresh_registry(scan_dirs)

        self.refresh_list()

        self._status_callback(
            f"Refresh complete: {result.added} added, "
            f"{result.updated} updated, {result.removed} removed"
        )

    def _on_selection_change(self, event: tk.Event[tk.Misc]) -> None:
        """Handle treeview selection change.

        Args:
            event: Tkinter event object
        """
        selection = self.tree.selection()
        if selection:
            count = len(selection)
            if count == 1:
                logger.debug("skill_selected", name=selection[0])
            else:
                logger.debug("skills_selected", count=count)

    def _toggle_visibility(self, enabled: bool) -> None:
        """Toggle visibility for selected items.

        Args:
            enabled: True to show, False to hide
        """
        selection = self.tree.selection()
        if not selection:
            return

        names = list(selection)
        updated = self._service.set_skills_enabled(names, enabled)

        if updated > 0:
            action = "shown" if enabled else "hidden"
            self._status_callback(f"{updated} item(s) {action}")
            self.refresh_list()

    def _get_selected_file_path(self) -> str | None:
        """Get the file path of the first selected item."""
        selection = self.tree.selection()
        if not selection:
            return None

        name = selection[0]
        skill = self._service.get_skill(name)
        if not skill:
            return None

        return str(self._service.repo_root / skill.path)

    def _show_in_explorer(self) -> None:
        """Open file explorer at the selected file's location."""
        file_path = self._get_selected_file_path()
        if not file_path:
            messagebox.showinfo("Show in Explorer", "No item selected.")
            return

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", file_path], check=False)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path], check=False)
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)], check=False)
            logger.info("show_in_explorer", path=file_path)
        except Exception as e:
            logger.error("show_in_explorer_error", error=str(e))
            messagebox.showerror("Error", f"Could not open explorer: {e}")

    def _open_with_editor(self) -> None:
        """Open the selected file with the default application."""
        file_path = self._get_selected_file_path()
        if not file_path:
            messagebox.showinfo("Open with Editor", "No item selected.")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path], check=False)
            else:  # Linux
                subprocess.run(["xdg-open", file_path], check=False)
            logger.info("open_with_editor", path=file_path)
        except Exception as e:
            logger.error("open_with_editor_error", error=str(e))
            messagebox.showerror("Error", f"Could not open file: {e}")

    def _on_rename_click(self) -> None:
        """Handle resize/rename action."""
        selection = self.tree.selection()
        if not selection:
            return

        name = selection[0]
        skill = self._service.get_skill(name)
        if not skill:
            return

        dialog = RenameDialog(
            self,
            skill,
            naming_service=self._service.naming_service,
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                self._service.rename_skill(
                    current_name=name,
                    new_basename=dialog.result["basename"],
                    new_type=dialog.result["type"],
                    new_major=dialog.result["major"],
                    new_minor=dialog.result["minor"],
                )
                self._status_callback(f"Renamed '{name}' successfully.")
                self.refresh_list()
            except Exception as e:
                logger.error("rename_error", error=str(e))
                messagebox.showerror("Rename Failed", str(e))

    def _show_quick_view(self) -> None:
        """Show a Quick View popup for the selected skill."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Quick View", "No item selected.")
            return

        name = selection[0]
        skill = self._service.get_skill(name)

        if not skill:
            messagebox.showwarning("Quick View", f"Skill '{name}' not found.")
            return

        # Read file content
        file_path = self._service.repo_root / skill.path
        if not file_path.exists():
            messagebox.showwarning("Quick View", f"File not found: {file_path}")
            return

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Quick View", f"Error reading file: {e}")
            return

        # Parse markdown for display
        h1, summary, toc = self._parse_markdown_preview(content)

        # Create popup window
        popup = tk.Toplevel(self)
        popup.title(f"Quick View: {name}")
        popup.geometry("500x400")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()

        # Content frame with scrollbar
        frame = ttk.Frame(popup, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # H1 Title
        title_label = ttk.Label(
            frame, text=h1, font=("TkDefaultFont", 14, "bold"), wraplength=460
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # Summary
        if summary:
            summary_label = ttk.Label(frame, text=summary, wraplength=460)
            summary_label.pack(anchor=tk.W, pady=(0, 10))

        # TOC (H2 headings)
        if toc:
            toc_label = ttk.Label(
                frame, text="Contents:", font=("TkDefaultFont", 10, "bold")
            )
            toc_label.pack(anchor=tk.W, pady=(5, 2))
            for heading in toc:
                h2_label = ttk.Label(frame, text=f"  • {heading}")
                h2_label.pack(anchor=tk.W)

        # Close button
        close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=10)

        # Center popup on parent
        popup.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = (
            self.winfo_rooty()
            + (self.winfo_height() // 2)
            - (popup.winfo_height() // 2)
        )
        popup.geometry(f"+{x}+{y}")

    def _parse_markdown_preview(self, content: str) -> tuple[str, str, list[str]]:
        """Parse markdown content for Quick View display.

        Args:
            content: Raw markdown content

        Returns:
            Tuple of (h1_title, summary_paragraph, list_of_h2_headings)
        """
        lines = content.splitlines()
        h1 = ""
        summary = ""
        toc: list[str] = []
        in_summary = False

        for line in lines:
            stripped = line.strip()

            # Extract H1
            if stripped.startswith("# ") and not h1:
                h1 = stripped[2:].strip()
                in_summary = True
                continue

            # Extract first paragraph after H1 as summary
            if in_summary:
                if stripped.startswith("#"):
                    in_summary = False
                elif stripped:
                    if not summary:
                        summary = stripped
                    else:
                        # Stop at next paragraph break or heading
                        pass
                elif summary:
                    # Empty line after summary paragraph
                    in_summary = False

            # Collect H2 headings
            if stripped.startswith("## "):
                toc.append(stripped[3:].strip())

        return h1, summary, toc
