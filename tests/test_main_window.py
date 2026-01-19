"""Tests for MainWindow."""

from __future__ import annotations

import tkinter as tk
from unittest.mock import MagicMock

import pytest

from ui.main_window import MainWindow

# Window will be created in fixture


@pytest.fixture(scope="module")
def main_window(tk_root):
    """Create a single MainWindow instance for the entire module."""
    mock_registry_service = MagicMock()
    mock_registry_service.list_all.return_value = []
    mock_agent_builder = MagicMock()

    # Note: MainWindow inherits from tk.Tk, which is still problematic
    # if it doesn't take a master. But our fixture ensures at least
    # one root exists.
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
