"""Tests for archive/restore functionality in RegistryService."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from services.registry_service import RegistryService, ARCHIVE_DIR
from models.skill_status import SkillStatus
from repositories.registry_repository import RegistryRepository


@pytest.fixture
def tmp_repo_archive(tmp_path: Path) -> Path:
    """Create a temporary repository structure for archive tests."""
    (tmp_path / "core").mkdir()
    (tmp_path / "core" / "GUIDE-1-0-Test.md").write_text(
        "# Test Guide", encoding="utf-8"
    )
    (tmp_path / "core" / "GUIDE-1-1-Test2.md").write_text(
        "# Test Guide 2", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def registry_service(tmp_repo_archive: Path) -> RegistryService:
    """Create a RegistryService instance for testing."""
    repo = RegistryRepository()
    registry_path = tmp_repo_archive / "registry.json"
    registry_path.write_text(
        json.dumps({"version": "1.0", "ingredients": {}}), encoding="utf-8"
    )
    service = RegistryService(repo, registry_path, tmp_repo_archive)

    # Add skills to registry
    service.add_skill(Path("core/GUIDE-1-0-Test.md"))
    service.add_skill(Path("core/GUIDE-1-1-Test2.md"))
    return service


def test_archive_skill_success(
    registry_service: RegistryService, tmp_repo_archive: Path
) -> None:
    """Test archiving a single skill successfully."""
    skill_name = "GUIDE-1-0-Test"
    count = registry_service.archive_skills([skill_name])

    assert count == 1

    # Verify file moved
    original_path = tmp_repo_archive / "core/GUIDE-1-0-Test.md"
    archive_path = tmp_repo_archive / ARCHIVE_DIR / "core/GUIDE-1-0-Test.md"

    assert not original_path.exists()
    assert archive_path.exists()

    # Verify registry updated
    skill = registry_service.get_skill(skill_name)
    assert skill is not None
    assert skill.status == SkillStatus.ARCHIVED
    assert not skill.is_enabled
    assert skill.path == Path(f"{ARCHIVE_DIR}/core/GUIDE-1-0-Test.md")


def test_restore_skill_success(
    registry_service: RegistryService, tmp_repo_archive: Path
) -> None:
    """Test restoring an archived skill successfully."""
    skill_name = "GUIDE-1-0-Test"
    registry_service.archive_skills([skill_name])

    # Restore
    count = registry_service.restore_skills([skill_name])
    assert count == 1

    # Verify file moved back
    original_path = tmp_repo_archive / "core/GUIDE-1-0-Test.md"
    archive_path = tmp_repo_archive / ARCHIVE_DIR / "core/GUIDE-1-0-Test.md"

    assert original_path.exists()
    assert not archive_path.exists()

    # Verify registry updated
    skill = registry_service.get_skill(skill_name)
    assert skill is not None
    assert skill.status == SkillStatus.VALID
    assert not skill.is_enabled
    assert skill.path == Path("core/GUIDE-1-0-Test.md")


def test_archive_destination_exists(
    registry_service: RegistryService, tmp_repo_archive: Path
) -> None:
    """Test archiving fails if destination file already exists."""
    skill_name = "GUIDE-1-0-Test"

    # Manually create the destination file
    archive_path = tmp_repo_archive / ARCHIVE_DIR / "core/GUIDE-1-0-Test.md"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text("Existing content")

    count = registry_service.archive_skills([skill_name])

    assert count == 0
    assert (tmp_repo_archive / "core/GUIDE-1-0-Test.md").exists()
    assert registry_service.get_skill(skill_name).status == SkillStatus.VALID


def test_restore_destination_exists(
    registry_service: RegistryService, tmp_repo_archive: Path
) -> None:
    """Test restoring fails if destination file already exists."""
    skill_name = "GUIDE-1-0-Test"
    registry_service.archive_skills([skill_name])

    # Manually recreate the original file
    (tmp_repo_archive / "core/GUIDE-1-0-Test.md").write_text("New content")

    count = registry_service.restore_skills([skill_name])

    assert count == 0
    assert (tmp_repo_archive / ARCHIVE_DIR / "core/GUIDE-1-0-Test.md").exists()
    assert registry_service.get_skill(skill_name).status == SkillStatus.ARCHIVED


def test_archive_nonexistent_skill(registry_service: RegistryService) -> None:
    """Test archiving specific non-existent skill does nothing."""
    count = registry_service.archive_skills(["NONEXISTENT"])
    assert count == 0


def test_restore_nonexistent_skill(registry_service: RegistryService) -> None:
    """Test restoring non-existent skill does nothing."""
    count = registry_service.restore_skills(["NONEXISTENT"])
    assert count == 0


def test_restore_not_archived_skill(registry_service: RegistryService) -> None:
    """Test restoring a skill that is not archived does nothing."""
    skill_name = "GUIDE-1-0-Test"  # currently valid
    count = registry_service.restore_skills([skill_name])
    assert count == 0
    assert registry_service.get_skill(skill_name).status == SkillStatus.VALID
