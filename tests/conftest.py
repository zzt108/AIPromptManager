"""Shared pytest fixtures for AI Prompt Manager tests."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Any

import pytest

from models.ingredient import Ingredient
from models.registry_schema import RegistrySchema


@pytest.fixture(scope="session")
def tk_root() -> tk.Tk:
    """Create a single session-scoped hidden Tk root.

    This avoids 'invalid command name tcl_findLibrary' and other
    Tcl initialization errors on Windows when running multiple
    UI test modules.
    """
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def sample_ingredient() -> Ingredient:
    """Create a sample Ingredient instance for testing.

    Returns:
        Ingredient with test data
    """
    return Ingredient(
        name="python-conventions",
        path=Path("platform/python/GUIDE-1-0-coding-convention-python.md"),
        description="Python Coding Conventions & Standards",
        type="GUIDE",
        major=1,
        minor=0,
        basename="coding-convention-python",
    )


@pytest.fixture
def tmp_registry(tmp_path: Path) -> Path:
    """Create a temporary registry.json file with sample data.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to temporary registry.json
    """
    registry_path = tmp_path / "registry.json"

    # Sample registry data
    registry_data: dict[str, Any] = {
        "version": "1.0",
        "ingredients": {
            "python-conventions": {
                "name": "python-conventions",
                "path": "platform/python/GUIDE-1-0-coding-convention-python.md",
                "description": "Python Coding Conventions & Standards",
                "type": "GUIDE",
                "major": 1,
                "minor": 0,
                "basename": "coding-convention-python",
            },
            "plantuml-core": {
                "name": "plantuml-core",
                "path": "visualization/GUIDE-1-4-visualization-plantuml-core.md",
                "description": "PlantUML Core Syntax Guide",
                "type": "GUIDE",
                "major": 1,
                "minor": 4,
                "basename": "visualization-plantuml-core",
            },
        },
    }

    # Write registry to file
    import json

    registry_path.write_text(
        json.dumps(registry_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return registry_path


@pytest.fixture
def tmp_empty_registry(tmp_path: Path) -> Path:
    """Create a temporary empty registry.json file.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to temporary empty registry.json
    """
    registry_path = tmp_path / "registry.json"

    registry_data: dict[str, Any] = {"version": "1.0", "ingredients": {}}

    import json

    registry_path.write_text(
        json.dumps(registry_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return registry_path


@pytest.fixture
def tmp_agent_config(tmp_path: Path) -> Path:
    """Create a temporary agent.config.json file.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to temporary agent.config.json
    """
    config_path = tmp_path / ".agent" / "agent.config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config_data: dict[str, Any] = {
        "ingredients": ["python-conventions", "plantuml-core"]
    }

    import json

    config_path.write_text(
        json.dumps(config_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return config_path
