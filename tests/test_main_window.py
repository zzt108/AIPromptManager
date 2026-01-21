"""Tests for MainWindow."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

# Mock tkinter at the very top
mock_tk = MagicMock()
mock_ttk = MagicMock()

with patch.dict(
    "sys.modules",
    {
        "tkinter": mock_tk,
        "tkinter.ttk": mock_ttk,
        "tkinter.messagebox": MagicMock(),
        "tkinter.filedialog": MagicMock(),
    },
):
    from ui.main_window import MainWindow

import pytest


@pytest.fixture
def mock_services() -> dict[str, MagicMock]:
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
def main_window(mock_services: dict[str, MagicMock]) -> MainWindow:
    return MainWindow(
        registry_service=mock_services["registry"],
        agent_builder=mock_services["agent"],
        settings_service=mock_services["settings"],
    )


class TestMainWindow:
    def test_mainwindow_basic(self, main_window: MainWindow) -> None:
        """Basic check if MainWindow instantiates and has attributes."""
        # Just check it exists and has some basic attributes
        assert main_window is not None
        assert hasattr(main_window, "notebook")
        assert hasattr(main_window, "status_bar")
