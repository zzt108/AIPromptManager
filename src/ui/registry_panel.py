"""Registry panel for viewing and managing skills."""

from __future__ import annotations

import os
import platform
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable

import structlog

from ui.dialogs.rename_dialog import RenameDialog
from ui.dialogs.move_dialog import MoveDialog
from models.skill_status import SkillStatus

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
        self._all_items: list[
            tuple[str, str, str, str, bool, SkillStatus, str, float]
        ] = []  # Cache for filtering (..., modified_str, modified_ts)

        self._setup_ui()
        self._setup_context_menu()
        self._setup_bindings()

        # Sort state (default by name ascending)
        self._sort_col = "name"
        self._sort_reverse = False

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
            text="Show Hidden",
            variable=self.show_hidden_var,
            command=self._apply_filter_and_sort,
        )
        show_hidden_chk.pack(side=tk.LEFT, padx=(20, 5))

        # Show Archived Toggle
        self.show_archived_var = tk.BooleanVar(value=False)
        show_archived_chk = ttk.Checkbutton(
            toolbar,
            text="Show Archived",
            variable=self.show_archived_var,
            command=self._apply_filter_and_sort,
        )
        show_archived_chk.pack(side=tk.LEFT, padx=5)

        # Treeview with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ("status", "type", "name", "version", "path", "modified")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended",  # Enable multi-selection
        )

        self.tree.column("status", width=50, minwidth=40, anchor=tk.CENTER)
        self.tree.column("type", width=80, minwidth=60)
        self.tree.column("name", width=200, minwidth=100)
        self.tree.column("version", width=60, minwidth=50, anchor=tk.CENTER)
        self.tree.column("path", width=300, minwidth=200)
        self.tree.column("modified", width=140, minwidth=120)

        # Configure sortable headings
        self.tree.heading(
            "status",
            text="St",
            command=lambda: self._sort_column("status", False),
        )
        for col in ("type", "name", "version", "path", "modified"):
            self.tree.heading(
                col,
                text=col.capitalize() if col != "modified" else "Last Modified",
                anchor=tk.W if col not in ("version",) else tk.CENTER,
                command=lambda c=col: self._sort_column(c, False),
            )

        # Configure tag styles
        self.tree.tag_configure("hidden", foreground="gray")
        self.tree.tag_configure("status_valid", foreground="black")
        self.tree.tag_configure("status_unrecognized", foreground="#e67e22")  # Orange
        self.tree.tag_configure("status_parse_error", foreground="#c0392b")  # Red
        self.tree.tag_configure("status_archived", foreground="#7f8c8d")  # Gray/Slate

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
        self.context_menu.add_command(
            label="Move to Folder...",
            command=self._on_move_click,
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Archive Skills...",
            command=self._on_archive_click,
        )
        self.context_menu.add_command(
            label="Restore Skills...",
            command=self._on_restore_click,
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
        self.context_menu.add_command(
            label="Open with Notepad",
            command=self._open_with_notepad,
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

            # Format modified date
            modified_str = ""
            if skill.modified_at > 0:
                dt = datetime.fromtimestamp(skill.modified_at)
                modified_str = dt.strftime("%Y-%m-%d %H:%M")

            self._all_items.append(
                (
                    skill.type,
                    skill.name,
                    version_str,
                    str(skill.path),
                    skill.is_enabled,
                    skill.status,
                    modified_str,
                    skill.modified_at,
                )
            )

        # Apply current filter
        self._apply_filter()

        # Re-apply current sort
        self._sort_column(self._sort_col, self._sort_reverse)

        count = len(skills)
        self._status_callback(f"Loaded {count} skills")
        logger.info("registry_list_refreshed", count=count)

    def _apply_filter_and_sort(self) -> None:
        """Apply filter and re-apply current sort order.

        Used as command for checkboxes to ensure consistent display.
        """
        self._apply_filter()
        self._sort_column(self._sort_col, self._sort_reverse)

    def _apply_filter(self) -> None:
        """Apply filter to treeview based on filter entry text."""
        filter_text = self.filter_var.get().lower()

        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Re-populate with filtered items
        show_hidden = self.show_hidden_var.get()
        for (
            type_val,
            name,
            version,
            path,
            is_enabled,
            status,
            modified_str,
            modified_ts,
        ) in self._all_items:
            # Respect "Show Hidden" toggle
            if not is_enabled and not show_hidden:
                continue

            # Respect "Show Archived" toggle
            if status == SkillStatus.ARCHIVED and not self.show_archived_var.get():
                continue

            # Filter on name, path, OR modified date
            search_content = f"{name} {path} {modified_str}".lower()
            if filter_text and filter_text not in search_content:
                continue

            # Determine tags
            tags = []
            if not is_enabled:
                tags.append("hidden")

            # Status tag for coloring (use .value to get string)
            tags.append(f"status_{status.value}")

            # Determine icon
            icon = "✓"
            if status == SkillStatus.UNRECOGNIZED:
                icon = "⚠️"
            elif status == SkillStatus.PARSE_ERROR:
                icon = "❌"
            elif status == SkillStatus.ARCHIVED:
                icon = "📦"

            self.tree.insert(
                "",
                tk.END,
                iid=name,
                values=(icon, type_val, name, version, path, modified_str),
                tags=tuple(tags),
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
        elif col == "modified":
            # Sort by timestamp via looking up in _all_items
            # Make a map for faster lookup {name: timestamp}
            ts_map = {item[1]: item[7] for item in self._all_items}

            def ts_key(item: tuple[str, str]) -> float:
                # item[1] is the iid (which is name in our case)
                return ts_map.get(item[1], 0.0)

            data.sort(key=ts_key, reverse=reverse)
        else:
            # Standard string sort
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)

        # Rearrange items in treeview
        for index, (_, child) in enumerate(data):
            self.tree.move(child, "", index)

        # Update sorting state cache
        self._sort_col = col
        self._sort_reverse = reverse

        # Update headers with sort indicators
        for c in ("type", "name", "version", "path", "modified"):
            # Determine base text
            base_text = c.capitalize()
            if c == "modified":
                base_text = "Last Modified"

            # Add arrow if this is the sorted column
            if c == col:
                arrow = "↓" if reverse else "↑"
                header_text = f"{base_text} {arrow}"
            else:
                header_text = base_text

            # Update heading
            self.tree.heading(
                c,
                text=header_text,
                command=lambda cls=c: self._sort_column(
                    cls, not reverse if cls == col else False
                ),
            )

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

    def _open_with_notepad(self) -> None:
        """Open the selected file with Notepad."""
        file_path = self._get_selected_file_path()
        if not file_path:
            messagebox.showinfo("Open with Notepad", "No item selected.")
            return

        try:
            if platform.system() == "Windows":
                subprocess.Popen(["notepad.exe", file_path])
            else:
                # Fallback for non-Windows (mostly for dev/testing)
                self._open_with_editor()
            logger.info("open_with_notepad", path=file_path)
        except Exception as e:
            logger.error("open_with_notepad_error", error=str(e))
            messagebox.showerror("Error", f"Could not open Notepad: {e}")

    def _on_rename_click(self) -> None:
        """Handle resize/rename action."""
        selection = self.tree.selection()
        if not selection:
            return

        name = selection[0]
        skill = self._service.get_skill(name)
        if not skill:
            return

        suggestions = self._service.generate_rename_suggestions(skill)
        dialog = RenameDialog(
            self,
            skill,
            naming_service=self._service.naming_service,
            suggestions=suggestions,
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

                # Restore selection to the renamed item
                if self._service.naming_service:
                    fname = self._service.naming_service.make_versioned(
                        basename=dialog.result["basename"],
                        major=dialog.result["major"],
                        minor=dialog.result["minor"],
                        type_str=dialog.result["type"],
                    )
                    # Skill name is valid filename stem (without extension)
                    new_name = os.path.splitext(fname)[0]

                    if self.tree.exists(new_name):
                        self.tree.selection_set(new_name)
                        self.tree.focus(new_name)
                        self.tree.see(new_name)

            except Exception as e:
                logger.error("rename_error", error=str(e))
                messagebox.showerror("Rename Failed", str(e))

    def _on_move_click(self) -> None:
        """Handle move action."""
        selection = self.tree.selection()
        if not selection:
            return

        skill_names = list(selection)

        # Determine initial directory from first selected skill
        initial_dir = None
        if skill_names:
            first_skill = self._service.get_skill(skill_names[0])
            if first_skill:
                initial_dir = (self._service.repo_root / first_skill.path).parent

        dialog = MoveDialog(
            self,
            repo_root=self._service.repo_root,
            initial_dir=initial_dir,
            count=len(skill_names),
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                moved = self._service.move_skills(skill_names, dialog.result)
                if moved > 0:
                    self._status_callback(f"Moved {moved} skills to {dialog.result}.")
                    self.refresh_list()
                else:
                    messagebox.showwarning("Move", "No skills were moved.")
            except Exception as e:
                logger.error("move_error", error=str(e))
                messagebox.showerror("Move Failed", str(e))

    def _on_archive_click(self) -> None:
        """Handle archive action."""
        selection = self.tree.selection()
        if not selection:
            return

        # Confirm action
        count = len(selection)
        msg = f"Are you sure you want to archive {count} skill(s)?\nThey will be moved to the .archive directory."
        if not messagebox.askyesno("Confirm Archive", msg):
            return

        try:
            archived = self._service.archive_skills(list(selection))
            if archived > 0:
                self._status_callback(f"Archived {archived} skills.")
                self.refresh_list()
            else:
                messagebox.showwarning("Archive", "No skills were archived.")
        except Exception as e:
            logger.error("archive_error", error=str(e))
            messagebox.showerror("Archive Failed", str(e))

    def _on_restore_click(self) -> None:
        """Handle restore action."""
        selection = self.tree.selection()
        if not selection:
            return

        # Confirm action
        count = len(selection)
        msg = f"Are you sure you want to restore {count} skill(s)?\nThey will be moved back to their original locations."
        if not messagebox.askyesno("Confirm Restore", msg):
            return

        try:
            restored = self._service.restore_skills(list(selection))
            if restored > 0:
                self._status_callback(f"Restored {restored} skills.")
                self.refresh_list()
            else:
                messagebox.showwarning("Restore", "No skills were restored.")
        except Exception as e:
            logger.error("restore_error", error=str(e))
            messagebox.showerror("Restore Failed", str(e))

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
        popup.geometry("600x500")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()

        # Content frame with scrollbar
        container = ttk.Frame(popup)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # H1 Edit Frame
        h1_frame = ttk.Frame(container)
        h1_frame.pack(fill=tk.X, pady=(0, 10))

        h1_var = tk.StringVar(value=h1)
        h1_entry = ttk.Entry(
            h1_frame, textvariable=h1_var, font=("TkDefaultFont", 12, "bold")
        )
        h1_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def save_h1() -> None:
            new_h1 = h1_var.get().strip()
            if not new_h1:
                messagebox.showwarning("Save H1", "Title cannot be empty.")
                return

            if self._service.update_skill_h1(name, new_h1):
                self._status_callback(f"Updated title for '{name}'")
                self.refresh_list()
                popup.destroy()
                # Re-open to show updated content? Or just close?
                # Let's just close for now as it's a modal action
            else:
                messagebox.showerror("Save H1", "Failed to update title.")

        save_btn = ttk.Button(h1_frame, text="💾 Save", command=save_h1, width=8)
        save_btn.pack(side=tk.LEFT)

        # Summary
        if summary:
            summary_label = ttk.Label(container, text=summary, wraplength=550)
            summary_label.pack(anchor=tk.W, pady=(0, 10))

        # TOC (H2 headings)
        if toc:
            toc_label = ttk.Label(
                container, text="Contents:", font=("TkDefaultFont", 10, "bold")
            )
            toc_label.pack(anchor=tk.W, pady=(5, 2))

            # Scrollable frame for TOC if it's long?
            # For now just pack them
            for heading in toc:
                h2_label = ttk.Label(container, text=f"  • {heading}")
                h2_label.pack(anchor=tk.W)

        # Spacer to push buttons to bottom
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

        ttk.Button(btn_frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT)

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
