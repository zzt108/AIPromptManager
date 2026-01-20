"""Tests for ConventionsRepository."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from models.conventions_schema import ConventionsSchema
from repositories.conventions_repository import ConventionsRepository
from repositories.json_repository import JsonRepository


@pytest.fixture
def json_repo() -> JsonRepository:
    """Create JsonRepository instance."""
    return JsonRepository()


@pytest.fixture
def conventions_repo(json_repo: JsonRepository) -> ConventionsRepository:
    """Create ConventionsRepository instance."""
    return ConventionsRepository(json_repo)


@pytest.fixture
def sample_conventions_file(tmp_path: Path) -> Path:
    """Create a sample conventions.json file."""
    conventions_path = tmp_path / ".apm" / "conventions.json"
    conventions_path.parent.mkdir(parents=True)
    conventions_data = {
        "file_naming": {
            "pattern": "{TYPE}-{VERSION}-{DESCRIPTION}",
            "version_format": "X-Y",
            "supported_types": ["GUIDE", "SPACE"],
            "output_pattern": "{TYPE}--{DESCRIPTION}",
            "type_separator": "_",
        }
    }
    conventions_path.write_text(json.dumps(conventions_data, indent=2))
    return conventions_path


class TestLoadConventions:
    """Tests for load_conventions method."""

    def test_load_conventions_success(
        self,
        conventions_repo: ConventionsRepository,
        sample_conventions_file: Path,
    ) -> None:
        """Test loading valid conventions file."""
        conventions = conventions_repo.load_conventions(sample_conventions_file)
        assert conventions.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert "GUIDE" in conventions.file_naming.supported_types

    def test_load_conventions_file_not_found(
        self,
        conventions_repo: ConventionsRepository,
        tmp_path: Path,
    ) -> None:
        """Test loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            conventions_repo.load_conventions(tmp_path / "nonexistent.json")

    def test_load_conventions_malformed_json(
        self,
        conventions_repo: ConventionsRepository,
        tmp_path: Path,
    ) -> None:
        """Test loading malformed JSON raises ValueError."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ invalid json }")
        with pytest.raises(ValueError):
            conventions_repo.load_conventions(bad_file)


class TestGetDefaultConventions:
    """Tests for get_default_conventions method."""

    def test_get_default_conventions(
        self, conventions_repo: ConventionsRepository
    ) -> None:
        """Test default conventions have expected values."""
        conventions = conventions_repo.get_default_conventions()
        assert conventions.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert "GUIDE" in conventions.file_naming.supported_types


class TestLoadOrDefault:
    """Tests for load_or_default method."""

    def test_load_or_default_with_valid_file(
        self,
        conventions_repo: ConventionsRepository,
        sample_conventions_file: Path,
    ) -> None:
        """Test load_or_default returns conventions and no warnings."""
        conventions, warnings = conventions_repo.load_or_default(
            sample_conventions_file
        )
        assert conventions.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert len(warnings) == 0

    def test_load_or_default_with_none(
        self, conventions_repo: ConventionsRepository
    ) -> None:
        """Test load_or_default with None returns defaults and no warnings."""
        conventions, warnings = conventions_repo.load_or_default(None)
        assert conventions.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert len(warnings) == 0

    def test_load_or_default_missing_file(
        self,
        conventions_repo: ConventionsRepository,
        tmp_path: Path,
    ) -> None:
        """Test load_or_default returns defaults and warning for missing file."""
        conventions, warnings = conventions_repo.load_or_default(
            tmp_path / "missing.json"
        )
        assert conventions.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert len(warnings) == 1
        assert "not found" in warnings[0]

    def test_load_or_default_malformed_file(
        self,
        conventions_repo: ConventionsRepository,
        tmp_path: Path,
    ) -> None:
        """Test load_or_default returns defaults and warning for invalid file."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json")
        conventions, warnings = conventions_repo.load_or_default(bad_file)
        assert conventions.file_naming.pattern == "{TYPE}-{VERSION}-{DESCRIPTION}"
        assert len(warnings) == 1
        assert "Invalid" in warnings[0]


class TestSaveConventions:
    """Tests for save_conventions method."""

    def test_save_conventions_creates_file(
        self,
        conventions_repo: ConventionsRepository,
        tmp_path: Path,
    ) -> None:
        """Test save_conventions creates file."""
        conventions = ConventionsSchema.get_default()
        path = tmp_path / ".apm" / "conventions.json"
        conventions_repo.save_conventions(path, conventions)
        assert path.exists()

    def test_save_conventions_round_trip(
        self,
        conventions_repo: ConventionsRepository,
        tmp_path: Path,
    ) -> None:
        """Test saved conventions can be loaded back."""
        original = ConventionsSchema.get_default()
        path = tmp_path / "conventions.json"
        conventions_repo.save_conventions(path, original)
        loaded = conventions_repo.load_conventions(path)
        assert loaded.file_naming.pattern == original.file_naming.pattern
