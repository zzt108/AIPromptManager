import pytest
from pathlib import Path
from services.registry_service import RegistryService
from repositories.registry_repository import RegistryRepository
from models.skill import Skill
from models.skill_status import SkillStatus


class TestRenameSuggestions:

    @pytest.fixture
    def setup_service(self, tmp_path: Path) -> tuple[RegistryService, Path]:
        repo_root = tmp_path
        registry_path = tmp_path / "registry.json"

        # Mock repository (simple in-memory)
        registry_repo = RegistryRepository()

        service = RegistryService(
            registry_repository=registry_repo,
            registry_path=registry_path,
            repo_root=repo_root,
            naming_service=None,
        )
        return service, repo_root

    def create_skill(self, root: Path, name: str, content: str) -> Skill:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        return Skill(
            name=path.stem,
            path=Path(name),
            description="Test",
            type="Uncategorized",
            major=0,
            minor=0,
            basename=path.stem,
            status=SkillStatus.UNRECOGNIZED,
        )

    def test_suggestion_from_h1(
        self, setup_service: tuple[RegistryService, Path]
    ) -> None:
        service, root = setup_service
        skill = self.create_skill(
            root, "random_file.md", "# Setup Guide\n\nSome content"
        )

        suggestions = service.generate_rename_suggestions(skill)

        # Should have H1 and Stem suggestions
        # H1: SetupGuide
        # Stem: RandomFile

        # Find H1 suggestion
        h1_sugg = next((s for s in suggestions if s["source"] == "H1 Heading"), None)
        assert h1_sugg is not None
        assert h1_sugg["basename"] == "SetupGuide"
        assert (
            h1_sugg["type"] == "GUIDE"
        )  # Defaulted because current type is Uncategorized

    def test_suggestion_from_yaml(
        self, setup_service: tuple[RegistryService, Path]
    ) -> None:
        service, root = setup_service
        yaml_content = """---
type: PROMPT
version: 2.1
name: "Awesome Generator"
---
# Ignored H1
"""
        skill = self.create_skill(root, "bad-name.md", yaml_content)

        suggestions = service.generate_rename_suggestions(skill)

        # Check for YAML suggestion
        yaml_sugg = next(
            (s for s in suggestions if s["source"] == "YAML Frontmatter"), None
        )
        assert yaml_sugg is not None
        assert yaml_sugg["type"] == "PROMPT"
        assert yaml_sugg["major"] == 2
        assert yaml_sugg["minor"] == 1
        assert yaml_sugg["basename"] == "AwesomeGenerator"

    def test_suggestion_clean_stem(
        self, setup_service: tuple[RegistryService, Path]
    ) -> None:
        service, root = setup_service
        skill = self.create_skill(root, "my-cool_script.md", "No metadata")

        suggestions = service.generate_rename_suggestions(skill)

        # Check for Stem suggestion
        stem_sugg = next(
            (s for s in suggestions if s["source"] == "Cleaned Filename"), None
        )
        assert stem_sugg is not None
        assert stem_sugg["basename"] == "MyCoolScript"

    def test_yaml_uncategorized_type_defaults_to_guide(
        self, setup_service: tuple[RegistryService, Path]
    ) -> None:
        service, root = setup_service
        content = "---\ntype: Uncategorized\nname: Foo\n---"
        skill = self.create_skill(root, "test.md", content)

        suggestions = service.generate_rename_suggestions(skill)
        yaml_sugg = next(
            (s for s in suggestions if s["source"] == "YAML Frontmatter"), None
        )
        assert yaml_sugg is not None
        assert yaml_sugg["type"] == "GUIDE"  # Should default to GUIDE

    def test_h1_already_matches_stem_ignored(
        self, setup_service: tuple[RegistryService, Path]
    ) -> None:
        service, root = setup_service
        # If H1 is just "MyFile" and filename is "MyFile.md", H1 suggestion is redundant or filtered
        # Logic says: if h1_text != skill.path.stem

        skill = self.create_skill(root, "SetupGuide.md", "# SetupGuide")
        skill.type = "GUIDE"  # Matches context

        suggestions = service.generate_rename_suggestions(skill)

        # H1 "SetupGuide" == stem "SetupGuide" -> Strategy 1 skipped
        h1_sugg = next((s for s in suggestions if s["source"] == "H1 Heading"), None)
        assert h1_sugg is None

        # Should still have Cleaned Filename
        stem_sugg = next(
            (s for s in suggestions if s["source"] == "Cleaned Filename"), None
        )
        assert stem_sugg is not None
