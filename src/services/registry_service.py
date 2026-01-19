"""Registry service for AI Prompt Manager business logic."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from models.ingredient import Ingredient
from models.registry_schema import RegistrySchema
from models.service_results import RefreshResult

if TYPE_CHECKING:
    from repositories.registry_repository import RegistryRepository

logger = structlog.get_logger()

# Pattern for versioned filenames: TYPE-MAJOR-MINOR-Name.md
VERSIONED_PATTERN = re.compile(
    r"^(?P<type>[a-zA-Z0-9]+)-(?P<major>\d+)-(?P<minor>\d+)-(?P<basename>.+)\.md$"
)

# Pattern for version-less filenames: TYPE--Name.md
VERSIONLESS_PATTERN = re.compile(r"^(?P<type>[a-zA-Z0-9]+)--(?P<basename>.+)\.md$")


class RegistryService:
    """Business logic for registry operations.

    Provides CRUD operations on ingredients and registry refresh functionality.
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
    ) -> None:
        """Initialize registry service.

        Args:
            registry_repository: Repository for loading/saving registry
            registry_path: Path to registry.json
            repo_root: Root path of the repository for relative paths
        """
        self.registry_repository = registry_repository
        self.registry_path = registry_path
        self.repo_root = repo_root
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
                self._registry = RegistrySchema(version="1.0", ingredients={})
        return self._registry

    def _save_registry(self) -> None:
        """Save current registry state to file."""
        if self._registry is not None:
            self.registry_repository.save_registry(self.registry_path, self._registry)

    def _invalidate_cache(self) -> None:
        """Invalidate the cached registry to force reload."""
        self._registry = None

    def add_ingredient(
        self,
        path: Path,
        description: str | None = None,
    ) -> Ingredient:
        """Add a new ingredient to the registry.

        Extracts metadata (type, version, basename) from the filename.
        If description is None, extracts H1 heading from markdown file.

        Args:
            path: Path to the ingredient file (relative to repo_root)
            description: Optional description (extracted from H1 if None)

        Returns:
            The created Ingredient

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If ingredient already exists or filename is invalid
        """
        absolute_path = self.repo_root / path

        if not absolute_path.exists():
            logger.error("ingredient_file_not_found", path=str(path))
            raise FileNotFoundError(f"Ingredient file not found: {path}")

        # Extract metadata from filename
        ingredient_type, major, minor, basename = self._extract_metadata(path)

        # Derive ingredient name from path
        name = self._derive_ingredient_name(path)

        # Check for duplicates
        registry = self._load_registry()
        if name in registry.ingredients:
            logger.warning("ingredient_already_exists", name=name)
            raise ValueError(f"Ingredient already exists: {name}")

        # Extract description from H1 if not provided
        if description is None:
            description = self._extract_h1_heading(absolute_path)

        # Create ingredient
        ingredient = Ingredient(
            name=name,
            path=path,
            description=description,
            type=ingredient_type,
            major=major,
            minor=minor,
            basename=basename,
        )

        # Add to registry and save
        registry.ingredients[name] = ingredient
        self._save_registry()

        logger.info(
            "ingredient_added",
            name=name,
            path=str(path),
            type=ingredient_type,
            version=f"{major}.{minor}",
        )

        return ingredient

    def remove_ingredient(self, name: str) -> None:
        """Remove an ingredient from the registry.

        Args:
            name: Name of the ingredient to remove

        Raises:
            KeyError: If ingredient doesn't exist
        """
        registry = self._load_registry()

        if name not in registry.ingredients:
            logger.error("ingredient_not_found", name=name)
            raise KeyError(f"Ingredient not found: {name}")

        del registry.ingredients[name]
        self._save_registry()

        logger.info("ingredient_removed", name=name)

    def get_ingredient(self, name: str) -> Ingredient | None:
        """Get an ingredient by name.

        Args:
            name: Name of the ingredient

        Returns:
            Ingredient if found, None otherwise
        """
        registry = self._load_registry()
        return registry.ingredients.get(name)

    def list_all(self) -> list[Ingredient]:
        """List all ingredients in the registry.

        Returns:
            List of all ingredients, sorted by name
        """
        registry = self._load_registry()
        return sorted(
            registry.ingredients.values(),
            key=lambda i: i.name,
        )

    def list_enabled(self) -> list[Ingredient]:
        """List only enabled ingredients (visible in Profession Designer).

        Returns:
            List of enabled ingredients, sorted by name
        """
        return [ing for ing in self.list_all() if ing.is_enabled]

    def set_ingredient_enabled(self, name: str, enabled: bool) -> None:
        """Set the enabled/hidden state for a single ingredient.

        Args:
            name: Name of the ingredient
            enabled: True to enable (show), False to hide

        Raises:
            KeyError: If ingredient doesn't exist
        """
        registry = self._load_registry()

        if name not in registry.ingredients:
            logger.error("ingredient_not_found", name=name)
            raise KeyError(f"Ingredient not found: {name}")

        old = registry.ingredients[name]
        registry.ingredients[name] = Ingredient(
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
        logger.info("ingredient_visibility_changed", name=name, action=action)

    def set_ingredients_enabled(self, names: list[str], enabled: bool) -> int:
        """Set the enabled/hidden state for multiple ingredients.

        Args:
            names: List of ingredient names to update
            enabled: True to enable (show), False to hide

        Returns:
            Number of ingredients actually updated
        """
        registry = self._load_registry()
        updated = 0

        for name in names:
            if name not in registry.ingredients:
                logger.warning("ingredient_not_found_during_bulk", name=name)
                continue

            old = registry.ingredients[name]
            if old.is_enabled != enabled:
                registry.ingredients[name] = Ingredient(
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

    def update_ingredient_path(self, name: str, new_path: Path) -> None:
        """Update the path for an existing ingredient.

        Args:
            name: Name of the ingredient to update
            new_path: New path for the ingredient

        Raises:
            KeyError: If ingredient doesn't exist
            FileNotFoundError: If new path doesn't exist
        """
        registry = self._load_registry()

        if name not in registry.ingredients:
            logger.error("ingredient_not_found", name=name)
            raise KeyError(f"Ingredient not found: {name}")

        absolute_path = self.repo_root / new_path
        if not absolute_path.exists():
            logger.error("new_path_not_found", path=str(new_path))
            raise FileNotFoundError(f"New path doesn't exist: {new_path}")

        # Update the ingredient
        old_ingredient = registry.ingredients[name]
        registry.ingredients[name] = Ingredient(
            name=old_ingredient.name,
            path=new_path,
            description=old_ingredient.description,
            type=old_ingredient.type,
            major=old_ingredient.major,
            minor=old_ingredient.minor,
            basename=old_ingredient.basename,
            is_enabled=old_ingredient.is_enabled,
        )
        self._save_registry()

        logger.info(
            "ingredient_path_updated",
            name=name,
            old_path=str(old_ingredient.path),
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
                    name = self._derive_ingredient_name(relative_path)
                    found_files.add(name)

                    if name in registry.ingredients:
                        # Check if path changed
                        existing = registry.ingredients[name]
                        if existing.path != relative_path:
                            self.update_ingredient_path(name, relative_path)
                            result.updated += 1
                    else:
                        # Add new ingredient
                        self.add_ingredient(relative_path)
                        result.added += 1

                except ValueError as e:
                    # Invalid filename pattern, skip
                    result.errors.append(f"Skipped {relative_path}: {e}")

        # Check for removed files
        missing_ingredients = [
            name for name in registry.ingredients if name not in found_files
        ]
        result.removed = len(missing_ingredients)

        # Log removed files and delete them
        for name in missing_ingredients:
            del registry.ingredients[name]
            logger.warning(
                "ingredient_removed_during_refresh",
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
        """Extract metadata from ingredient filename.

        Supports both versioned (TYPE-MAJOR-MINOR-Name.md) and
        version-less (TYPE--Name.md) patterns.

        Args:
            path: Path to the ingredient file

        Returns:
            Tuple of (type, major, minor, basename)

        Raises:
            ValueError: If filename doesn't match expected pattern
        """
        filename = path.name

        # Try versioned pattern first
        match = VERSIONED_PATTERN.match(filename)
        if match:
            return (
                match.group("type"),
                int(match.group("major")),
                int(match.group("minor")),
                match.group("basename"),
            )

        # Try version-less pattern
        match = VERSIONLESS_PATTERN.match(filename)
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
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
        except Exception as e:
            logger.warning(
                "failed_to_extract_h1",
                path=str(path),
                error=str(e),
            )

        # Fallback to filename without extension
        return path.stem

    def _derive_ingredient_name(self, path: Path) -> str:
        """Derive ingredient name from file path.

        Uses the filename without extension as the ingredient name.

        Args:
            path: Path to the ingredient file

        Returns:
            Derived ingredient name
        """
        return path.stem

    def find_ingredients_by_basename(self, basename: str) -> list[Ingredient]:
        """Find all ingredients with the same basename.

        Useful for finding all versions of an ingredient.

        Args:
            basename: The basename to search for

        Returns:
            List of ingredients with matching basename, sorted by version
        """
        registry = self._load_registry()
        matches = [
            ingredient
            for ingredient in registry.ingredients.values()
            if ingredient.basename == basename
        ]
        return sorted(
            matches,
            key=lambda i: (i.major, i.minor),
            reverse=True,
        )

    def get_latest_version(self, basename: str) -> Ingredient | None:
        """Get the latest version of an ingredient by basename.

        Args:
            basename: The basename to search for

        Returns:
            Latest version ingredient, or None if not found
        """
        matches = self.find_ingredients_by_basename(basename)
        return matches[0] if matches else None
