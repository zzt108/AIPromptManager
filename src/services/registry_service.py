"""Registry service for AI Prompt Manager business logic."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from models.conventions_schema import ConventionsSchema
from models.skill import Skill
from models.skill_status import SkillStatus
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
ARCHIVE_DIR = ".archive"


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

        # Extract metadata intelligently
        (
            skill_type,
            major,
            minor,
            basename,
            status,
            status_detail,
        ) = self._extract_metadata_intelligently(path)

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
            status=status,
            status_detail=status_detail,
            modified_at=absolute_path.stat().st_mtime,
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
            modified_at=old.modified_at,
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
                    modified_at=old.modified_at,
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
            modified_at=absolute_path.stat().st_mtime,
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

            # Scan for markdown and YAML files
            for pattern in ("*.md", "*.yaml", "*.yml"):
                for skill_file in dir_path.rglob(pattern):
                    relative_path = skill_file.relative_to(self.repo_root)

                    try:
                        name = self._derive_skill_name(relative_path)
                        found_files.add(name)

                        current_mtime = skill_file.stat().st_mtime
                        if name in registry.skills:
                            existing = registry.skills[name]

                            # Check if path changed
                            path_changed = existing.path != relative_path
                            # Check if file modified (allow small float diff)
                            file_modified = (
                                abs(existing.modified_at - current_mtime) > 0.001
                            )

                            if path_changed or file_modified:
                                # We need to update the skill
                                new_skill = Skill(
                                    name=existing.name,
                                    path=relative_path,
                                    description=existing.description,
                                    type=existing.type,
                                    major=existing.major,
                                    minor=existing.minor,
                                    basename=existing.basename,
                                    is_enabled=existing.is_enabled,
                                    status=existing.status,
                                    status_detail=existing.status_detail,
                                    modified_at=current_mtime,
                                )
                                registry.skills[name] = new_skill
                                result.updated += 1
                                if path_changed:
                                    logger.info(
                                        "skill_path_updated_refresh",
                                        name=name,
                                        old=str(existing.path),
                                        new=str(relative_path),
                                    )
                        else:
                            # Add new skill (name NOT in registry)
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

    def _extract_metadata_intelligently(
        self,
        path: Path,
    ) -> tuple[str, int, int, str, SkillStatus, str | None]:
        """Extract metadata using multiple strategies.

        Returns:
            Tuple of (type, major, minor, basename, status, status_detail)
        """
        absolute_path = self.repo_root / path

        # Check if file is readable
        try:
            _ = absolute_path.read_text(encoding="utf-8")
        except Exception as e:
            # File unreadable - parse_error
            return (
                "Uncategorized",
                0,
                0,
                path.stem,
                SkillStatus.PARSE_ERROR,
                f"Cannot read file: {e}",
            )

        # Strategy 1: strict using existing extraction logic
        try:
            t, M, m, b = self._extract_metadata(path)
            # If successful, it's valid
            return t, M, m, b, SkillStatus.VALID, None
        except ValueError as e:
            # Fallback to permissive mode
            error_msg = str(e)

        # Strategy 2-4: Fallback defaults for now
        # Future: Implement H1/Frontmatter extraction here
        return (
            "Uncategorized",
            0,
            0,
            path.stem,
            SkillStatus.UNRECOGNIZED,
            f"Pattern mismatch: {error_msg}",
        )

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

        # Update registry directly instead of calling refresh_registry
        # (refresh_registry with single dir would delete all other skills!)
        registry = self._load_registry()

        # Remove old skill entry
        if current_name in registry.skills:
            del registry.skills[current_name]

        # Create new skill entry with updated metadata
        new_relative_path = new_path.relative_to(self.repo_root)
        new_name = self._derive_skill_name(new_relative_path)
        new_description = self._extract_h1_heading(new_path)

        new_skill = Skill(
            name=new_name,
            path=new_relative_path,
            description=new_description,
            type=new_type,
            major=new_major,
            minor=new_minor,
            basename=new_basename,
            is_enabled=skill.is_enabled,
            status=SkillStatus.VALID,  # Now has valid naming pattern
            status_detail=None,
            modified_at=new_path.stat().st_mtime,
        )

        registry.skills[new_name] = new_skill
        self._save_registry()

        logger.info(
            "skill_renamed_in_registry",
            old_name=current_name,
            new_name=new_name,
        )

    def _derive_skill_name(self, path: Path) -> str:
        """Derive skill name from file path.

        Uses the filename without extension as the skill name.

        Args:
            path: Path to the skill file

        Returns:
            Derived skill name
        """
        return path.stem

    def generate_rename_suggestions(self, skill: Skill) -> list[dict[str, Any]]:
        """Generate intelligent rename suggestions for a skill.

        Strategies:
        1. H1 Heading: Extract basename from first H1
        2. YAML Frontmatter: Extract type/version/name
        3. Cleaned Stem: Fallback text cleanup

        Args:
            skill: The skill to generate suggestions for

        Returns:
            List of suggestion dicts {source, type, major, minor, basename}
        """
        suggestions = []
        absolute_path = self.repo_root / skill.path

        try:
            content = absolute_path.read_text(encoding="utf-8")
        except Exception:
            return []

        # Strategy 1: H1 Heading (Basename only)
        # Use existing helper but handle fallback
        h1_text = self._extract_h1_heading(absolute_path)
        # _extract_h1_heading falls back to stem, so check if it differs
        if h1_text and h1_text != skill.path.stem:
            # Clean up H1: PascalCase, alphanumeric only
            clean_h1 = "".join(x for x in h1_text.title() if x.isalnum())
            if clean_h1:
                # Default to GUIDE if type is unknown/uncategorized
                suggestion_type = (
                    skill.type if skill.type != "Uncategorized" else "GUIDE"
                )
                suggestions.append(
                    {
                        "source": "H1 Heading",
                        "type": suggestion_type,
                        "major": skill.major,
                        "minor": skill.minor,
                        "basename": clean_h1,
                    }
                )

        # Strategy 2: YAML Frontmatter
        frontmatter = {}
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_text = parts[1]
                    for line in yaml_text.splitlines():
                        if ":" in line:
                            key, val = line.split(":", 1)
                            frontmatter[key.strip()] = val.strip().strip("\"'")
            except Exception:
                pass

        if frontmatter:
            # Extract fields with defaults
            fm_type = frontmatter.get("type", skill.type)
            if fm_type == "Uncategorized":
                fm_type = "GUIDE"

            fm_ver = str(frontmatter.get("version", f"{skill.major}.{skill.minor}"))
            fm_name = frontmatter.get("name", "")

            # Parse version string "1.2" -> 1, 2
            try:
                if "." in fm_ver:
                    fm_major, fm_minor = map(int, fm_ver.split(".")[:2])
                else:
                    fm_major, fm_minor = int(fm_ver), 0
            except ValueError:
                fm_major, fm_minor = 1, 0

            clean_fm_name = "".join(x for x in fm_name.title() if x.isalnum())

            # Only add if we found something useful
            if clean_fm_name or fm_type != skill.type:
                suggestions.append(
                    {
                        "source": "YAML Frontmatter",
                        "type": fm_type,
                        "major": fm_major,
                        "minor": fm_minor,
                        "basename": clean_fm_name or skill.basename,
                    }
                )

        # Strategy 3: Cleaned Stem (Fallback)
        # e.g. "my-cool_script" -> "MyCoolScript"
        stem = skill.path.stem
        clean_stem = "".join(
            x for x in stem.replace("-", " ").replace("_", " ").title() if x.isalnum()
        )

        suggestions.append(
            {
                "source": "Cleaned Filename",
                "type": skill.type if skill.type != "Uncategorized" else "GUIDE",
                "major": skill.major,
                "minor": skill.minor,
                "basename": clean_stem,
            }
        )

        return suggestions

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

    def archive_skills(self, skill_names: list[str]) -> int:
        """Archive a list of skills.

        Moves the files to the .archive/ directory and updates the registry status.

        Args:
            skill_names: List of skill names to archive

        Returns:
            Number of skills successfully archived
        """
        registry = self._load_registry()
        archived_count = 0
        archive_root = self.repo_root / ARCHIVE_DIR

        for name in skill_names:
            if name not in registry.skills:
                logger.warning("skill_not_found_for_archive", name=name)
                continue

            skill = registry.skills[name]
            if skill.status == SkillStatus.ARCHIVED:
                logger.info("skill_already_archived", name=name)
                continue

            # Calculate paths
            original_path = self.repo_root / skill.path
            archive_path = archive_root / skill.path

            if not original_path.exists():
                logger.error("file_not_found_for_archive", path=str(original_path))
                continue

            if archive_path.exists():
                logger.error("archive_destination_exists", path=str(archive_path))
                # Skip to prevent overwriting existing archive
                continue

            # Ensure archive directory exists
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                # Move file
                original_path.rename(archive_path)

                # Update registry
                new_relative_path = archive_path.relative_to(self.repo_root)
                registry.skills[name] = Skill(
                    name=skill.name,
                    path=new_relative_path,
                    description=skill.description,
                    type=skill.type,
                    major=skill.major,
                    minor=skill.minor,
                    basename=skill.basename,
                    is_enabled=False,  # Implicitly hidden
                    status=SkillStatus.ARCHIVED,
                    status_detail=None,
                    modified_at=archive_path.stat().st_mtime,
                )
                archived_count += 1
                logger.info("skill_archived", name=name, path=str(archive_path))

            except OSError as e:
                logger.error("archive_failed", name=name, error=str(e))

        if archived_count > 0:
            self._save_registry()

        return archived_count

    def restore_skills(self, skill_names: list[str]) -> int:
        """Restore a list of skills from archive.

        Moves the files back to their original location (stripping .archive prefix)
        and updates the registry status.

        Args:
            skill_names: List of skill names to restore

        Returns:
            Number of skills successfully restored
        """
        registry = self._load_registry()
        restored_count = 0
        archive_root = self.repo_root / ARCHIVE_DIR

        for name in skill_names:
            if name not in registry.skills:
                logger.warning("skill_not_found_for_restore", name=name)
                continue

            skill = registry.skills[name]
            if skill.status != SkillStatus.ARCHIVED:
                logger.info("skill_not_archived", name=name)
                continue

            # Calculate paths
            current_path = self.repo_root / skill.path

            # Target path: strip ARCHIVE_DIR from the relative path
            # skill.path is like ".archive/prompts/..."
            try:
                # Get path relative to archive root to restore original structure
                # e.g. "prompts/foo.md" from ".archive/prompts/foo.md"
                original_relative_path = current_path.relative_to(archive_root)
            except ValueError:
                # Fallback if path manipulation fails or manual edit messed it up
                logger.error("invalid_archive_path", path=str(skill.path))
                continue

            restore_path = self.repo_root / original_relative_path

            if not current_path.exists():
                logger.error("archived_file_not_found", path=str(current_path))
                continue

            if restore_path.exists():
                logger.error("restore_destination_exists", path=str(restore_path))
                continue

            # Ensure restore directory exists
            restore_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                # Move file
                current_path.rename(restore_path)

                # Update registry
                registry.skills[name] = Skill(
                    name=skill.name,
                    path=original_relative_path,
                    description=skill.description,
                    type=skill.type,
                    major=skill.major,
                    minor=skill.minor,
                    basename=skill.basename,
                    is_enabled=True,  # Re-enable by default
                    status=SkillStatus.VALID,
                    status_detail=None,
                    modified_at=restore_path.stat().st_mtime,
                )
                restored_count += 1
                logger.info("skill_restored", name=name, path=str(restore_path))

            except OSError as e:
                logger.error("restore_failed", name=name, error=str(e))

        if restored_count > 0:
            self._save_registry()

        return restored_count

    def get_latest_version(self, basename: str) -> Skill | None:
        """Get the latest version of a skill by basename.

        Args:
            basename: The basename to search for

        Returns:
            Latest version skill, or None if not found
        """
        matches = self.find_skills_by_basename(basename)
        return matches[0] if matches else None
