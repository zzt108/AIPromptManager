"""Tests for MainWindow."""

from __future__ import annotations

import os
import tkinter as tk
from unittest.mock import MagicMock
from typing import TYPE_CHECKING, Generator

import pytest

if TYPE_CHECKING:
    from ui.main_window import MainWindow


# Global check for Tkinter availability
def check_tk_available() -> bool:
    """Check if a real Tcl/Tk interpreter is available and working."""
    if os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true":
        return False
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except (tk.TclError, Exception):
        return False


HAS_TK = check_tk_available()

# Skip all tests in this module if no display or Tcl is broken
pytestmark = pytest.mark.skipif(
    not HAS_TK,
    reason="MainWindow tests require a working Tcl/Tk environment (display available and init.tcl found)",
)


@pytest.fixture
def mock_services() -> dict[str, MagicMock]:
    """Create mock services for MainWindow."""
    registry = MagicMock()
    registry.list_enabled.return_value = []
    registry.list_all.return_value = []

    settings = MagicMock()
    settings.get_merge_tool_config.return_value = {
        "name": "manual",
        "path": "",
        "args_2way": "",
        "args_3way": "",
    }

    agent = MagicMock()

    return {"registry": registry, "settings": settings, "agent": agent}


@pytest.fixture
def main_window(
    tk_root: tk.Tk, mock_services: dict[str, MagicMock]
) -> Generator[MainWindow, None, None]:
    """Create a MainWindow instance using the session tk_root."""
    # Importing here to avoid issues if Tcl is broken at top level
    from ui.main_window import MainWindow

    # We patch tk.Tk to return a Toplevel so we don't create a second root.
    # This is safe because it only happens during the lifetime of this fixture.
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("tkinter.Tk", tk.Toplevel)

        window = MainWindow(
            registry_service=mock_services["registry"],
            agent_builder=mock_services["agent"],
            settings_service=mock_services["settings"],
        )

        window.withdraw()
        yield window
        window.destroy()


class TestMainWindow:
    """Test cases for MainWindow class."""

    def test_mainwindow_instantiation(self, main_window: MainWindow) -> None:
        """Test that MainWindow can be instantiated with mock services."""
        assert main_window.title() == "AI Prompt Manager"
        assert main_window.notebook is not None
        assert main_window.registry_panel is not None

    def test_mainwindow_has_tabs(self, main_window: MainWindow) -> None:
        """Test that tabs exist in notebook."""
        tabs = main_window.notebook.tabs()  # type: ignore[no-untyped-call]
        assert len(tabs) >= 3

    def test_status_bar_initial_text(self, main_window: MainWindow) -> None:
        """Test that status bar shows skill count after load."""
        status_text: str = main_window.status_bar.cget("text")
        assert "0 skills" in status_text
