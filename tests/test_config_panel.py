"""Tests for ConfigPanel UI."""

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from unittest.mock import MagicMock, patch

import pytest

from models.ingredient import Ingredient
from ui.config_panel import ConfigPanel


@pytest.fixture
def mock_registry_service() -> MagicMock:
    """Create a mock registry service."""
    service = MagicMock()
    ingredients = [
        Ingredient(
            name="ingredient1",
            path=Path("path/to/i1.md"),
            description="i1 desc",
            type="PROMPT",
            major=1,
            minor=0,
            basename="i1",
        ),
        Ingredient(
            name="ingredient2",
            path=Path("path/to/i2.md"),
            description="i2 desc",
            type="PROMPT",
            major=1,
            minor=0,
            basename="i2",
        ),
    ]
    service.list_all.return_value = ingredients
    service.list_enabled.return_value = ingredients  # Same as list_all for tests
    return service




@pytest.fixture
def config_panel(tk_root, mock_registry_service: MagicMock) -> ConfigPanel:
    """Create a ConfigPanel instance using the shared root."""
    # Create a new notebook for each test to keep widgets isolated
    notebook = ttk.Notebook(tk_root)
    panel = ConfigPanel(notebook, mock_registry_service, MagicMock())
    return panel


def test_initial_state(config_panel, mock_registry_service):
    """Test that the panel initializes correctly."""
    available = config_panel.available_list.get(0, "end")
    assert available == ("ingredient1", "ingredient2")

    selected = config_panel.selected_list.get(0, "end")
    assert selected == ()


def test_add_selected(config_panel):
    """Test adding items from available to selected list."""
    # Select first item in available list
    config_panel.available_list.selection_set(0)

    config_panel._add_selected()

    selected = config_panel.selected_list.get(0, "end")
    assert selected == ("ingredient1",)


def test_add_duplicate_prevention(config_panel):
    """Test that duplicates are not added."""
    # Add item once
    config_panel.available_list.selection_set(0)
    config_panel._add_selected()

    # Try adding again
    config_panel.available_list.selection_set(0)
    config_panel._add_selected()

    selected = config_panel.selected_list.get(0, "end")
    assert selected == ("ingredient1",)


def test_remove_selected(config_panel):
    """Test removing items from selected list."""
    # setup: add an item
    config_panel.available_list.selection_set(0)
    config_panel._add_selected()

    # Select in selected list
    config_panel.selected_list.selection_set(0)

    config_panel._remove_selected()

    selected = config_panel.selected_list.get(0, "end")
    assert selected == ()


def test_move_up(config_panel):
    """Test moving an item up."""
    # Add two items
    config_panel.available_list.selection_set(0)
    config_panel.available_list.selection_set(1)
    config_panel._add_selected()

    # Manually populate selected list for controlled state
    config_panel.selected_list.delete(0, "end")
    config_panel.selected_list.insert("end", "item1")
    config_panel.selected_list.insert("end", "item2")

    # Select second item ("item2")
    config_panel.selected_list.selection_set(1)

    config_panel._move_up()

    current = config_panel.selected_list.get(0, "end")
    assert current == ("item2", "item1")


def test_move_down(config_panel):
    """Test moving an item down."""
    config_panel.selected_list.insert("end", "item1")
    config_panel.selected_list.insert("end", "item2")

    # Select first item ("item1")
    config_panel.selected_list.selection_set(0)

    config_panel._move_down()

    current = config_panel.selected_list.get(0, "end")
    assert current == ("item2", "item1")


def test_new_profession(config_panel):
    """Test clearing the profession."""
    config_panel.selected_list.insert("end", "item1")

    with patch("tkinter.messagebox.askyesno", return_value=True):
        config_panel._new_config()

    assert config_panel.selected_list.size() == 0


def test_load_profession(config_panel, tmp_path):
    """Test loading profession from file."""
    config_file = tmp_path / "agent.config.json"
    config_data = {"ingredients": ["file1", "file2"]}
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    config_panel.load_config(config_file)

    selected = config_panel.selected_list.get(0, "end")
    assert selected == ("file1", "file2")


def test_save_profession(config_panel, tmp_path):
    """Test saving profession to file."""
    config_panel.selected_list.insert("end", "saved1")
    config_panel.selected_list.insert("end", "saved2")

    save_path = tmp_path / "saved_config.json"

    config_panel.save_config(save_path)

    assert save_path.exists()
    data = json.loads(save_path.read_text(encoding="utf-8"))
    assert data["ingredients"] == ["saved1", "saved2"]
