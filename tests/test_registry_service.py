"""Tests for RegistryService."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from models.skill import Skill
from models.registry_schema import RegistrySchema
from repositories.registry_repository import RegistryRepository
from services.registry_service import RegistryService


@pytest.fixture
def tmp_repo_structure(tmp_path: Path) -> Path:
    """Create a temporary repository structure with test files.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to the temporary repository root
    """
    # Create directories
    (tmp_path / "core").mkdir()
    (tmp_path / "platform" / "python").mkdir(parents=True)
    (tmp_path / "workflows").mkdir()

    # Create test markdown files
    (tmp_path / "core" / "GUIDE-1-2-General.md").write_text(
        "# General Coding Conventions\n\nSome content here.",
        encoding="utf-8",
    )
    (tmp_path / "core" / "GUIDE-1-3-General.md").write_text(
        "# General Coding Conventions (Updated)\n\nNewer content.",
        encoding="utf-8",
    )
    (
        tmp_path / "platform" / "python" / "GUIDE-1-0-coding-convention-python.md"
    ).write_text(
        "# Python Coding Conventions\n\nPython-specific rules.",
        encoding="utf-8",
    )
    (tmp_path / "workflows" / "WORKFLOW-1-0-testing.md").write_text(
        "# Testing Workflow\n\nHow to run tests.",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture
def empty_registry_path(tmp_path: Path) -> Path:
    """Create an empty registry.json file.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to registry.json
    """
    registry_path = tmp_path / "registry.json"
    registry_data = {"version": "1.0", "ingredients": {}}
    registry_path.write_text(json.dumps(registry_data), encoding="utf-8")
    return registry_path


@pytest.fixture
def registry_service(
    tmp_repo_structure: Path,
    empty_registry_path: Path,
) -> RegistryService:
    """Create a RegistryService instance for testing.

    Args:
        tmp_repo_structure: Temporary repository with test files
        empty_registry_path: Path to empty registry

    Returns:
        Configured RegistryService
    """
    repo = RegistryRepository()
    return RegistryService(
        registry_repository=repo,
        registry_path=empty_registry_path,
        repo_root=tmp_repo_structure,
    )


class TestAddSkill:
    """Tests for add_skill method."""

    def test_add_skill_success(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test adding a valid Skill extracts metadata correctly."""
        path = Path("core/GUIDE-1-2-General.md")

        skill = registry_service.add_skill(path)

        assert skill.name == "GUIDE-1-2-General"
        assert skill.path == path
        assert skill.type == "GUIDE"
        assert skill.major == 1
        assert skill.minor == 2
        assert skill.basename == "General"
        assert skill.description == "General Coding Conventions"

    def test_add_skill_with_custom_description(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test adding Skill with explicit description."""
        path = Path("core/GUIDE-1-2-General.md")

        skill = registry_service.add_skill(path, description="Custom Description")

        assert skill.description == "Custom Description"

    def test_add_skill_duplicate_error(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test adding duplicate Skill raises ValueError."""
        path = Path("core/GUIDE-1-2-General.md")
        registry_service.add_skill(path)

        with pytest.raises(ValueError, match="already exists"):
            registry_service.add_skill(path)

    def test_add_skill_file_not_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test adding non-existent file raises FileNotFoundError."""
        path = Path("core/NONEXISTENT.md")

        with pytest.raises(FileNotFoundError):
            registry_service.add_skill(path)


class TestRemoveSkill:
    """Tests for remove_skill method."""

    def test_remove_skill_success(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test removing existing Skill."""
        path = Path("core/GUIDE-1-2-General.md")
        registry_service.add_skill(path)

        registry_service.remove_skill("GUIDE-1-2-General")

        assert registry_service.get_skill("GUIDE-1-2-General") is None

    def test_remove_skill_not_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test removing non-existent Skill raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            registry_service.remove_skill("nonexistent")


class TestGetSkill:
    """Tests for get_skill method."""

    def test_get_skill_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test retrieving existing Skill."""
        path = Path("core/GUIDE-1-2-General.md")
        registry_service.add_skill(path)

        skill = registry_service.get_skill("GUIDE-1-2-General")

        assert skill is not None
        assert skill.name == "GUIDE-1-2-General"

    def test_get_skill_not_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test retrieving non-existent Skill returns None."""
        skill = registry_service.get_skill("nonexistent")

        assert skill is None


class TestListAll:
    """Tests for list_all method."""

    def test_list_all_empty(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test listing empty registry."""
        Skills = registry_service.list_all()

        assert Skills == []

    def test_list_all_multiple(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test listing multiple Skills sorted by name."""
        registry_service.add_skill(Path("core/GUIDE-1-2-General.md"))
        registry_service.add_skill(
            Path("platform/python/GUIDE-1-0-coding-convention-python.md")
        )

        Skills = registry_service.list_all()

        assert len(Skills) == 2
        # Should be sorted alphabetically
        assert Skills[0].name == "GUIDE-1-0-coding-convention-python"
        assert Skills[1].name == "GUIDE-1-2-General"


class TestUpdateSkillPath:
    """Tests for update_skill_path method."""

    def test_update_skill_path_success(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test updating Skill path."""
        old_path = Path("core/GUIDE-1-2-General.md")
        new_path = Path("core/GUIDE-1-3-General.md")
        registry_service.add_skill(old_path)

        registry_service.update_skill_path("GUIDE-1-2-General", new_path)

        skill = registry_service.get_skill("GUIDE-1-2-General")
        assert skill is not None
        assert skill.path == new_path

    def test_update_skill_path_not_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test updating path for non-existent Skill."""
        with pytest.raises(KeyError, match="not found"):
            registry_service.update_skill_path("nonexistent", Path("some/path.md"))

    def test_update_skill_path_new_path_missing(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test updating to non-existent path raises FileNotFoundError."""
        registry_service.add_skill(Path("core/GUIDE-1-2-General.md"))

        with pytest.raises(FileNotFoundError):
            registry_service.update_skill_path(
                "GUIDE-1-2-General", Path("missing/path.md")
            )


class TestExtractMetadata:
    """Tests for _extract_metadata method."""

    def test_extract_metadata_versioned(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test extracting metadata from versioned filename."""
        path = Path("core/GUIDE-1-2-General.md")

        type_, major, minor, basename = registry_service._extract_metadata(path)

        assert type_ == "GUIDE"
        assert major == 1
        assert minor == 2
        assert basename == "General"

    def test_extract_metadata_versionless(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test extracting metadata from version-less filename."""
        # Create a version-less file
        versionless_file = tmp_repo_structure / "core" / "GUIDE--General.md"
        versionless_file.write_text("# General Guide\n", encoding="utf-8")

        path = Path("core/GUIDE--General.md")
        type_, major, minor, basename = registry_service._extract_metadata(path)

        assert type_ == "GUIDE"
        assert major == 0
        assert minor == 0
        assert basename == "General"

    def test_extract_metadata_invalid_pattern(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test invalid filename pattern raises ValueError."""
        path = Path("core/README.md")

        with pytest.raises(ValueError, match="doesn't match"):
            registry_service._extract_metadata(path)

    def test_extract_metadata_mixed_case(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test extracting metadata with mixed case type and suffixes."""
        path = Path("core/GuideCC-1-0-CodingConvention.md")

        type_, major, minor, basename = registry_service._extract_metadata(path)

        assert type_ == "GuideCC"
        assert major == 1
        assert minor == 0
        assert basename == "CodingConvention"


class TestExtractH1Heading:
    """Tests for _extract_h1_heading method."""

    def test_extract_h1_heading_success(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test extracting H1 heading from markdown."""
        path = tmp_repo_structure / "core" / "GUIDE-1-2-General.md"

        heading = registry_service._extract_h1_heading(path)

        assert heading == "General Coding Conventions"

    def test_extract_h1_heading_no_heading(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test fallback to filename when no H1 found."""
        # Create file without H1
        no_h1_file = tmp_repo_structure / "core" / "GUIDE-1-0-NoHeading.md"
        no_h1_file.write_text("No heading here.\n", encoding="utf-8")

        heading = registry_service._extract_h1_heading(no_h1_file)

        assert heading == "GUIDE-1-0-NoHeading"


class TestRefreshRegistry:
    """Tests for refresh_registry method."""

    def test_refresh_registry_adds_new(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test refresh adds new files to registry."""
        result = registry_service.refresh_registry(["core"])

        assert result.added == 2  # GUIDE-1-2-General and GUIDE-1-3-General
        assert result.updated == 0
        assert result.removed == 0

    def test_refresh_registry_multiple_directories(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test refresh scans multiple directories."""
        result = registry_service.refresh_registry(
            ["core", "platform/python", "workflows"]
        )

        # 2 in core + 1 in platform/python + 1 in workflows = 4
        assert result.added == 4

    def test_refresh_registry_missing_directory(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test refresh handles missing directory gracefully."""
        result = registry_service.refresh_registry(["nonexistent"])

        assert result.added == 0
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]

    def test_refresh_registry_removes_deleted(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test refresh removes files that were deleted from disk."""
        # 1. Add an Skill initially
        path = Path("core/GUIDE-1-2-General.md")
        registry_service.add_skill(path)

        # 2. Delete the file from disk
        (tmp_repo_structure / path).unlink()

        # 3. Refresh registry
        result = registry_service.refresh_registry(["core"])

        # 4. Verify removal
        assert result.removed == 1
        assert registry_service.get_skill("GUIDE-1-2-General") is None


class TestVersionLookup:
    """Tests for version lookup methods."""

    def test_find_skills_by_basename(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test finding all versions of an Skill."""
        registry_service.add_skill(Path("core/GUIDE-1-2-General.md"))
        registry_service.add_skill(Path("core/GUIDE-1-3-General.md"))

        matches = registry_service.find_skills_by_basename("General")

        assert len(matches) == 2
        # Should be sorted by version descending
        assert matches[0].minor == 3
        assert matches[1].minor == 2

    def test_get_latest_version(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test getting latest version of an Skill."""
        registry_service.add_skill(Path("core/GUIDE-1-2-General.md"))
        registry_service.add_skill(Path("core/GUIDE-1-3-General.md"))

        latest = registry_service.get_latest_version("General")

        assert latest is not None
        assert latest.minor == 3

    def test_get_latest_version_not_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test getting latest version for non-existent basename."""
        latest = registry_service.get_latest_version("Nonexistent")

        assert latest is None


class TestRenameSkill:
    """Tests for rename_skill method."""

    def test_rename_skill_success(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test renaming an Skill successfully."""
        # 1. Setup initial Skill
        old_path = Path("core/GUIDE-1-2-General.md")
        registry_service.add_skill(old_path)

        # 2. Rename it
        registry_service.rename_skill(
            current_name="GUIDE-1-2-General",
            new_basename="RenamedGeneral",
            new_type="GUIDE",
            new_major=1,
            new_minor=3,
        )

        # 3. Verify old file gone, new file exists
        assert not (tmp_repo_structure / old_path).exists()
        new_path = tmp_repo_structure / "core/GUIDE-1-3-RenamedGeneral.md"
        assert new_path.exists()

        # 4. Verify registry updated
        assert registry_service.get_skill("GUIDE-1-2-General") is None
        new_ing = registry_service.get_skill("GUIDE-1-3-RenamedGeneral")
        assert new_ing is not None
        assert new_ing.basename == "RenamedGeneral"

    def test_rename_skill_not_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test renaming non-existent Skill raises KeyError."""
        with pytest.raises(KeyError):
            registry_service.rename_skill("nonexistent", "New", "GUIDE", 1, 0)

    def test_rename_skill_collision(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test renaming to existing filename raises ValueError."""
        path1 = Path("core/GUIDE-1-2-General.md")
        path2 = Path("core/GUIDE-1-3-Target.md")
        # Create second file first
        (tmp_repo_structure / path2).write_text("Target", encoding="utf-8")

        registry_service.add_skill(path1)
        registry_service.add_skill(path2)

        # Try to rename first to match second
        with pytest.raises(ValueError, match="already exists"):
            registry_service.rename_skill(
                current_name="GUIDE-1-2-General",
                new_basename="Target",
                new_type="GUIDE",
                new_major=1,
                new_minor=3,
            )

    def test_rename_skill_same_name_noop(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test renaming to same name works (no-op on file, refresh registry)."""
        path = Path("core/GUIDE-1-2-General.md")
        registry_service.add_skill(path)

        # Rename to same
        registry_service.rename_skill(
            current_name="GUIDE-1-2-General",
            new_basename="General",
            new_type="GUIDE",
            new_major=1,
            new_minor=2,
        )

        assert (tmp_repo_structure / path).exists()
        assert registry_service.get_skill("GUIDE-1-2-General") is not None
