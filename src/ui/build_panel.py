"""Build panel for creating agent configurations."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk
from typing import TYPE_CHECKING, Callable

import structlog

if TYPE_CHECKING:
    from services.agent_builder import AgentBuilder

logger = structlog.get_logger(__name__)


class BuildPanel(ttk.Frame):
    """Panel for building agent folder configurations.

    Allows user to select an agent.config.json file and output
    directory, then runs the build process with visual feedback.
    """

    def __init__(
        self,
        parent: tk.Widget,
        agent_builder: AgentBuilder | None = None,
        status_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize build panel.

        Args:
            parent: Parent widget (notebook)
            agent_builder: AgentBuilder service for building
            status_callback: Callback to update status bar
        """
        super().__init__(parent)
        self._agent_builder = agent_builder
        self._status_callback = status_callback or (lambda _: None)

        self._config_path = tk.StringVar()
        self._output_path = tk.StringVar()

        self._setup_ui()

    def set_agent_builder(self, builder: AgentBuilder) -> None:
        """Set the agent builder service (for late binding).

        Args:
            builder: AgentBuilder instance
        """
        self._agent_builder = builder

    def _setup_ui(self) -> None:
        """Setup panel layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)  # Log area expands

        # --- Profession Definition (Config File) ---
        config_frame = ttk.LabelFrame(self, text="Profession Definition", padding=10)
        config_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        config_frame.columnconfigure(0, weight=1)

        config_entry = ttk.Entry(config_frame, textvariable=self._config_path, width=60)
        config_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        config_browse = ttk.Button(
            config_frame, text="Browse...", command=self._browse_config
        )
        config_browse.grid(row=0, column=1)

        # --- Agent Rules Folder (Output Directory) ---
        output_frame = ttk.LabelFrame(
            self, text="Agent Rules Folder (e.g. .agent/rules)", padding=10
        )
        output_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        output_frame.columnconfigure(0, weight=1)

        output_entry = ttk.Entry(output_frame, textvariable=self._output_path, width=60)
        output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        output_help = ttk.Label(
            output_frame,
            text="Files will be generated here. Usually '.agent/rules' in your project.",
            font=("Segoe UI", 8),
            foreground="#666666",
        )
        output_help.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        output_browse = ttk.Button(
            output_frame, text="Browse...", command=self._browse_output
        )
        output_browse.grid(row=0, column=1)

        # --- Log View ---
        log_frame = ttk.LabelFrame(self, text="Build Log", padding=10)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self._log_view = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED,
            font=("Consolas", 10),
        )
        self._log_view.grid(row=0, column=0, sticky="nsew")

        # --- Build Button ---
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        button_frame.columnconfigure(0, weight=1)

        self._build_button = ttk.Button(
            button_frame, text="🚀 Onboard Agent", command=self._on_build
        )
        self._build_button.grid(row=0, column=1, sticky="e")

        logger.debug("build_panel_initialized")

    def _browse_config(self) -> None:
        """Open file dialog to select agent.config.json."""
        filename = filedialog.askopenfilename(
            title="Select agent.config.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if filename:
            self._config_path.set(filename)
            self._log(f"Config selected: {filename}")

    def _browse_output(self) -> None:
        """Open directory dialog to select output folder."""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self._output_path.set(dirname)
            self._log(f"Output directory: {dirname}")

    def _log(self, message: str) -> None:
        """Append a message to the log view.

        Args:
            message: Text to append
        """
        self._log_view.configure(state=tk.NORMAL)
        self._log_view.insert(tk.END, message + "\n")
        self._log_view.see(tk.END)
        self._log_view.configure(state=tk.DISABLED)

    def _on_build(self) -> None:
        """Handle build button click."""
        from models.service_results import BuildResult
        from models.sync_types import SyncAction, SyncStatus
        from ui.dialogs.sync_dialogs import LocalChangesDialog, UpdateAvailableDialog

        config_str = self._config_path.get().strip()
        output_str = self._output_path.get().strip()

        # Validation
        if not config_str:
            self._log("❌ Error: Please select a config file.")
            self._status_callback("Error: No config file selected")
            return

        if not output_str:
            self._log("❌ Error: Please select an output directory.")
            self._status_callback("Error: No output directory selected")
            return

        config_path = Path(config_str)
        output_path = Path(output_str)

        if not config_path.exists():
            self._log(f"❌ Error: Config file not found: {config_path}")
            self._status_callback("Error: Config file not found")
            return

        if self._agent_builder is None:
            self._log("❌ Error: Agent builder not configured.")
            self._status_callback("Error: Internal configuration error")
            return

        # Execute build
        self._log("=" * 50)
        self._log(f"🚀 Starting build...")
        self._log(f"   Config: {config_path}")
        self._log(f"   Output: {output_path}")
        self._status_callback("Building...")

        # Disable button during build
        self._build_button.config(state=tk.DISABLED)
        self.update_idletasks()

        try:
            # 1. Get Tasks (Dry Run)
            tasks = self._agent_builder.get_sync_tasks(config_path, output_path)

            result = BuildResult()

            # Check warnings first
            # Re-load config just for version checks (small overhead)
            from models.agent_config import AgentConfig

            config_obj = AgentConfig.from_file(config_path)
            version_updates = self._agent_builder.check_newer_versions(config_obj)
            for update in version_updates:
                result.warnings.append(str(update))

            # 2. Process Tasks
            for task in tasks:
                action = SyncAction.SKIP

                if task.status == SyncStatus.MISSING_SOURCE:
                    msg = f"❌ Missing source: {task.ingredient.name} ({task.source_path})"
                    self._log(msg)
                    result.warnings.append(msg)
                    continue

                elif task.status == SyncStatus.NOT_DEPLOYED:
                    action = SyncAction.COPY

                elif task.status == SyncStatus.IN_SYNC:
                    action = SyncAction.SKIP
                    result.skipped += 1

                elif task.status == SyncStatus.SOURCE_NEWER:
                    # Show Dialog
                    dialog = UpdateAvailableDialog(self, task)
                    if dialog.result:
                        action = dialog.result.action
                    else:
                        action = SyncAction.SKIP  # Dialog cancelled

                elif task.status == SyncStatus.TARGET_NEWER:
                    # Show Dialog
                    dialog_local = LocalChangesDialog(self, task)
                    if dialog_local.result:
                        action = dialog_local.result.action
                    else:
                        action = SyncAction.SKIP

                # Execute Action
                if action != SyncAction.SKIP:
                    success = self._agent_builder.process_task(task, action)
                    if success:
                        if action == SyncAction.COPY:
                            self._log(f"✅ Copied: {task.target_filename}")
                            result.copied += 1
                        elif action == SyncAction.UPDATE_SOURCE:
                            self._log(f"⬅️  Updated Source: {task.source_path.name}")
                            result.copied += 1  # Count as processed
                    else:
                        self._log(f"⚠️ Failed to process: {task.target_filename}")

            # Final Report
            self._log("")
            self._log(f"🏁 Build complete!")
            self._log(f"   Processed: {result.copied}")
            self._log(f"   Skipped: {result.skipped}")

            if result.warnings:
                self._log("")
                self._log("⚠️ Warnings:")
                for warning in result.warnings:
                    self._log(f"   - {warning}")

            self._status_callback(
                f"Build complete: {result.copied} processed, {result.skipped} skipped"
            )

        except Exception as e:
            self._log(f"❌ Unexpected error: {e}")
            self._status_callback(f"Error: {e}")
            logger.exception("build_failed", error=str(e))

        finally:
            self._build_button.config(state=tk.NORMAL)
