"""Main application window for AI Prompt Manager."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from services.agent_builder import AgentBuilder
    from services.registry_service import RegistryService

from ui.build_panel import BuildPanel
from ui.config_panel import ConfigPanel, ToolTip
from ui.registry_panel import RegistryPanel

logger = structlog.get_logger(__name__)


class MainWindow(tk.Tk):
    """Main application window with tabbed interface.

    Contains Registry, Build, and Config panels in a notebook layout.
    Provides menu bar and status bar.

    Attributes:
        registry_service: Service for registry operations
        agent_builder: Service for building agent folders
        notebook: Tab container for panels
        registry_panel: Panel for viewing/managing registry
        build_panel: Panel for building agent folders
        config_panel: Panel for managing agent configuration
        status_bar: Label for status messages
    """

    def __init__(
        self,
        registry_service: RegistryService,
        agent_builder: AgentBuilder,
        startup_warnings: list[str] | None = None,
    ) -> None:
        """Initialize main window.

        Args:
            registry_service: Service for registry operations
            agent_builder: Service for building agent folders
            startup_warnings: Optional list of warnings to display on startup
        """
        super().__init__()
        self._registry_service = registry_service
        self._agent_builder = agent_builder
        self._startup_warnings = startup_warnings or []

        self._setup_window()
        self._setup_menu()
        self._setup_status_bar()
        self._setup_notebook()

        # Show startup warnings in status bar
        if self._startup_warnings:
            self._set_status(f"⚠️ {self._startup_warnings[0]}")

        logger.info("main_window_initialized")

    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.title("AI Prompt Manager")
        self.geometry("900x600")
        self.minsize(700, 400)

        # Configure grid weights for resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _setup_menu(self) -> None:
        """Create menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _setup_notebook(self) -> None:
        """Create tabbed interface with panels."""
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Registry panel (Tab 1) - Knowledge Base
        self.registry_panel = RegistryPanel(
            self.notebook,
            self._registry_service,
            self._set_status,
        )
        self.notebook.add(self.registry_panel, text="Knowledge Base")

        # Config panel (Tab 2) - Profession Designer
        self.config_panel = ConfigPanel(
            self.notebook,
            registry_service=self._registry_service,
            status_callback=self._set_status,
        )
        self.notebook.add(self.config_panel, text="Profession Designer")

        # Build panel (Tab 3) - Agent Onboarding
        self.build_panel = BuildPanel(
            self.notebook,
            agent_builder=self._agent_builder,
            status_callback=self._set_status,
        )
        self.notebook.add(self.build_panel, text="Agent Onboarding")

        # Add tooltips to tabs
        self._setup_tab_tooltips()

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event: tk.Event[tk.Misc]) -> None:
        """Handle tab change event."""
        # Get selected tab index
        try:
            current_tab = self.notebook.index(self.notebook.select())  # type: ignore[no-untyped-call]

            # If "Profession Designer" tab (index 1) is selected, refresh common lists
            if current_tab == 1:
                self.config_panel.refresh()
                logger.debug("refreshed_config_panel_on_tab_switch")
        except tk.TclError:
            pass

    def _setup_status_bar(self) -> None:
        """Create status bar at bottom of window."""
        self.status_bar = ttk.Label(
            self,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2),
        )
        self.status_bar.grid(row=1, column=0, sticky="ew")

    def _set_status(self, message: str) -> None:
        """Update status bar message.

        Args:
            message: Status message to display
        """
        self.status_bar.config(text=message)
        logger.debug("status_updated", message=message)

    def _show_about(self) -> None:
        """Show about dialog."""
        from tkinter import messagebox

        messagebox.showinfo(
            "About",
            "AI Prompt Manager\n\n"
            "Manage AI prompt skills and build agent configurations.\n\n"
            "Version 0.1.0",
        )

    def run(self) -> None:
        """Start the application main loop."""
        logger.info("starting_mainloop")
        self.mainloop()

    def _setup_tab_tooltips(self) -> None:
        """Add tooltips to notebook tabs explaining the Teaching Paradigm."""
        # Tab tooltips are applied to the notebook itself via motion events
        self._tab_tooltips = {
            0: "Knowledge Base: Browse all available skills, guides, and prompts.",
            1: "Profession Designer: Select and arrange skills for an agent's role.",
            2: "Agent Onboarding: Deploy the profession to an agent's rules folder.",
        }
        self._current_tab_tooltip: tk.Toplevel | None = None
        self.notebook.bind("<Motion>", self._on_tab_motion)
        self.notebook.bind("<Leave>", self._hide_tab_tooltip)

    def _on_tab_motion(self, event: tk.Event[tk.Misc]) -> None:
        """Show tooltip when hovering over a tab."""
        try:
            tab_index = self.notebook.index(f"@{event.x},{event.y}")  # type: ignore[no-untyped-call]
        except tk.TclError:
            self._hide_tab_tooltip(event)
            return

        tooltip_text = self._tab_tooltips.get(tab_index)
        if not tooltip_text:
            self._hide_tab_tooltip(event)
            return

        # Show or update tooltip
        if self._current_tab_tooltip:
            # Update position
            x = event.x_root + 10
            y = event.y_root + 20
            self._current_tab_tooltip.wm_geometry(f"+{x}+{y}")
            label = self._current_tab_tooltip.winfo_children()[0]
            if isinstance(label, ttk.Label):
                label.configure(text=tooltip_text)
        else:
            # Create tooltip
            x = event.x_root + 10
            y = event.y_root + 20
            self._current_tab_tooltip = tk.Toplevel(self)
            self._current_tab_tooltip.wm_overrideredirect(True)
            self._current_tab_tooltip.wm_geometry(f"+{x}+{y}")
            label = ttk.Label(
                self._current_tab_tooltip,
                text=tooltip_text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                padding=(5, 2),
            )
            label.pack()

    def _hide_tab_tooltip(self, event: tk.Event[tk.Misc] | None) -> None:
        """Hide the tab tooltip."""
        if self._current_tab_tooltip:
            self._current_tab_tooltip.destroy()
            self._current_tab_tooltip = None
