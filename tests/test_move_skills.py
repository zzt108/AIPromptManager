"""Tests for Move Skills feature."""

import shutil
from pathlib import Path
from unittest.mock import Mock

import pytest
from services.registry_service import RegistryService
from models.skill_status import SkillStatus
from models.skill import Skill


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a temp repo structure."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "core").mkdir()
    (repo / "platform").mkdir()
    (repo / ".archive").mkdir()
    return repo


@pytest.fixture
def service(temp_repo: Path) -> RegistryService:
    """Create a registry service instance."""
    mock_repo = Mock()
    # Mock load_registry to return basic structure with empty skills dict initially
    # We'll populate it in tests
    mock_registry_schema = Mock()
    mock_registry_schema.skills = {}
    mock_repo.load_registry.return_value = mock_registry_schema

    svc = RegistryService(
        registry_repository=mock_repo,
        registry_path=temp_repo / "registry.json",
        repo_root=temp_repo,
    )
    # Inject our mock registry into the service cache
    svc._registry = mock_registry_schema
    return svc


def test_move_skill_basic(service: RegistryService, temp_repo: Path) -> None:
    """Test moving a skill from one folder to another."""
    # Setup
    skill_file = temp_repo / "core" / "test-skill.md"
    skill_file.write_text("# Test Skill")

    skill = Skill(
        name="test-skill",
        path=Path("core/test-skill.md"),
        description="Test Skill",
        type="test",
        major=1,
        minor=0,
        basename="skill",
        is_enabled=True,
        status=SkillStatus.VALID,
        status_detail=None,
        modified_at=100.0,
    )
    service._load_registry().skills["test-skill"] = skill

    # Execute
    moved = service.move_skills(["test-skill"], "platform")

    # Verify
    assert moved == 1
    assert not (temp_repo / "core" / "test-skill.md").exists()
    assert (temp_repo / "platform" / "test-skill.md").exists()

    # Check registry update
    updated_skill = service._load_registry().skills["test-skill"]
    assert updated_skill.path == Path("platform/test-skill.md")
    assert updated_skill.status == SkillStatus.VALID


def test_move_to_archive(service: RegistryService, temp_repo: Path) -> None:
    """Test moving a skill to Archive folder updates status."""
    # Setup
    skill_file = temp_repo / "core" / "test-archive.md"
    skill_file.write_text("# Test Archive")

    skill = Skill(
        name="test-archive",
        path=Path("core/test-archive.md"),
        description="Test Archive",
        type="test",
        major=1,
        minor=0,
        basename="archive",
        is_enabled=True,
        status=SkillStatus.VALID,
        status_detail=None,
        modified_at=100.0,
    )
    service._load_registry().skills["test-archive"] = skill

    # Execute move to .archive
    moved = service.move_skills(["test-archive"], ".archive")

    # Verify
    assert moved == 1
    assert not (temp_repo / "core" / "test-archive.md").exists()
    assert (temp_repo / ".archive" / "test-archive.md").exists()

    # Check registry status
    updated_skill = service._load_registry().skills["test-archive"]
    assert updated_skill.path == Path(".archive/test-archive.md")
    assert updated_skill.status == SkillStatus.ARCHIVED
    assert not updated_skill.is_enabled


def test_move_from_archive(service: RegistryService, temp_repo: Path) -> None:
    """Test moving a skill from Archive folder restores status."""
    # Setup
    skill_file = temp_repo / ".archive" / "test-restore.md"
    skill_file.write_text("# Test Restore")

    skill = Skill(
        name="test-restore",
        path=Path(".archive/test-restore.md"),
        description="Test Restore",
        type="test",
        major=1,
        minor=0,
        basename="restore",
        is_enabled=False,
        status=SkillStatus.ARCHIVED,
        status_detail=None,
        modified_at=100.0,
    )
    service._load_registry().skills["test-restore"] = skill

    # Execute move back to core
    moved = service.move_skills(["test-restore"], "core")

    # Verify
    assert moved == 1
    assert not (temp_repo / ".archive" / "test-restore.md").exists()
    assert (temp_repo / "core" / "test-restore.md").exists()

    # Check registry status
    updated_skill = service._load_registry().skills["test-restore"]
    assert updated_skill.path == Path("core/test-restore.md")
    assert updated_skill.status == SkillStatus.VALID
    # Enabled state remains False as per logic
    assert not updated_skill.is_enabled


def test_move_collision(service: RegistryService, temp_repo: Path) -> None:
    """Test move fails safely if destination exists."""
    # Setup
    (temp_repo / "core" / "collision.md").write_text("Source")
    (temp_repo / "platform" / "collision.md").write_text("Dest")

    skill = Skill(
        name="collision",
        path=Path("core/collision.md"),
        description="Collision",
        type="test",
        major=1,
        minor=0,
        basename="collision",
        is_enabled=True,
        status=SkillStatus.VALID,
        status_detail=None,
        modified_at=100.0,
    )
    service._load_registry().skills["collision"] = skill

    # Execute
    moved = service.move_skills(["collision"], "platform")

    # Verify
    assert moved == 0
    assert (temp_repo / "core" / "collision.md").exists()
    assert (temp_repo / "platform" / "collision.md").exists()
    assert (temp_repo / "core" / "collision.md").read_text() == "Source"
