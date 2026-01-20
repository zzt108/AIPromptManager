"""Tests for RegistryPanel."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from unittest.mock import MagicMock

import pytest

from models.skill import Skill
from ui.registry_panel import RegistryPanel


def make_skill(name: str, skill_type: str = "GUIDE") -> Skill:
    """Create a test Skill."""
    return Skill(
        name=name,
        path=Path(f"core/{name}.md"),
        description=f"Test {name}",
        type=skill_type,
        major=1,
        minor=0,
        basename=name.split("-")[-1] if "-" in name else name,
    )


class TestRegistryPanel:
    """Test cases for RegistryPanel class."""

    def test_registry_panel_instantiation(self, tk_root: tk.Tk) -> None:
        """Test that RegistryPanel can be instantiated."""
        mock_service = MagicMock()
        mock_service.list_all.return_value = []

        panel = RegistryPanel(tk_root, mock_service, lambda msg: None)

        assert panel.tree is not None
        mock_service.list_all.assert_called_once()

    def test_refresh_list_calls_service(self, tk_root: tk.Tk) -> None:
        """Test that refresh_list calls service.list_all."""
        mock_service = MagicMock()
        mock_service.list_all.return_value = []

        panel = RegistryPanel(tk_root, mock_service, lambda msg: None)

        # Reset call count after init
        mock_service.list_all.reset_mock()

        panel.refresh_list()

        mock_service.list_all.assert_called_once()

    def test_refresh_list_populates_treeview(self, tk_root: tk.Tk) -> None:
        """Test that refresh_list populates treeview with skills."""
        mock_service = MagicMock()

        test_skills = [
            make_skill("GUIDE-1-0-General", "GUIDE"),
            make_skill("SPACE-260116-Python", "SPACE"),
        ]
        mock_service.list_all.return_value = test_skills

        panel = RegistryPanel(tk_root, mock_service, lambda msg: None)

        # Check treeview has items
        children = panel.tree.get_children()
        assert len(children) == 2

        # Check first item values
        first_values = panel.tree.item(children[0], "values")
        assert first_values[0] == "GUIDE"  # Type
        assert first_values[1] == "GUIDE-1-0-General"  # Name

    def test_status_callback_called_after_refresh(self, tk_root: tk.Tk) -> None:
        """Test that status callback is invoked with skill count."""
        mock_service = MagicMock()

        test_skills = [
            make_skill("GUIDE-1-0-General", "GUIDE"),
        ]
        mock_service.list_all.return_value = test_skills

        status_messages: list[str] = []

        def capture_status(msg: str) -> None:
            status_messages.append(msg)

        panel = RegistryPanel(tk_root, mock_service, capture_status)

        assert len(status_messages) > 0
        assert "1 skills" in status_messages[-1]

    def test_refresh_button_triggers_scan(self, tk_root: tk.Tk) -> None:
        """Test that clicking refresh button calls refresh_registry."""
        mock_service = MagicMock()
        mock_service.list_all.return_value = []
        mock_service.refresh_registry.return_value = MagicMock(
            added=0, updated=0, removed=0
        )

        panel = RegistryPanel(tk_root, mock_service, lambda msg: None)

        # Simulate button click
        panel._on_refresh_click()

        mock_service.refresh_registry.assert_called_once()
