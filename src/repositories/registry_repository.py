"""Registry repository for AI Prompt Manager."""

from __future__ import annotations

from pathlib import Path

import structlog

from models.registry_schema import RegistrySchema
from repositories.json_repository import JsonRepository

logger = structlog.get_logger()


class RegistryRepository:
    """Registry-specific persistence operations.

    Uses JsonRepository for I/O and handles RegistrySchema validation
    and conversion.

    Attributes:
        json_repo: JsonRepository instance for file operations
    """

    def __init__(self, json_repo: JsonRepository | None = None) -> None:
        """Initialize registry repository.

        Args:
            json_repo: Optional JsonRepository instance (creates default if None)
        """
        self.json_repo = json_repo or JsonRepository()

    def load_registry(self, path: Path) -> RegistrySchema:
        """Load and validate registry from file.

        Args:
            path: Path to registry.json

        Returns:
            Validated RegistrySchema instance

        Raises:
            FileNotFoundError: If registry file doesn't exist
            ValueError: If registry schema is invalid
        """
        logger.info("loading_registry", path=str(path))

        data = self.json_repo.load_json(path)
        registry = RegistrySchema.from_dict(data)
        registry.validate()

        logger.info(
            "registry_loaded",
            path=str(path),
            ingredient_count=len(registry.ingredients),
        )
        return registry

    def save_registry(self, path: Path, registry: RegistrySchema) -> None:
        """Save registry to file.

        Validates schema before saving.

        Args:
            path: Path where registry.json should be written
            registry: RegistrySchema to save

        Raises:
            ValueError: If registry validation fails
        """
        logger.info("saving_registry", path=str(path))

        registry.validate()
        data = registry.to_dict()
        self.json_repo.save_json(path, data)

        logger.info(
            "registry_saved",
            path=str(path),
            ingredient_count=len(registry.ingredients),
        )
