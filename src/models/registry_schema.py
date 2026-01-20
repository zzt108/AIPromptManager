"""Registry schema model for AI Prompt Manager."""

from __future__ import annotations

from typing import Any

from models.skill import Skill


class RegistrySchema:
    """Registry structure with validation.

    Represents the complete registry.json structure including schema version
    and skill catalog.

    Attributes:
        version: Schema version string (e.g., "1.0")
        skills: Dictionary mapping skill names to Skill objects
    """

    def __init__(self, version: str, skills: dict[str, Skill]) -> None:
        """Initialize registry schema.

        Args:
            version: Schema version string
            skills: Dictionary of skill name -> Skill
        """
        self.version = version
        self.skills = skills

    @staticmethod
    def from_dict(data: dict[str, Any]) -> RegistrySchema:
        """Create RegistrySchema from dictionary.

        Args:
            data: Dictionary containing schema and skills

        Returns:
            RegistrySchema instance

        Raises:
            KeyError: If required field is missing
            ValueError: If schema validation fails
        """
        version = data.get("version")
        if not version:
            raise ValueError("Missing 'version' field in registry schema")

        # Support both "skills" and legacy "ingredients" keys
        skills_data = data.get("skills", data.get("ingredients", {}))
        skills: dict[str, Skill] = {}

        # Handle both list and dictionary formats for skills
        if isinstance(skills_data, list):
            # Convert list to dictionary using 'name' field as key
            for item in skills_data:
                if not isinstance(item, dict):
                    raise ValueError(f"Invalid skill format: {item}")

                name = item.get("name")
                if not name:
                    raise ValueError(f"Skill missing 'name' field: {item}")

                try:
                    skills[name] = Skill.from_dict(item)
                except KeyError as e:
                    raise ValueError(
                        f"Skill '{name}' is missing required field: {e}"
                    ) from e
        else:
            # Dictionary format (expected)
            for name, skill_data in skills_data.items():
                # Ensure name is consistent
                if "name" not in skill_data:
                    skill_data["name"] = name

                try:
                    skills[name] = Skill.from_dict(skill_data)
                except KeyError as e:
                    raise ValueError(
                        f"Skill '{name}' is missing required field: {e}"
                    ) from e

        return RegistrySchema(version=version, skills=skills)

    def to_dict(self) -> dict[str, Any]:
        """Convert registry schema to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "version": self.version,
            "ingredients": {
                name: skill.to_dict() for name, skill in self.skills.items()
            },
        }

    def validate(self) -> None:
        """Validate registry schema integrity.

        Raises:
            ValueError: If schema validation fails
        """
        if not self.version:
            raise ValueError("Registry schema requires a version")

        for name, skill in self.skills.items():
            if skill.name != name:
                raise ValueError(
                    f"Skill name mismatch: key='{name}', " f"skill.name='{skill.name}'"
                )
