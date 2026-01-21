"""Tooltip widget for displaying hover hints."""

import tkinter as tk
from tkinter import ttk


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
