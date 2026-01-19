"""Registry schema model for AI Prompt Manager."""

from __future__ import annotations

from typing import Any

from models.ingredient import Ingredient


class RegistrySchema:
    """Registry structure with validation.

    Represents the complete registry.json structure including schema version
    and ingredient catalog.

    Attributes:
        version: Schema version string (e.g., "1.0")
        ingredients: Dictionary mapping ingredient names to Ingredient objects
    """

    def __init__(self, version: str, ingredients: dict[str, Ingredient]) -> None:
        """Initialize registry schema.

        Args:
            version: Schema version string
            ingredients: Dictionary of ingredient name -> Ingredient
        """
        self.version = version
        self.ingredients = ingredients

    @staticmethod
    def from_dict(data: dict[str, Any]) -> RegistrySchema:
        """Create RegistrySchema from dictionary.

        Args:
            data: Dictionary containing schema and ingredients

        Returns:
            RegistrySchema instance

        Raises:
            KeyError: If required field is missing
            ValueError: If schema validation fails
        """
        version = data.get("version")
        if not version:
            raise ValueError("Missing 'version' field in registry schema")

        ingredients_data = data.get("ingredients", {})
        ingredients: dict[str, Ingredient] = {}

        # Handle both list and dictionary formats for ingredients
        if isinstance(ingredients_data, list):
            # Convert list to dictionary using 'name' field as key
            for item in ingredients_data:
                if not isinstance(item, dict):
                    raise ValueError(f"Invalid ingredient format: {item}")

                name = item.get("name")
                if not name:
                    raise ValueError(f"Ingredient missing 'name' field: {item}")

                try:
                    ingredients[name] = Ingredient.from_dict(item)
                except KeyError as e:
                    raise ValueError(
                        f"Ingredient '{name}' is missing required field: {e}"
                    ) from e
        else:
            # Dictionary format (expected)
            for name, ingredient_data in ingredients_data.items():
                # Ensure name is consistent
                if "name" not in ingredient_data:
                    ingredient_data["name"] = name

                try:
                    ingredients[name] = Ingredient.from_dict(ingredient_data)
                except KeyError as e:
                    raise ValueError(
                        f"Ingredient '{name}' is missing required field: {e}"
                    ) from e

        return RegistrySchema(version=version, ingredients=ingredients)

    def to_dict(self) -> dict[str, Any]:
        """Convert registry schema to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "version": self.version,
            "ingredients": {
                name: ingredient.to_dict()
                for name, ingredient in self.ingredients.items()
            },
        }

    def validate(self) -> None:
        """Validate registry schema integrity.

        Raises:
            ValueError: If schema validation fails
        """
        if not self.version:
            raise ValueError("Registry schema requires a version")

        for name, ingredient in self.ingredients.items():
            if ingredient.name != name:
                raise ValueError(
                    f"Ingredient name mismatch: key='{name}', "
                    f"ingredient.name='{ingredient.name}'"
                )
