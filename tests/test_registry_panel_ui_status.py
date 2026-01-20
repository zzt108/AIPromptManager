import pytest
from unittest.mock import MagicMock
from pathlib import Path
import tkinter as tk
from models.skill import Skill
from models.skill_status import SkillStatus
from ui.registry_panel import RegistryPanel


def make_skill_with_status(
    name: str,
    status: SkillStatus,
    details: str | None = None,
    modified_at: float = 0.0,
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
        modified_at=modified_at,
    )


class TestRegistryPanelStatus:

    def test_status_icons_and_tags(self, tk_root: tk.Tk) -> None:
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

        # Check Valid Skill (modified_at=0.0 -> empty string)
        val_item = panel.tree.item("valid_skill")
        assert val_item["values"][0] == "✓"  # Icon
        assert val_item["values"][5] == ""
        assert "status_valid" in val_item["tags"]

        # Check Unrecognized Skill (modified_at=0.0 -> empty string)
        unrec_item = panel.tree.item("unrec_skill")
        assert unrec_item["values"][0] == "⚠️"
        assert unrec_item["values"][5] == ""
        assert "status_unrecognized" in unrec_item["tags"]

        # Check Error Skill
        err_item = panel.tree.item("error_skill")
        assert err_item["values"][0] == "❌"
        assert "status_parse_error" in err_item["tags"]

    def test_filter_includes_modified_date(self, tk_root: tk.Tk) -> None:
        mock_service = MagicMock()
        # 2024-01-01 12:00:00 UTC timestamp = 1704110400
        skills = [
            make_skill_with_status(
                "recent", SkillStatus.VALID, modified_at=1704110400.0
            ),
        ]
        mock_service.list_all.return_value = skills

        panel = RegistryPanel(tk_root, mock_service, lambda msg: None)

        # Filter by year
        panel.filter_var.set("2024")
        panel._apply_filter()

        children = panel.tree.get_children()
        assert len(children) == 1
        assert children[0] == "recent"

        # Verify formatting
        item = panel.tree.item("recent")
        assert "2024-01-01" in item["values"][5]
