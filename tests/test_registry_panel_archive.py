"""Tests for Archive/Restore features in RegistryPanel."""

from __future__ import annotations

import tkinter as tk
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest

from models.skill import Skill
from models.skill_status import SkillStatus
from ui.registry_panel import RegistryPanel


def make_skill(name: str, status: SkillStatus = SkillStatus.VALID) -> Skill:
    """Create a test Skill."""
    return Skill(
        name=name,
        path=Path(f"core/{name}.md"),
        description=f"Test {name}",
        type="GUIDE",
        major=1,
        minor=0,
        basename=name,
        status=status,
        is_enabled=True,
        modified_at=100.0,
    )


class TestRegistryPanelArchive:
    """Test cases for Archive/Restore UI logic."""

    @pytest.fixture
    def panel(self, tk_root: tk.Tk) -> RegistryPanel:
        """Create a panel with mocked service."""
        service = MagicMock()
        service.list_all.return_value = []
        service.repo_root = Path("/tmp")
        return RegistryPanel(tk_root, service, lambda msg: None)

    def test_archive_skills_success(self, panel: RegistryPanel) -> None:
        """Test invoking archive action."""
        panel._service.list_all.return_value = [make_skill("Skill1")]
        panel.refresh_list()

        # Select item
        children = panel.tree.get_children()
        assert len(children) == 1
        panel.tree.selection_set(children[0])

        # Mock confirmation and service
        with patch("tkinter.messagebox.askyesno", return_value=True):
            panel._service.archive_skills.return_value = 1
            panel._on_archive_click()

        panel._service.archive_skills.assert_called_with(["Skill1"])

    def test_archive_skills_cancel(self, panel: RegistryPanel) -> None:
        """Test cancelling archive action."""
        panel._service.list_all.return_value = [make_skill("Skill1")]
        panel.refresh_list()

        children = panel.tree.get_children()
        panel.tree.selection_set(children[0])

        with patch("tkinter.messagebox.askyesno", return_value=False):
            panel._on_archive_click()

        panel._service.archive_skills.assert_not_called()

    def test_restore_skills_success(self, panel: RegistryPanel) -> None:
        """Test invoking restore action."""
        # Setup archived skill
        skill = make_skill("Skill1", SkillStatus.ARCHIVED)
        panel._service.list_all.return_value = [skill]

        # Enable "Show Archived" to see it
        panel.show_archived_var.set(True)
        panel.refresh_list()

        children = panel.tree.get_children()
        assert len(children) == 1
        panel.tree.selection_set(children[0])

        with patch("tkinter.messagebox.askyesno", return_value=True):
            panel._service.restore_skills.return_value = 1
            panel._on_restore_click()

        panel._service.restore_skills.assert_called_with(["Skill1"])

    def test_show_archived_filter(self, panel: RegistryPanel) -> None:
        """Test toggling the Show Archived checkbox."""
        panel._service.list_all.return_value = [
            make_skill("ValidSkill", SkillStatus.VALID),
            make_skill("ArchivedSkill", SkillStatus.ARCHIVED),
        ]

        # Default: Hidden (show_archived_var defaults to False in code)
        panel.show_archived_var.set(False)
        panel.refresh_list()
        assert len(panel.tree.get_children()) == 1
        assert (
            panel.tree.item(panel.tree.get_children()[0], "values")[2] == "ValidSkill"
        )

        # Show
        panel.show_archived_var.set(True)
        # Calling _apply_filter directly as checkbox command, or refresh_list
        panel._apply_filter()

        children = panel.tree.get_children()
        assert len(children) == 2
