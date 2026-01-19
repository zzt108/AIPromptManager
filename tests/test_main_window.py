"""Tests for MainWindow."""

from __future__ import annotations

import os
import tkinter as tk
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from ui.main_window import MainWindow

# Detect if running in CI or headless environment
_is_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"

# Skip all tests in this module if in CI (no display available)
pytestmark = pytest.mark.skipif(
    _is_ci,
    reason="MainWindow tests require a display (Tcl/Tk) which is not available in CI",
)


@pytest.fixture(scope="module")
def main_window(tk_root):
    """Create a single MainWindow instance for the entire module."""
    mock_registry_service = MagicMock()
    mock_registry_service.list_all.return_value = []
    mock_agent_builder = MagicMock()

    # Patch tk.Tk to be Toplevel so we don't try to create a second root
    # which causes TclError in some environments (like CI)
    with patch("tkinter.Tk", new=tk.Toplevel):
        import importlib
        import ui.main_window

        # Force reload so MainWindow class is redefined using the patched tk.Tk
        importlib.reload(ui.main_window)
        from ui.main_window import MainWindow

        # MainWindow calls super().__init__() which becomes Toplevel().__init__()
        # This automatically attaches to the existing default root (created by tk_root)
        window = MainWindow(mock_registry_service, mock_agent_builder)

    window.withdraw()

    yield window

    window.destroy()


class TestMainWindow:
    """Test cases for MainWindow class."""

    def test_mainwindow_instantiation(self, main_window: MainWindow) -> None:
        """Test that MainWindow can be instantiated with mock service."""
        assert main_window.title() == "AI Prompt Manager"
        assert main_window.notebook is not None
        assert main_window.registry_panel is not None
        assert main_window.build_panel is not None
        assert main_window.status_bar is not None

    def test_mainwindow_has_registry_tab(self, main_window: MainWindow) -> None:
        """Test that Knowledge Base tab exists in notebook."""
        tabs = main_window.notebook.tabs()
        assert len(tabs) >= 2

        # Check tab names
        tab_text_0 = main_window.notebook.tab(tabs[0], "text")
        assert tab_text_0 == "Knowledge Base"

    def test_mainwindow_has_build_tab(self, main_window: MainWindow) -> None:
        """Test that Agent Onboarding tab exists in notebook."""
        tabs = main_window.notebook.tabs()
        tab_text_2 = main_window.notebook.tab(tabs[2], "text")
        assert tab_text_2 == "Agent Onboarding"

    def test_status_bar_initial_text(self, main_window: MainWindow) -> None:
        """Test that status bar shows skill count after load."""
        status_text = main_window.status_bar.cget("text")
        assert "0 skills" in status_text
