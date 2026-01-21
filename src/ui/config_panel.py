from __future__ import annotations

import tkinter as tk
import os
import platform
import subprocess
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Callable, cast

import structlog

from ui.dialogs.quick_view_dialog import QuickViewDialog
from models.agent_config import AgentConfig

if TYPE_CHECKING:
    from services.registry_service import RegistryService

logger = structlog.get_logger(__name__)


class ToolTip:
    """Tooltip helper class for displaying hover hints on widgets."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        """Initialize tooltip.

        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text to display
        """
        self.widget = widget
        self.text = text
        self.tooltip_window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event: tk.Event[tk.Misc]) -> None:
        """Show tooltip near the widget."""
        if self.tooltip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padding=(5, 2),
        )
        label.pack()

    def _hide(self, event: tk.Event[tk.Misc]) -> None:
        """Hide tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class ConfigPanel(ttk.Frame):
    """Panel for creating and editing agent configurations.

    Provides a dual-listbox interface to select skills from the registry
    and arrange them into a configuration.

    Attributes:
        registry_service: Service for accessing available skills
        available_list: Listbox showing registry skills
        selected_list: Listbox showing selected skills
    """

    def __init__(
        self,
        parent: ttk.Notebook,
        registry_service: RegistryService,
        status_callback: Callable[[str], None],
    ) -> None:
        """Initialize configuration panel.

        Args:
            parent: Parent widget (Notebook)
            registry_service: Service for registry operations
            status_callback: Callback to update status bar
        """
        super().__init__(parent)
        self._registry_service = registry_service
        self._set_status = status_callback
        self._current_config_path: Path | None = None
        self._all_skills: list[str] = []  # Cache for filtering

        self._setup_ui()
        self._setup_bindings()
        self._setup_context_menus()
        self._refresh_available_list()

    def _setup_ui(self) -> None:
        """Create and arrange UI elements."""
        # Main container with 4 columns
        self.columnconfigure(0, weight=1)  # Available
        self.columnconfigure(1, weight=0)  # Buttons
        self.columnconfigure(2, weight=1)  # Selected
        self.columnconfigure(3, weight=0)  # Order Buttons
        self.rowconfigure(2, weight=1)  # Listboxes expand vertically

        # --- Header Row (row 0) ---
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        kb_label = ttk.Label(header_frame, text="Knowledge Base")
        kb_label.pack(side=tk.LEFT, padx=5)
        ToolTip(kb_label, "All available skills, guides, and prompts in the registry.")

        prof_label = ttk.Label(header_frame, text="Profession Skills")
        prof_label.pack(side=tk.RIGHT, padx=40)
        ToolTip(prof_label, "Skills selected for this agent's profession/role.")

        # --- Filter Row (row 1) ---
        filter_frame = ttk.Frame(self)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))

        filter_label = ttk.Label(filter_frame, text="🔍")
        filter_label.pack(side=tk.LEFT, padx=(0, 5))

        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ToolTip(self.filter_entry, "Type to filter the Knowledge Base list.")

        clear_btn = ttk.Button(
            filter_frame,
            text="✕",
            width=3,
            command=self._clear_filter,
        )
        clear_btn.pack(side=tk.LEFT, padx=(2, 0))
        ToolTip(clear_btn, "Clear filter")

        # --- Available List (Left, row 2) ---
        available_frame = ttk.Frame(self)
        available_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        self.available_list = tk.Listbox(available_frame, selectmode=tk.EXTENDED)
        self.available_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ToolTip(self.available_list, "Double-click to add. Right-click for Quick View.")

        av_scroll = ttk.Scrollbar(
            available_frame, orient="vertical", command=self.available_list.yview
        )
        av_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.available_list.config(yscrollcommand=av_scroll.set)

        # --- Selection Buttons (Center, row 2) ---
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=1, padx=5, pady=5)

        add_btn = ttk.Button(btn_frame, text="Add >>", command=self._add_selected)
        add_btn.pack(pady=5)
        ToolTip(add_btn, "Add selected items to the profession.")

        remove_btn = ttk.Button(
            btn_frame, text="<< Remove", command=self._remove_selected
        )
        remove_btn.pack(pady=5)
        ToolTip(remove_btn, "Remove selected items from the profession.")

        # --- Selected List (Right, row 2) ---
        selected_frame = ttk.Frame(self)
        selected_frame.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)

        self.selected_list = tk.Listbox(selected_frame, selectmode=tk.EXTENDED)
        self.selected_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ToolTip(
            self.selected_list, "Double-click to remove. Right-click for Quick View."
        )

        sel_scroll = ttk.Scrollbar(
            selected_frame, orient="vertical", command=self.selected_list.yview
        )
        sel_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.selected_list.config(yscrollcommand=sel_scroll.set)

        # --- Ordering Buttons (Far Right, row 2) ---
        order_frame = ttk.Frame(self)
        order_frame.grid(row=2, column=3, padx=5, pady=5)

        up_btn = ttk.Button(order_frame, text="Move Up", command=self._move_up)
        up_btn.pack(pady=5)
        ToolTip(up_btn, "Move selected skill(s) higher in priority.")

        down_btn = ttk.Button(order_frame, text="Move Down", command=self._move_down)
        down_btn.pack(pady=5)
        ToolTip(down_btn, "Move selected skill(s) lower in priority.")

        # --- Action Buttons (Bottom, row 3) ---
        action_frame = ttk.Frame(self)
        action_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=10)

        new_btn = ttk.Button(
            action_frame, text="New Profession", command=self._new_config
        )
        new_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(new_btn, "Start a fresh profession configuration.")

        load_btn = ttk.Button(
            action_frame, text="Load Profession...", command=self._load_config_dialog
        )
        load_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(load_btn, "Load an existing agent.config.json file.")

        save_btn = ttk.Button(
            action_frame, text="Save Profession...", command=self._save_config_dialog
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(save_btn, "Save the current profession to agent.config.json.")

    def _setup_bindings(self) -> None:
        """Set up event bindings for interactions."""
        # Double-click to move items
        self.available_list.bind("<Double-Button-1>", lambda e: self._add_selected())
        self.selected_list.bind("<Double-Button-1>", lambda e: self._remove_selected())

        # Filter on key release
        self.filter_entry.bind("<KeyRelease>", lambda e: self._filter_available_list())

    def _setup_context_menus(self) -> None:
        """Set up right-click context menus for Quick View."""
        # Context menu for available list
        self.available_menu = tk.Menu(self, tearoff=0)
        self.available_menu.add_command(
            label="Quick View",
            command=lambda: self._show_quick_view(self.available_list),
        )
        self.available_menu.add_command(
            label="Open with Notepad",
            command=lambda: self._open_with_notepad(self.available_list),
        )
        self.available_list.bind("<Button-3>", self._show_available_menu)

        # Context menu for selected list
        self.selected_menu = tk.Menu(self, tearoff=0)
        self.selected_menu.add_command(
            label="Quick View",
            command=lambda: self._show_quick_view(self.selected_list),
        )
        self.selected_menu.add_command(
            label="Open with Notepad",
            command=lambda: self._open_with_notepad(self.selected_list),
        )
        self.selected_list.bind("<Button-3>", self._show_selected_menu)

    def _show_available_menu(self, event: tk.Event[tk.Misc]) -> None:
        """Show context menu for available list."""
        # Select item under cursor
        index = self.available_list.nearest(event.y)  # type: ignore[no-untyped-call]
        self.available_list.selection_clear(0, tk.END)
        self.available_list.selection_set(index)
        self.available_menu.tk_popup(event.x_root, event.y_root)

    def _show_selected_menu(self, event: tk.Event[tk.Misc]) -> None:
        """Show context menu for selected list."""
        index = self.selected_list.nearest(event.y)  # type: ignore[no-untyped-call]
        self.selected_list.selection_clear(0, tk.END)
        self.selected_list.selection_set(index)
        self.selected_menu.tk_popup(event.x_root, event.y_root)

    def refresh(self) -> None:
        """Refresh the available skills list."""
        self._refresh_available_list()

    def _refresh_available_list(self) -> None:
        """Populate available list from registry (enabled items only)."""
        self.available_list.delete(0, tk.END)
        skills = self._registry_service.list_enabled()
        self._all_skills = [skill.name for skill in skills]
        for name in self._all_skills:
            self.available_list.insert(tk.END, name)

    def _filter_available_list(self) -> None:
        """Filter available list based on filter entry text."""
        filter_text = self.filter_var.get().lower()
        self.available_list.delete(0, tk.END)

        for name in self._all_skills:
            if filter_text in name.lower():
                self.available_list.insert(tk.END, name)

    def _clear_filter(self) -> None:
        """Clear the filter entry and refresh the list."""
        self.filter_var.set("")
        self._filter_available_list()

    def _add_selected(self) -> None:
        """Move selected items from available to selected list."""
        indices = cast(
            tuple[int, ...], self.available_list.curselection()  # type: ignore[no-untyped-call]
        )
        if not indices:
            return

        added_count = 0
        for i in indices:
            name = self.available_list.get(i)
            # Check if already in selected list to prevent duplicates
            if name not in self.selected_list.get(0, tk.END):
                self.selected_list.insert(tk.END, name)
                added_count += 1

        if added_count > 0:
            self._set_status(f"Added {added_count} skill(s)")

    def _remove_selected(self) -> None:
        """Remove selected items from the selected list."""
        indices = cast(
            tuple[int, ...], self.selected_list.curselection()  # type: ignore[no-untyped-call]
        )
        if not indices:
            return

        # Delete in reverse order to maintain indices
        for i in reversed(indices):
            self.selected_list.delete(i)

        self._set_status(f"Removed {len(indices)} skill(s)")

    def _move_up(self) -> None:
        """Move selected item up in the list."""
        indices = cast(
            tuple[int, ...], self.selected_list.curselection()  # type: ignore[no-untyped-call]
        )
        if not indices:
            return

        for i in indices:
            if i == 0:
                continue
            text = self.selected_list.get(i)
            self.selected_list.delete(i)
            self.selected_list.insert(i - 1, text)
            self.selected_list.selection_set(i - 1)

    def _move_down(self) -> None:
        """Move selected item down in the list."""
        indices = cast(
            tuple[int, ...], self.selected_list.curselection()  # type: ignore[no-untyped-call]
        )
        if not indices:
            return

        # Process in reverse to avoid index shifting issues
        for i in reversed(indices):
            if i == self.selected_list.size() - 1:
                continue
            text = self.selected_list.get(i)
            self.selected_list.delete(i)
            self.selected_list.insert(i + 1, text)
            self.selected_list.selection_set(i + 1)

    def _new_config(self) -> None:
        """Clear the selected list to start fresh."""
        if self.selected_list.size() > 0:
            if not messagebox.askyesno("Confirm", "Clear current profession?"):
                return
        self.selected_list.delete(0, tk.END)
        self._current_config_path = None
        self._set_status("Started new profession")

    def _load_config_dialog(self) -> None:
        """Open file dialog to load a profession."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Profession",
        )
        if path:
            try:
                self.load_config(Path(path))
            except Exception as e:
                logger.error("load_config_error", error=str(e))
                messagebox.showerror("Error", f"Failed to load profession: {e}")

    def load_config(self, path: Path) -> None:
        """Load configuration from file.

        Args:
            path: Path to agent.config.json
        """
        config = AgentConfig.from_file(path)
        self.selected_list.delete(0, tk.END)
        for name in config.ingredients:
            self.selected_list.insert(tk.END, name)

        self._current_config_path = path
        self._set_status(f"Loaded profession from {path.name}")

    def _save_config_dialog(self) -> None:
        """Open file dialog to save profession."""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="agent.config.json",
            title="Save Profession",
        )
        if path:
            try:
                self.save_config(Path(path))
            except Exception as e:
                logger.error("save_config_error", error=str(e))
                messagebox.showerror("Error", f"Failed to save profession: {e}")

    def save_config(self, path: Path) -> None:
        """Save current configuration to file.

        Args:
            path: Path to save agent.config.json
        """
        skills = list(self.selected_list.get(0, tk.END))
        config = AgentConfig(ingredients=skills)
        config.to_file(path)
        self._current_config_path = path
        self._set_status(f"Saved profession to {path.name}")

    def _show_quick_view(self, listbox: tk.Listbox) -> None:
        """Show a Quick View popup for the selected skill.

        Args:
            listbox: The listbox from which to get the selected item
        """
        indices = cast(
            tuple[int, ...], listbox.curselection()  # type: ignore[no-untyped-call]
        )
        if not indices:
            messagebox.showinfo("Quick View", "No item selected.")
            return

        name = listbox.get(indices[0])

        # Callback to refresh list if H1 is updated
        def on_update() -> None:
            self._set_status(f"Updated title for '{name}'")
            self.refresh()

        QuickViewDialog(self, self._registry_service, name, on_update=on_update)

    def _open_with_editor(self, listbox: tk.Listbox) -> None:
        """Open the selected file with the default application.

        Args:
             listbox: The listbox from which to get the selected item
        """
        indices = cast(
            tuple[int, ...], listbox.curselection()  # type: ignore[no-untyped-call]
        )
        if not indices:
            messagebox.showinfo("Open with Editor", "No item selected.")
            return

        name = listbox.get(indices[0])
        skill = self._registry_service.get_skill(name)

        if not skill:
            messagebox.showwarning("Open with Editor", f"Skill '{name}' not found.")
            return

        file_path = self._registry_service.repo_root / skill.path
        if not file_path.exists():
            messagebox.showwarning("Open with Editor", f"File not found: {file_path}")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path], check=False)
            else:  # Linux
                subprocess.run(["xdg-open", file_path], check=False)
            logger.info("open_with_editor", path=str(file_path))
        except Exception as e:
            logger.error("open_with_editor_error", error=str(e))
            messagebox.showerror("Error", f"Could not open file: {e}")

    def _open_with_notepad(self, listbox: tk.Listbox) -> None:
        """Open the selected file with Notepad.

        Args:
             listbox: The listbox from which to get the selected item
        """
        indices = cast(
            tuple[int, ...], listbox.curselection()  # type: ignore[no-untyped-call]
        )
        if not indices:
            messagebox.showinfo("Open with Notepad", "No item selected.")
            return

        name = listbox.get(indices[0])
        skill = self._registry_service.get_skill(name)

        if not skill:
            messagebox.showwarning("Open with Notepad", f"Skill '{name}' not found.")
            return

        file_path = self._registry_service.repo_root / skill.path
        if not file_path.exists():
            messagebox.showwarning("Open with Notepad", f"File not found: {file_path}")
            return

        try:
            if platform.system() == "Windows":
                subprocess.Popen(["notepad.exe", str(file_path)])
            else:
                # Fallback for non-Windows
                self._open_with_editor(listbox)
            logger.info("open_with_notepad", path=str(file_path))
        except Exception as e:
            logger.error("open_with_notepad_error", error=str(e))
            messagebox.showerror("Error", f"Could not open editor: {e}")
