"""Tests for RegistryRepository."""

from __future__ import annotations

from pathlib import Path

import pytest

from models.skill import Skill
from models.registry_schema import RegistrySchema
from repositories.registry_repository import RegistryRepository


def test_load_registry_success(tmp_registry: Path) -> None:
    """Test loading and parsing valid registry."""
    # Arrange
    repo = RegistryRepository()

    # Act
    registry = repo.load_registry(tmp_registry)

    # Assert
    assert isinstance(registry, RegistrySchema)
    assert registry.version == "1.0"
    assert len(registry.skills) == 2
    assert "python-conventions" in registry.skills
    assert "plantuml-core" in registry.skills


def test_load_registry_file_not_found(tmp_path: Path) -> None:
    """Test loading non-existent registry raises FileNotFoundError."""
    # Arrange
    repo = RegistryRepository()
    nonexistent = tmp_path / "missing.json"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        repo.load_registry(nonexistent)


def test_load_registry_validates_schema(tmp_path: Path) -> None:
    """Test loading invalid schema raises ValueError."""
    # Arrange
    repo = RegistryRepository()
    invalid_registry = tmp_path / "invalid.json"

    # Write registry with mismatched name
    import json

    invalid_data = {
        "version": "1.0",
        "ingredients": {
            "correct-key": {
                "name": "wrong-name",  # Mismatch!
                "path": "test.md",
                "description": "Test",
                "type": "GUIDE",
                "major": 1,
                "minor": 0,
                "basename": "test",
            }
        },
    }
    invalid_registry.write_text(json.dumps(invalid_data), encoding="utf-8")

    # Act & Assert
    with pytest.raises(ValueError, match="name mismatch"):
        repo.load_registry(invalid_registry)


def test_save_registry_success(tmp_path: Path) -> None:
    """Test saving registry to file."""
    # Arrange
    repo = RegistryRepository()
    registry_path = tmp_path / "new_registry.json"

    skill = Skill(
        name="test",
        path=Path("test.md"),
        description="Test Skill",
        type="GUIDE",
        major=1,
        minor=0,
        basename="test",
    )

    registry = RegistrySchema(version="1.0", skills={"test": skill})

    # Act
    repo.save_registry(registry_path, registry)

    # Assert
    assert registry_path.exists()

    # Verify content
    loaded_registry = repo.load_registry(registry_path)
    assert loaded_registry.version == "1.0"
    assert "test" in loaded_registry.skills


def test_save_registry_round_trip(tmp_registry: Path, tmp_path: Path) -> None:
    """Test save then load produces identical registry."""
    # Arrange
    repo = RegistryRepository()
    original_registry = repo.load_registry(tmp_registry)
    new_path = tmp_path / "round_trip.json"

    # Act
    repo.save_registry(new_path, original_registry)
    loaded_registry = repo.load_registry(new_path)

    # Assert
    assert loaded_registry.version == original_registry.version
    assert len(loaded_registry.skills) == len(original_registry.skills)

    for name, skill in original_registry.skills.items():
        assert name in loaded_registry.skills
        loaded = loaded_registry.skills[name]
        assert loaded.name == skill.name
        assert loaded.path == skill.path
        assert loaded.type == skill.type
        assert loaded.major == skill.major
        assert loaded.minor == skill.minor
