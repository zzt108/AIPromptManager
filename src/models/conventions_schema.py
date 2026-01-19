"""Conventions schema for configurable naming patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FileNaming:
    """Configuration for file naming patterns.

    Attributes:
        pattern: Template for versioned filenames, e.g., "{TYPE}-{VERSION}-{DESCRIPTION}"
        version_format: Format for version numbers, e.g., "X-Y" for major-minor
        supported_types: List of recognized parent types (GUIDE, SPACE, PROMPT, etc.)
        output_pattern: Template for version-less output, e.g., "{TYPE}--{DESCRIPTION}"
        type_separator: Character separating type from subtype, e.g., "_" for GUIDE_CC
    """

    pattern: str = "{TYPE}-{VERSION}-{DESCRIPTION}"
    version_format: str = "X-Y"
    supported_types: list[str] = field(
        default_factory=lambda: ["GUIDE", "SPACE", "PROMPT", "WORKFLOW"]
    )
    output_pattern: str = "{TYPE}--{DESCRIPTION}"
    type_separator: str = "_"

    @staticmethod
    def from_dict(data: dict[str, Any]) -> FileNaming:
        """Create FileNaming from dictionary.

        Args:
            data: Dictionary with file naming configuration

        Returns:
            FileNaming instance with values from dict or defaults
        """
        return FileNaming(
            pattern=data.get("pattern", "{TYPE}-{VERSION}-{DESCRIPTION}"),
            version_format=data.get("version_format", "X-Y"),
            supported_types=data.get(
                "supported_types", ["GUIDE", "SPACE", "PROMPT", "WORKFLOW"]
            ),
            output_pattern=data.get("output_pattern", "{TYPE}--{DESCRIPTION}"),
            type_separator=data.get("type_separator", "_"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pattern": self.pattern,
            "version_format": self.version_format,
            "supported_types": self.supported_types,
            "output_pattern": self.output_pattern,
            "type_separator": self.type_separator,
        }


@dataclass
class ConventionsSchema:
    """Schema for conventions.json configuration.

    Defines naming patterns and metadata conventions for prompt files.

    Attributes:
        file_naming: Configuration for filename patterns
    """

    file_naming: FileNaming = field(default_factory=FileNaming)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> ConventionsSchema:
        """Create ConventionsSchema from dictionary.

        Args:
            data: Dictionary loaded from conventions.json

        Returns:
            ConventionsSchema instance
        """
        file_naming_data = data.get("file_naming", {})
        return ConventionsSchema(
            file_naming=FileNaming.from_dict(file_naming_data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_naming": self.file_naming.to_dict(),
        }

    @staticmethod
    def get_default() -> ConventionsSchema:
        """Get default conventions matching current hardcoded patterns.

        Returns:
            ConventionsSchema with default values for backward compatibility
        """
        return ConventionsSchema(file_naming=FileNaming())

    def extract_parent_type(self, type_str: str) -> str:
        """Extract parent type from a type string with optional subtype.

        Examples:
            GUIDE -> GUIDE
            GUIDE_CC -> GUIDE
            SPACE_WEB -> SPACE

        Args:
            type_str: Type string, possibly with subtype suffix

        Returns:
            Parent type (part before separator) or original if no separator
        """
        separator = self.file_naming.type_separator
        if separator and separator in type_str:
            return type_str.split(separator)[0]
        return type_str

    def is_known_type(self, type_str: str) -> bool:
        """Check if a type (or its parent) is in supported_types.

        Args:
            type_str: Type string to check

        Returns:
            True if type or parent type is recognized
        """
        parent_type = self.extract_parent_type(type_str)
        return parent_type in self.file_naming.supported_types
