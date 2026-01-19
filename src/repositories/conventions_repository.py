"""Conventions repository for loading naming configuration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from models.conventions_schema import ConventionsSchema

if TYPE_CHECKING:
    from repositories.json_repository import JsonRepository

logger = structlog.get_logger()


class ConventionsRepository:
    """Repository for loading and managing conventions.json files.

    Provides methods to load naming conventions from configuration files
    with graceful fallback to defaults when files are missing or invalid.

    Attributes:
        json_repo: Repository for JSON file I/O operations
    """

    def __init__(self, json_repo: JsonRepository) -> None:
        """Initialize conventions repository.

        Args:
            json_repo: Repository for JSON file operations
        """
        self.json_repo = json_repo

    def load_conventions(self, path: Path) -> ConventionsSchema:
        """Load conventions from a JSON file.

        Args:
            path: Path to conventions.json file

        Returns:
            ConventionsSchema loaded from file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is malformed
        """
        if not path.exists():
            logger.warning("conventions_file_not_found", path=str(path))
            raise FileNotFoundError(f"Conventions file not found: {path}")

        try:
            data = self.json_repo.load_json(path)
            conventions = ConventionsSchema.from_dict(data)
            logger.info("conventions_loaded", path=str(path))
            return conventions
        except Exception as e:
            logger.error("conventions_load_error", path=str(path), error=str(e))
            raise ValueError(f"Failed to load conventions: {e}") from e

    def get_default_conventions(self) -> ConventionsSchema:
        """Get default conventions for backward compatibility.

        Returns:
            ConventionsSchema with default naming patterns
        """
        return ConventionsSchema.get_default()

    def load_or_default(self, path: Path | None) -> tuple[ConventionsSchema, list[str]]:
        """Load conventions from file or fall back to defaults.

        Attempts to load conventions from the specified path. If the file
        is missing or invalid, returns defaults with warning messages.

        Args:
            path: Path to conventions.json, or None to use defaults

        Returns:
            Tuple of (ConventionsSchema, list of warning messages)
            Warning list is empty if loaded successfully.
        """
        warnings: list[str] = []

        if path is None:
            logger.debug("conventions_path_none_using_defaults")
            return self.get_default_conventions(), warnings

        try:
            conventions = self.load_conventions(path)
            return conventions, warnings
        except FileNotFoundError:
            warnings.append(f"Conventions file not found at {path}, using defaults")
            logger.warning("conventions_fallback_file_missing", path=str(path))
            return self.get_default_conventions(), warnings
        except ValueError as e:
            warnings.append(f"Invalid conventions file: {e}, using defaults")
            logger.warning(
                "conventions_fallback_invalid",
                path=str(path),
                error=str(e),
            )
            return self.get_default_conventions(), warnings

    def save_conventions(self, path: Path, conventions: ConventionsSchema) -> None:
        """Save conventions to a JSON file.

        Args:
            path: Path to save conventions.json
            conventions: ConventionsSchema to save
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        self.json_repo.save_json(path, conventions.to_dict())
        logger.info("conventions_saved", path=str(path))
