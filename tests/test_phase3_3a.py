import pytest
from pathlib import Path
from services.registry_service import RegistryService
from repositories.registry_repository import RegistryRepository
from models.skill_status import SkillStatus


class TestIntelligentExtraction:

    @pytest.fixture
    def setup_service(self, tmp_path):
        repo_root = tmp_path
        registry_path = tmp_path / "registry.json"

        registry_repo = RegistryRepository()
        service = RegistryService(
            registry_repository=registry_repo,
            registry_path=registry_path,
            repo_root=repo_root,
            naming_service=None,
        )
        return service, repo_root

    def test_refresh_tracks_unrecognized_file(self, setup_service):
        service, repo_root = setup_service

        # Create an invalid file
        (repo_root / "professions").mkdir()
        invalid_file = repo_root / "professions" / "random_notes.md"
        invalid_file.write_text("# My random notes", encoding="utf-8")

        # Refresh
        result = service.refresh_registry(["professions"])

        # Verify
        assert result.added == 1
        assert result.errors == []  # Should NOT be an error now

        # Verify skill in registry
        # The skill name derived from 'random_notes.md' should be 'random_notes'
        skill = service.get_skill("random_notes")
        assert skill is not None
        assert skill.status == SkillStatus.UNRECOGNIZED
        assert skill.status_detail is not None
        assert "Pattern mismatch" in skill.status_detail

    def test_refresh_tracks_valid_file(self, setup_service):
        service, repo_root = setup_service

        # Create a valid file
        (repo_root / "professions").mkdir(exist_ok=True)
        # Using legacy pattern TYPE-MAJOR-MINOR-Basename.md
        valid_file = repo_root / "professions" / "GUIDE-1-0-Setup.md"
        valid_file.write_text("# Setup Guide", encoding="utf-8")

        # Refresh
        result = service.refresh_registry(["professions"])

        # Verify
        assert result.added == 1

        # Verify skill
        # _derive_skill_name uses path.stem -> "GUIDE-1-0-Setup" ??
        # Wait, let's check _derive_skill_name implementation again.
        # It calls path.stem.
        # So name is "GUIDE-1-0-Setup".

        # But wait, lines 23-26 define _VERSIONED_PATTERN with groups.
        # But _derive_skill_name is simple.
        # In the original file:
        # 533:    def _derive_skill_name(self, path: Path) -> str:
        # 544:        return path.stem
        # So yes, the name in registry is the filename stem.

        skill = service.get_skill("GUIDE-1-0-Setup")
        assert skill is not None
        assert skill.status == SkillStatus.VALID
        assert skill.status_detail is None

    def test_intelligent_extraction_defaults(self, setup_service):
        # Verification of the _extract_metadata_intelligently method directly
        service, _ = setup_service
        path = Path("some/weird/file.md")

        t, M, m, b, status, detail = service._extract_metadata_intelligently(path)

        assert status == SkillStatus.PARSE_ERROR  # File doesn't exist
        assert b == "file"
        assert t == "Uncategorized"
