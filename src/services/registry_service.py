"""Registry service for AI Prompt Manager business logic."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from models.conventions_schema import ConventionsSchema
from models.skill import Skill
from models.registry_schema import RegistrySchema
from models.service_results import RefreshResult

if TYPE_CHECKING:
    from repositories.registry_repository import RegistryRepository
    from services.naming_service import NamingService

logger = structlog.get_logger()

# Legacy patterns for backward compatibility when no NamingService provided
_VERSIONED_PATTERN = re.compile(
    r"^(?P<type>[a-zA-Z0-9_]+)-(?P<major>\d+)-(?P<minor>\d+)-(?P<basename>.+)\.md$"
)
_VERSIONLESS_PATTERN = re.compile(r"^(?P<type>[a-zA-Z0-9_]+)--(?P<basename>.+)\.md$")


class RegistryService:
    """Business logic for registry operations.

    Provides CRUD operations on skills and registry refresh functionality.
    Uses constructor injection for testability.

    Attributes:
        registry_repository: Repository for registry persistence
        registry_path: Path to registry.json file
        repo_root: Root path of the AI Prompts repository
    """

    def __init__(
        self,
        registry_repository: RegistryRepository,
        registry_path: Path,
        repo_root: Path,
        naming_service: NamingService | None = None,
    ) -> None:
        """Initialize registry service.

        Args:
            registry_repository: Repository for loading/saving registry
            registry_path: Path to registry.json
            repo_root: Root path of the repository for relative paths
            naming_service: Optional NamingService for filename parsing.
                           If None, uses legacy hardcoded patterns.
        """
        self.registry_repository = registry_repository
        self.registry_path = registry_path
        self.repo_root = repo_root
        self.naming_service = naming_service
        self._registry: RegistrySchema | None = None

    def _load_registry(self) -> RegistrySchema:
        """Load registry from file, caching the result.

        Returns:
            Loaded RegistrySchema
        """
        if self._registry is None:
            if self.registry_path.exists():
                self._registry = self.registry_repository.load_registry(
                    self.registry_path
                )
            else:
                # Create empty registry if file doesn't exist
                self._registry = RegistrySchema(version="1.0", skills={})
        return self._registry

    def _save_registry(self) -> None:
        """Save current registry state to file."""
        if self._registry is not None:
            self.registry_repository.save_registry(self.registry_path, self._registry)

    def _invalidate_cache(self) -> None:
        """Invalidate the cached registry to force reload."""
        self._registry = None

    def add_skill(
        self,
        path: Path,
        description: str | None = None,
    ) -> Skill:
        """Add a new skill to the registry.

        Extracts metadata (type, version, basename) from the filename.
        If description is None, extracts H1 heading from markdown file.

        Args:
            path: Path to the skill file (relative to repo_root)
            description: Optional description (extracted from H1 if None)

        Returns:
            The created Skill

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If skill already exists or filename is invalid
        """
        absolute_path = self.repo_root / path

        if not absolute_path.exists():
            logger.error("skill_file_not_found", path=str(path))
            raise FileNotFoundError(f"Skill file not found: {path}")

        # Extract metadata from filename
        skill_type, major, minor, basename = self._extract_metadata(path)

        # Derive skill name from path
        name = self._derive_skill_name(path)

        # Check for duplicates
        registry = self._load_registry()
        if name in registry.skills:
            logger.warning("skill_already_exists", name=name)
            raise ValueError(f"Skill already exists: {name}")

        # Extract description from H1 if not provided
        if description is None:
            description = self._extract_h1_heading(absolute_path)

        # Create skill
        skill = Skill(
            name=name,
            path=path,
            description=description,
            type=skill_type,
            major=major,
            minor=minor,
            basename=basename,
        )

        # Add to registry and save
        registry.skills[name] = skill
        self._save_registry()

        logger.info(
            "skill_added",
            name=name,
            path=str(path),
            type=skill_type,
            version=f"{major}.{minor}",
        )

        return skill

    def remove_skill(self, name: str) -> None:
        """Remove a skill from the registry.

        Args:
            name: Name of the skill to remove

        Raises:
            KeyError: If skill doesn't exist
        """
        registry = self._load_registry()

        if name not in registry.skills:
            logger.error("skill_not_found", name=name)
            raise KeyError(f"Skill not found: {name}")

        del registry.skills[name]
        self._save_registry()

        logger.info("skill_removed", name=name)

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name.

        Args:
            name: Name of the skill

        Returns:
            Skill if found, None otherwise
        """
        registry = self._load_registry()
        return registry.skills.get(name)

    def list_all(self) -> list[Skill]:
        """List all skills in the registry.

        Returns:
            List of all skills, sorted by name
        """
        registry = self._load_registry()
        return sorted(
            registry.skills.values(),
            key=lambda i: i.name,
        )

    def list_enabled(self) -> list[Skill]:
        """List only enabled skills (visible in Profession Designer).

        Returns:
            List of enabled skills, sorted by name
        """
        return [skill for skill in self.list_all() if skill.is_enabled]

    def set_skill_enabled(self, name: str, enabled: bool) -> None:
        """Set the enabled/hidden state for a single skill.

        Args:
            name: Name of the skill
            enabled: True to enable (show), False to hide

        Raises:
            KeyError: If skill doesn't exist
        """
        registry = self._load_registry()

        if name not in registry.skills:
            logger.error("skill_not_found", name=name)
            raise KeyError(f"Skill not found: {name}")

        old = registry.skills[name]
        registry.skills[name] = Skill(
            name=old.name,
            path=old.path,
            description=old.description,
            type=old.type,
            major=old.major,
            minor=old.minor,
            basename=old.basename,
            is_enabled=enabled,
        )
        self._save_registry()

        action = "enabled" if enabled else "hidden"
        logger.info("skill_visibility_changed", name=name, action=action)

    def set_skills_enabled(self, names: list[str], enabled: bool) -> int:
        """Set the enabled/hidden state for multiple skills.

        Args:
            names: List of skill names to update
            enabled: True to enable (show), False to hide

        Returns:
            Number of skills actually updated
        """
        registry = self._load_registry()
        updated = 0

        for name in names:
            if name not in registry.skills:
                logger.warning("skill_not_found_during_bulk", name=name)
                continue

            old = registry.skills[name]
            if old.is_enabled != enabled:
                registry.skills[name] = Skill(
                    name=old.name,
                    path=old.path,
                    description=old.description,
                    type=old.type,
                    major=old.major,
                    minor=old.minor,
                    basename=old.basename,
                    is_enabled=enabled,
                )
                updated += 1

        if updated > 0:
            self._save_registry()
            action = "enabled" if enabled else "hidden"
            logger.info("bulk_visibility_changed", count=updated, action=action)

        return updated

    def update_skill_path(self, name: str, new_path: Path) -> None:
        """Update the path for an existing skill.

        Args:
            name: Name of the skill to update
            new_path: New path for the skill

        Raises:
            KeyError: If skill doesn't exist
            FileNotFoundError: If new path doesn't exist
        """
        registry = self._load_registry()

        if name not in registry.skills:
            logger.error("skill_not_found", name=name)
            raise KeyError(f"Skill not found: {name}")

        absolute_path = self.repo_root / new_path
        if not absolute_path.exists():
            logger.error("new_path_not_found", path=str(new_path))
            raise FileNotFoundError(f"New path doesn't exist: {new_path}")

        # Update the skill
        old_skill = registry.skills[name]
        registry.skills[name] = Skill(
            name=old_skill.name,
            path=new_path,
            description=old_skill.description,
            type=old_skill.type,
            major=old_skill.major,
            minor=old_skill.minor,
            basename=old_skill.basename,
            is_enabled=old_skill.is_enabled,
        )
        self._save_registry()

        logger.info(
            "skill_path_updated",
            name=name,
            old_path=str(old_skill.path),
            new_path=str(new_path),
        )

    def refresh_registry(
        self,
        scan_directories: list[str],
    ) -> RefreshResult:
        """Scan directories and sync registry with filesystem.

        Adds new files found in scan directories, updates paths for
        moved files, and flags removed files.

        Args:
            scan_directories: List of directory names to scan
                             (relative to repo_root)

        Returns:
            RefreshResult with counts of added/updated/removed items
        """
        result = RefreshResult()
        registry = self._load_registry()

        # Track files found during scan
        found_files: set[str] = set()

        for directory in scan_directories:
            dir_path = self.repo_root / directory
            if not dir_path.exists():
                result.errors.append(f"Directory not found: {directory}")
                continue

            # Scan for markdown files
            for md_file in dir_path.rglob("*.md"):
                relative_path = md_file.relative_to(self.repo_root)

                try:
                    name = self._derive_skill_name(relative_path)
                    found_files.add(name)

                    if name in registry.skills:
                        # Check if path changed
                        existing = registry.skills[name]
                        if existing.path != relative_path:
                            self.update_skill_path(name, relative_path)
                            result.updated += 1
                    else:
                        # Add new skill
                        self.add_skill(relative_path)
                        result.added += 1

                except ValueError as e:
                    # Invalid filename pattern, skip
                    result.errors.append(f"Skipped {relative_path}: {e}")

        # Check for removed files
        missing_skills = [name for name in registry.skills if name not in found_files]
        result.removed = len(missing_skills)

        # Log removed files and delete them
        for name in missing_skills:
            del registry.skills[name]
            logger.warning(
                "skill_removed_during_refresh",
                name=name,
            )

        if result.removed > 0 or result.added > 0 or result.updated > 0:
            self._save_registry()

        logger.info(
            "registry_refresh_complete",
            added=result.added,
            updated=result.updated,
            removed=result.removed,
            errors=len(result.errors),
        )

        return result

    def _extract_metadata(
        self,
        path: Path,
    ) -> tuple[str, int, int, str]:
        """Extract metadata from skill filename.

        Supports both versioned (TYPE-MAJOR-MINOR-Name.md) and
        version-less (TYPE--Name.md) patterns.

        Args:
            path: Path to the skill file

        Returns:
            Tuple of (type, major, minor, basename)

        Raises:
            ValueError: If filename doesn't match expected pattern
        """
        # Use naming service if available
        if self.naming_service is not None:
            return self.naming_service.extract_metadata(path)

        # Legacy fallback for backward compatibility
        filename = path.name

        # Try versioned pattern first
        match = _VERSIONED_PATTERN.match(filename)
        if match:
            return (
                match.group("type"),
                int(match.group("major")),
                int(match.group("minor")),
                match.group("basename"),
            )

        # Try version-less pattern
        match = _VERSIONLESS_PATTERN.match(filename)
        if match:
            return (
                match.group("type"),
                0,  # Version-less files have version 0.0
                0,
                match.group("basename"),
            )

        raise ValueError(f"Filename doesn't match expected pattern: {filename}")

    def _extract_h1_heading(self, path: Path) -> str:
        """Extract H1 heading from markdown file as description.

        Args:
            path: Absolute path to the markdown file

        Returns:
            H1 heading text, or filename if no H1 found
        """
        try:
            content = path.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("# "):
                    return line[2:].strip()
        except Exception:
            pass
        return path.stem

    def rename_skill(
        self,
        current_name: str,
        new_basename: str,
        new_type: str,
        new_major: int,
        new_minor: int,
    ) -> None:
        """Rename a skill file and update the registry.

        Args:
            current_name: Current name of the skill (key in registry)
            new_basename: New basename for the file
            new_type: New type (e.g., GUIDE, SPACE)
            new_major: New major version
            new_minor: New minor version

        Raises:
            KeyError: If skill not found
            ValueError: If new filename already exists or is invalid
            OSError: If rename operation fails
        """
        skill = self.get_skill(current_name)
        if not skill:
            raise KeyError(f"Skill not found: {current_name}")

        # Generate new filename
        if self.naming_service:
            new_filename = self.naming_service.make_versioned(
                basename=new_basename,
                major=new_major,
                minor=new_minor,
                type_str=new_type,
            )
        else:
            # Fallback using hardcoded pattern
            new_filename = f"{new_type}-{new_major}-{new_minor}-{new_basename}.md"

        old_path = self.repo_root / skill.path
        new_path = old_path.parent / new_filename

        if new_path.exists() and new_path != old_path:
            raise ValueError(f"File already exists: {new_filename}")

        # Rename file on disk
        try:
            old_path.rename(new_path)
            logger.info(
                "file_renamed",
                old=str(old_path),
                new=str(new_path),
            )
        except OSError as e:
            logger.error(
                "rename_failed",
                old=str(old_path),
                new=str(new_path),
                error=str(e),
            )
            raise

        # Force a refresh to update internal state
        # We need to scan the directory where the file lives.
        try:
            relative_dir = old_path.parent.relative_to(self.repo_root)
            self.refresh_registry([str(relative_dir)])
        except Exception as e:
            logger.error("registry_refresh_failed_after_rename", error=str(e))
            # We don't raise here because the rename succeeded on disk

    def _derive_skill_name(self, path: Path) -> str:
        """Derive skill name from file path.

        Uses the filename without extension as the skill name.

        Args:
            path: Path to the skill file

        Returns:
            Derived skill name
        """
        return path.stem

    def find_skills_by_basename(self, basename: str) -> list[Skill]:
        """Find all skills with the same basename.

        Useful for finding all versions of a skill.

        Args:
            basename: The basename to search for

        Returns:
            List of skills with matching basename, sorted by version
        """
        registry = self._load_registry()
        matches = [
            skill for skill in registry.skills.values() if skill.basename == basename
        ]
        return sorted(
            matches,
            key=lambda i: (i.major, i.minor),
            reverse=True,
        )

    def get_latest_version(self, basename: str) -> Skill | None:
        """Get the latest version of a skill by basename.

        Args:
            basename: The basename to search for

        Returns:
            Latest version skill, or None if not found
        """
        matches = self.find_skills_by_basename(basename)
        return matches[0] if matches else None
