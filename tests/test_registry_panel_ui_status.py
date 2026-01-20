import pytest
from unittest.mock import MagicMock
from pathlib import Path
import tkinter as tk
from models.skill import Skill
from models.skill_status import SkillStatus
from ui.registry_panel import RegistryPanel


def make_skill_with_status(
    name: str, status: SkillStatus, details: str | None = None
) -> Skill:
    """Create a test Skill with specific status."""
    return Skill(
        name=name,
        path=Path(f"core/{name}.md"),
        description=f"Test {name}",
        type="GUIDE",
        major=1,
        minor=0,
        basename="test",
        status=status,
        status_detail=details,
    )


class TestRegistryPanelStatus:

    def test_status_icons_and_tags(self, tk_root):
        mock_service = MagicMock()

        skills = [
            make_skill_with_status("valid_skill", SkillStatus.VALID),
            make_skill_with_status(
                "unrec_skill", SkillStatus.UNRECOGNIZED, "Pattern mismatch"
            ),
            make_skill_with_status("error_skill", SkillStatus.PARSE_ERROR, "Bad YAML"),
        ]
        mock_service.list_all.return_value = skills

        panel = RegistryPanel(tk_root, mock_service, lambda msg: None)

        # Get all items in tree
        children = panel.tree.get_children()
        assert len(children) == 3

        # Check Valid Skill
        val_item = panel.tree.item("valid_skill")
        assert val_item["values"][0] == "✓"  # Icon
        assert val_item["values"][5] == ""  # Details (empty string for None)
        assert "status_valid" in val_item["tags"]

        # Check Unrecognized Skill
        unrec_item = panel.tree.item("unrec_skill")
        assert unrec_item["values"][0] == "⚠️"
        assert unrec_item["values"][5] == "Pattern mismatch"
        assert "status_unrecognized" in unrec_item["tags"]

        # Check Error Skill
        err_item = panel.tree.item("error_skill")
        assert err_item["values"][0] == "❌"
        assert err_item["values"][5] == "Bad YAML"
        assert "status_parse_error" in err_item["tags"]

    def test_filter_includes_details(self, tk_root):
        mock_service = MagicMock()
        skills = [
            make_skill_with_status(
                "foo", SkillStatus.UNRECOGNIZED, "UniqueErrorString"
            ),
        ]
        mock_service.list_all.return_value = skills

        panel = RegistryPanel(tk_root, mock_service, lambda msg: None)

        # Filter by error detail
        panel.filter_var.set("UniqueError")
        panel._apply_filter()

        children = panel.tree.get_children()
        assert len(children) == 1
        assert children[0] == "foo"
