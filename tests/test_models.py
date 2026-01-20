"""Tests for data models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from models.agent_config import AgentConfig
from models.skill import Skill
from models.registry_schema import RegistrySchema


class TestSkill:
    """Tests for Skill model."""

    def test_from_dict_success(self) -> None:
        """Test creating Skill from dictionary."""
        # Arrange
        data: dict[str, Any] = {
            "name": "test-guide",
            "path": "guides/test.md",
            "description": "Test Guide",
            "type": "GUIDE",
            "major": 2,
            "minor": 3,
            "basename": "test",
        }

        # Act
        skill = Skill.from_dict(data)

        # Assert
        assert skill.name == "test-guide"
        assert skill.path == Path("guides/test.md")
        assert skill.description == "Test Guide"
        assert skill.type == "GUIDE"
        assert skill.major == 2
        assert skill.minor == 3
        assert skill.basename == "test"

    def test_to_dict_success(self, sample_skill: Skill) -> None:
        """Test converting Skill to dictionary."""
        # Act
        data = sample_skill.to_dict()

        # Assert
        assert data["name"] == "python-conventions"
        assert data["path"] == "platform/python/GUIDE-1-0-coding-convention-python.md"
        assert data["description"] == "Python Coding Conventions & Standards"
        assert data["type"] == "GUIDE"
        assert data["major"] == 1
        assert data["minor"] == 0
        assert data["basename"] == "coding-convention-python"

    def test_round_trip_conversion(self, sample_skill: Skill) -> None:
        """Test Skill survives dict conversion round trip."""
        # Act
        data = sample_skill.to_dict()
        restored = Skill.from_dict(data)

        # Assert
        assert restored.name == sample_skill.name
        assert restored.path == sample_skill.path
        assert restored.description == sample_skill.description
        assert restored.type == sample_skill.type
        assert restored.major == sample_skill.major
        assert restored.minor == sample_skill.minor
        assert restored.basename == sample_skill.basename


class TestRegistrySchema:
    """Tests for RegistrySchema model."""

    def test_from_dict_success(self, sample_skill: Skill) -> None:
        """Test creating RegistrySchema from dictionary."""
        # Arrange
        data: dict[str, Any] = {
            "version": "1.0",
            "ingredients": {"test": sample_skill.to_dict()},
        }

        # Act
        schema = RegistrySchema.from_dict(data)

        # Assert
        assert schema.version == "1.0"
        assert len(schema.skills) == 1
        assert "test" in schema.skills

    def test_from_dict_missing_version_raises_error(self) -> None:
        """Test missing version field raises ValueError."""
        # Arrange
        data: dict[str, Any] = {"ingredients": {}}

        # Act & Assert
        with pytest.raises(ValueError, match="Missing 'version' field"):
            RegistrySchema.from_dict(data)

    def test_validate_success(self, sample_skill: Skill) -> None:
        """Test schema validation passes for valid data."""
        # Arrange
        schema = RegistrySchema(
            version="1.0", skills={"python-conventions": sample_skill}
        )

        # Act & Assert (should not raise)
        schema.validate()

    def test_validate_name_mismatch_raises_error(self, sample_skill: Skill) -> None:
        """Test validation fails when skill name doesn't match key."""
        # Arrange
        schema = RegistrySchema(version="1.0", skills={"wrong-key": sample_skill})

        # Act & Assert
        with pytest.raises(ValueError, match="name mismatch"):
            schema.validate()

    def test_to_dict_success(self, sample_skill: Skill) -> None:
        """Test converting RegistrySchema to dictionary."""
        # Arrange
        schema = RegistrySchema(
            version="1.0", skills={"python-conventions": sample_skill}
        )

        # Act
        data = schema.to_dict()

        # Assert
        assert data["version"] == "1.0"
        assert "ingredients" in data
        assert "python-conventions" in data["ingredients"]


class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_from_file_success(self, tmp_agent_config: Path) -> None:
        """Test loading agent config from file."""
        # Act
        config = AgentConfig.from_file(tmp_agent_config)

        # Assert
        assert len(config.ingredients) == 2
        assert "python-conventions" in config.ingredients
        assert "plantuml-core" in config.ingredients

    def test_from_file_not_found_raises_error(self, tmp_path: Path) -> None:
        """Test loading non-existent config raises FileNotFoundError."""
        # Arrange
        nonexistent = tmp_path / "missing.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            AgentConfig.from_file(nonexistent)

    def test_from_file_invalid_json_raises_error(self, tmp_path: Path) -> None:
        """Test loading malformed JSON raises ValueError."""
        # Arrange
        invalid_config = tmp_path / "invalid.json"
        invalid_config.write_text("{invalid json}", encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid JSON"):
            AgentConfig.from_file(invalid_config)

    def test_to_file_success(self, tmp_path: Path) -> None:
        """Test saving agent config to file."""
        # Arrange
        config = AgentConfig(ingredients=["guide1", "guide2"])
        config_path = tmp_path / "config.json"

        # Act
        config.to_file(config_path)

        # Assert
        assert config_path.exists()
        loaded_config = AgentConfig.from_file(config_path)
        assert loaded_config.ingredients == ["guide1", "guide2"]

    def test_validate_success(self, sample_skill: Skill) -> None:
        """Test validation passes when all skills exist in registry."""
        # Arrange
        registry = RegistrySchema(
            version="1.0", skills={"python-conventions": sample_skill}
        )
        config = AgentConfig(ingredients=["python-conventions"])

        # Act & Assert (should not raise)
        config.validate(registry)

    def test_validate_missing_skill_raises_error(self, sample_skill: Skill) -> None:
        """Test validation fails when skill doesn't exist in registry."""
        # Arrange
        registry = RegistrySchema(
            version="1.0", skills={"python-conventions": sample_skill}
        )
        config = AgentConfig(ingredients=["nonexistent"])

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid ingredient references"):
            config.validate(registry)
