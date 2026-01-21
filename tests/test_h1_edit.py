import json
from pathlib import Path

import pytest

from models.registry_schema import RegistrySchema
from repositories.registry_repository import RegistryRepository
from services.registry_service import RegistryService, ARCHIVE_DIR


@pytest.fixture
def tmp_repo_structure(tmp_path: Path) -> Path:
    """Create a temporary repository structure with test files."""
    # Create directories
    (tmp_path / "core").mkdir()
    (tmp_path / "platform" / "python").mkdir(parents=True)
    (tmp_path / "workflows").mkdir()
    (tmp_path / ARCHIVE_DIR).mkdir()

    # Create test content
    (tmp_path / "core" / "GUIDE-1-2-General.md").write_text(
        "# General Coding Conventions\n\nSome content here.",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def empty_registry_path(tmp_path: Path) -> Path:
    """Create an empty registry.json file."""
    registry_path = tmp_path / "registry.json"
    registry_data = {"version": "1.0", "ingredients": {}}
    registry_path.write_text(json.dumps(registry_data), encoding="utf-8")
    return registry_path


@pytest.fixture
def registry_service(
    tmp_repo_structure: Path,
    empty_registry_path: Path,
) -> RegistryService:
    """Create a RegistryService instance for testing."""
    repo = RegistryRepository()
    return RegistryService(
        registry_repository=repo,
        registry_path=empty_registry_path,
        repo_root=tmp_repo_structure,
    )


class TestUpdateSkillH1:
    """Tests for update_skill_h1 method."""

    def test_update_skill_h1_simple(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test replacing an existing H1 heading."""
        path = Path("core/GUIDE-1-2-General.md")
        registry_service.add_skill(path)

        success = registry_service.update_skill_h1("GUIDE-1-2-General", "New General Guide")

        assert success is True
        
        # Verify file content
        content = (tmp_repo_structure / path).read_text(encoding="utf-8")
        assert "# New General Guide" in content
        assert "# General Coding Conventions" not in content
        
        # Verify registry update
        skill = registry_service.get_skill("GUIDE-1-2-General")
        assert skill is not None
        assert skill.description == "New General Guide"

    def test_update_skill_h1_inserts_new(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test inserting H1 when none exists."""
        # Create file without H1
        path = tmp_repo_structure / "core" / "GUIDE-0-0-NoH1.md"
        path.write_text("Just some content.\n", encoding="utf-8")
        
        rel_path = Path("core/GUIDE-0-0-NoH1.md")
        registry_service.add_skill(rel_path)

        success = registry_service.update_skill_h1("GUIDE-0-0-NoH1", "Added Title")

        assert success is True
        content = path.read_text(encoding="utf-8")
        assert content.startswith("# Added Title\n")
        assert "Just some content" in content

    def test_update_skill_h1_with_frontmatter(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test replacing H1 when file has frontmatter."""
        path = tmp_repo_structure / "core" / "GUIDE-1-0-Frontmatter.md"
        path.write_text(
            "---\ntype: GUIDE\n---\n\n# Old Title\n\nContent.", 
            encoding="utf-8"
        )
        
        rel_path = Path("core/GUIDE-1-0-Frontmatter.md")
        registry_service.add_skill(rel_path)

        success = registry_service.update_skill_h1("GUIDE-1-0-Frontmatter", "New Title")

        assert success is True
        content = path.read_text(encoding="utf-8")
        assert "---\ntype: GUIDE\n---\n" in content
        assert "# New Title" in content
        assert "# Old Title" not in content

    def test_update_skill_h1_inserts_after_frontmatter(
        self,
        registry_service: RegistryService,
        tmp_repo_structure: Path,
    ) -> None:
        """Test inserting H1 after frontmatter when missing."""
        path = tmp_repo_structure / "core" / "GUIDE-1-0-FrontmatterNoH1.md"
        path.write_text(
            "---\ntype: GUIDE\n---\n\nContent.", 
            encoding="utf-8"
        )
        
        rel_path = Path("core/GUIDE-1-0-FrontmatterNoH1.md")
        registry_service.add_skill(rel_path)

        success = registry_service.update_skill_h1("GUIDE-1-0-FrontmatterNoH1", "Inserted Title")

        assert success is True
        content = path.read_text(encoding="utf-8")
        # Should be inserted after frontmatter
        lines = content.splitlines()
        assert lines[0] == "---"
        assert lines[2] == "---"
        # Index 3 might be empty line
        assert "# Inserted Title" in content

    def test_update_skill_h1_not_found(
        self,
        registry_service: RegistryService,
    ) -> None:
        """Test updating non-existent skill returns False."""
        success = registry_service.update_skill_h1("NonExistent", "New Title")
        assert success is False
