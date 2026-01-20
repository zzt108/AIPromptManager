"""Tests for AgentBuilder."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from models.agent_config import AgentConfig
from models.service_results import BuildResult, VersionUpdate
from repositories.registry_repository import RegistryRepository
from services.agent_builder import AgentBuilder
from services.registry_service import RegistryService


@pytest.fixture
def tmp_repo_with_skills(tmp_path: Path) -> Path:
    """Create a temporary repository with skill files.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to the temporary repository root
    """
    # Create directories
    (tmp_path / "core").mkdir()
    (tmp_path / "platform" / "python").mkdir(parents=True)

    # Create test markdown files
    (tmp_path / "core" / "GUIDE-1-2-General.md").write_text(
        "# General Coding Conventions\n\nContent.",
        encoding="utf-8",
    )
    (tmp_path / "core" / "GUIDE-1-3-General.md").write_text(
        "# General Coding Conventions (Updated)\n\nNewer content.",
        encoding="utf-8",
    )
    (
        tmp_path / "platform" / "python" / "GUIDE-1-0-coding-convention-python.md"
    ).write_text(
        "# Python Coding Conventions\n\nPython rules.",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture
def populated_registry_path(tmp_path: Path) -> Path:
    """Create a registry.json with test skills.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to registry.json
    """
    registry_path = tmp_path / "registry.json"
    registry_data = {
        "version": "1.0",
        "ingredients": {
            "GUIDE-1-2-General": {
                "name": "GUIDE-1-2-General",
                "path": "core/GUIDE-1-2-General.md",
                "description": "General Coding Conventions",
                "type": "GUIDE",
                "major": 1,
                "minor": 2,
                "basename": "General",
            },
            "GUIDE-1-3-General": {
                "name": "GUIDE-1-3-General",
                "path": "core/GUIDE-1-3-General.md",
                "description": "General Coding Conventions (Updated)",
                "type": "GUIDE",
                "major": 1,
                "minor": 3,
                "basename": "General",
            },
            "GUIDE-1-0-coding-convention-python": {
                "name": "GUIDE-1-0-coding-convention-python",
                "path": "platform/python/GUIDE-1-0-coding-convention-python.md",
                "description": "Python Coding Conventions",
                "type": "GUIDE",
                "major": 1,
                "minor": 0,
                "basename": "coding-convention-python",
            },
        },
    }
    registry_path.write_text(json.dumps(registry_data), encoding="utf-8")
    return registry_path


@pytest.fixture
def agent_builder(
    tmp_repo_with_skills: Path,
    populated_registry_path: Path,
) -> AgentBuilder:
    """Create an AgentBuilder instance for testing.

    Args:
        tmp_repo_with_skills: Temporary repository with test files
        populated_registry_path: Path to populated registry

    Returns:
        Configured AgentBuilder
    """
    repo = RegistryRepository()
    registry_service = RegistryService(
        registry_repository=repo,
        registry_path=populated_registry_path,
        repo_root=tmp_repo_with_skills,
    )
    return AgentBuilder(
        registry_service=registry_service,
        repo_root=tmp_repo_with_skills,
    )


@pytest.fixture
def tmp_agent_config_file(tmp_path: Path) -> Path:
    """Create a temporary agent.config.json file.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to agent.config.json
    """
    config_path = tmp_path / "agent.config.json"
    config_data = {
        "ingredients": [
            "GUIDE-1-2-General",
            "GUIDE-1-0-coding-convention-python",
        ]
    }
    config_path.write_text(json.dumps(config_data), encoding="utf-8")
    return config_path


class TestBuildAgent:
    """Tests for build_agent method."""

    def test_build_agent_success(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test building agent folder with valid config."""
        output_path = tmp_path / "output" / ".agent" / "rules"

        result = agent_builder.build_agent(tmp_agent_config_file, output_path)

        assert result.copied == 2
        assert result.skipped == 0
        assert output_path.exists()

    def test_build_agent_creates_directory(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test build creates output directory if missing."""
        output_path = tmp_path / "new" / "nested" / "output"

        agent_builder.build_agent(tmp_agent_config_file, output_path)

        assert output_path.exists()

    def test_build_agent_versionless_names(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test output files use version-less naming."""
        output_path = tmp_path / "output"

        agent_builder.build_agent(tmp_agent_config_file, output_path)

        # Check files are renamed to version-less format
        assert (output_path / "GUIDE--General.md").exists()
        assert (output_path / "GUIDE--coding-convention-python.md").exists()
        # Versioned names should not exist
        assert not (output_path / "GUIDE-1-2-General.md").exists()

    def test_build_agent_missing_skill(
        self,
        agent_builder: AgentBuilder,
        tmp_path: Path,
    ) -> None:
        """Test build with missing skill raises ValueError."""
        config_path = tmp_path / "bad_config.json"
        config_data = {"ingredients": ["NONEXISTENT"]}
        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        output_path = tmp_path / "output"

        with pytest.raises(ValueError, match="Missing skills"):
            agent_builder.build_agent(config_path, output_path)

    def test_build_agent_skips_unchanged(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test build skips files that haven't changed."""
        output_path = tmp_path / "output"

        # First build
        result1 = agent_builder.build_agent(tmp_agent_config_file, output_path)
        assert result1.copied == 2

        # Second build should skip
        result2 = agent_builder.build_agent(tmp_agent_config_file, output_path)
        assert result2.copied == 0
        assert result2.skipped == 2


class TestCheckNewerVersions:
    """Tests for check_newer_versions method."""

    def test_check_newer_versions_finds_updates(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
    ) -> None:
        """Test detecting when newer version exists."""
        config = AgentConfig.from_file(tmp_agent_config_file)

        updates = agent_builder.check_newer_versions(config)

        # GUIDE-1-2-General has a newer version (1.3)
        assert len(updates) == 1
        assert updates[0].ingredient_name == "GUIDE-1-2-General"
        assert updates[0].current_minor == 2
        assert updates[0].latest_minor == 3

    def test_check_newer_versions_all_current(
        self,
        agent_builder: AgentBuilder,
        tmp_path: Path,
    ) -> None:
        """Test returns empty list when all up-to-date."""
        config_path = tmp_path / "latest_config.json"
        config_data = {"ingredients": ["GUIDE-1-3-General"]}
        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        config = AgentConfig.from_file(config_path)
        updates = agent_builder.check_newer_versions(config)

        assert len(updates) == 0

    def test_check_newer_versions_adds_warnings_to_build(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test build result includes version update warnings."""
        output_path = tmp_path / "output"

        result = agent_builder.build_agent(tmp_agent_config_file, output_path)

        assert len(result.warnings) == 1
        assert "1.2 →" in result.warnings[0]
        assert "1.3" in result.warnings[0]


class TestMakeVersionlessName:
    """Tests for _make_versionless_name method."""

    def test_make_versionless_name_versioned(
        self,
        agent_builder: AgentBuilder,
    ) -> None:
        """Test converting versioned to version-less filename."""
        result = agent_builder._make_versionless_name("GUIDE-1-2-General.md")

        assert result == "GUIDE--General.md"

    def test_make_versionless_name_already_versionless(
        self,
        agent_builder: AgentBuilder,
    ) -> None:
        """Test version-less filename passes through unchanged."""
        result = agent_builder._make_versionless_name("GUIDE--General.md")

        assert result == "GUIDE--General.md"

    def test_make_versionless_name_unknown_format(
        self,
        agent_builder: AgentBuilder,
    ) -> None:
        """Test unknown format passes through unchanged."""
        result = agent_builder._make_versionless_name("README.md")

        assert result == "README.md"


class TestGetSyncStatus:
    """Tests for get_sync_status method."""

    def test_get_sync_status_not_deployed(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test status shows not_deployed for missing files."""
        output_path = tmp_path / "empty_output"
        output_path.mkdir()

        status = agent_builder.get_sync_status(tmp_agent_config_file, output_path)

        assert status["GUIDE-1-2-General"] == "not_deployed"
        assert status["GUIDE-1-0-coding-convention-python"] == "not_deployed"

    def test_get_sync_status_in_sync(
        self,
        agent_builder: AgentBuilder,
        tmp_agent_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test status shows in_sync after build."""
        output_path = tmp_path / "output"
        agent_builder.build_agent(tmp_agent_config_file, output_path)

        status = agent_builder.get_sync_status(tmp_agent_config_file, output_path)

        assert status["GUIDE-1-2-General"] == "in_sync"
        assert status["GUIDE-1-0-coding-convention-python"] == "in_sync"


class TestVersionUpdate:
    """Tests for VersionUpdate dataclass."""

    def test_version_update_str(self) -> None:
        """Test human-readable string representation."""
        update = VersionUpdate(
            ingredient_name="GUIDE-1-2-General",
            current_major=1,
            current_minor=2,
            latest_major=1,
            latest_minor=3,
            latest_name="GUIDE-1-3-General",
        )

        result = str(update)

        assert "GUIDE-1-2-General" in result
        assert "1.2 →" in result
        assert "1.3" in result

    def test_version_update_properties(self) -> None:
        """Test version property methods."""
        update = VersionUpdate(
            ingredient_name="test",
            current_major=1,
            current_minor=2,
            latest_major=2,
            latest_minor=0,
            latest_name="test-2-0",
        )

        assert update.current_version == "1.2"
        assert update.latest_version == "2.0"
