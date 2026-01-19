"""Agent configuration model for AI Prompt Manager."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.registry_schema import RegistrySchema


class AgentConfig:
    """Agent configuration schema.

    Represents an agent.config.json file that references ingredients
    from the registry.

    Attributes:
        ingredients: List of ingredient names referenced in this config
    """

    def __init__(self, ingredients: list[str]) -> None:
        """Initialize agent configuration.

        Args:
            ingredients: List of ingredient names
        """
        self.ingredients = ingredients

    @staticmethod
    def from_file(config_path: Path) -> AgentConfig:
        """Load agent configuration from file.

        Args:
            config_path: Path to agent.config.json

        Returns:
            AgentConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If JSON is invalid or missing required fields
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_path}: {e}") from e

        ingredients = data.get("ingredients", [])
        if not isinstance(ingredients, list):
            raise ValueError("'ingredients' field must be a list")

        return AgentConfig(ingredients=ingredients)

    def to_file(self, config_path: Path) -> None:
        """Save agent configuration to file.

        Args:
            config_path: Path where agent.config.json should be written
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {"ingredients": self.ingredients}
        config_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def validate(self, registry: RegistrySchema) -> None:
        """Validate that all referenced ingredients exist in registry.

        Args:
            registry: Registry schema to validate against

        Raises:
            ValueError: If any ingredient reference is invalid
        """
        missing_ingredients = [
            name for name in self.ingredients if name not in registry.ingredients
        ]

        if missing_ingredients:
            raise ValueError(
                f"Invalid ingredient references: {', '.join(missing_ingredients)}"
            )
