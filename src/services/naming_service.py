"""Naming service for configurable file name parsing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import structlog

from models.conventions_schema import ConventionsSchema

logger = structlog.get_logger()


class NamingService:
    """Service for parsing and generating filenames based on conventions.

    Replaces hardcoded regex patterns with configurable patterns from
    conventions.json. Provides backward-compatible defaults.

    Attributes:
        conventions: ConventionsSchema with naming patterns
    """

    def __init__(self, conventions: ConventionsSchema) -> None:
        """Initialize naming service with conventions.

        Args:
            conventions: ConventionsSchema defining naming patterns
        """
        self.conventions = conventions
        self._versioned_pattern: re.Pattern[str] | None = None
        self._versionless_pattern: re.Pattern[str] | None = None
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns from conventions configuration."""
        # Build versioned pattern: TYPE-MAJOR-MINOR-Name.md
        # From template like "{TYPE}-{VERSION}-{DESCRIPTION}"
        self._versioned_pattern = re.compile(
            r"^(?P<type>[a-zA-Z0-9_]+)-(?P<major>\d+)-(?P<minor>\d+)-(?P<basename>.+)\.md$"
        )

        # Build version-less pattern: TYPE--Name.md
        # From template like "{TYPE}--{DESCRIPTION}"
        self._versionless_pattern = re.compile(
            r"^(?P<type>[a-zA-Z0-9_]+)--(?P<basename>.+)\.md$"
        )

        logger.debug(
            "naming_patterns_compiled",
            versioned=self._versioned_pattern.pattern,
            versionless=self._versionless_pattern.pattern,
        )

    def parse_filename(self, filename: str) -> dict[str, Any]:
        """Parse a filename and extract metadata fields.

        Attempts to match against versioned pattern first, then version-less.

        Args:
            filename: Filename to parse (e.g., "GUIDE-1-2-General.md")

        Returns:
            Dictionary with keys: type, major, minor, basename, is_versionless

        Raises:
            ValueError: If filename doesn't match any known pattern
        """
        # Try versioned pattern first
        if self._versioned_pattern:
            match = self._versioned_pattern.match(filename)
            if match:
                return {
                    "type": match.group("type"),
                    "major": int(match.group("major")),
                    "minor": int(match.group("minor")),
                    "basename": match.group("basename"),
                    "is_versionless": False,
                }

        # Try version-less pattern
        if self._versionless_pattern:
            match = self._versionless_pattern.match(filename)
            if match:
                return {
                    "type": match.group("type"),
                    "major": 0,
                    "minor": 0,
                    "basename": match.group("basename"),
                    "is_versionless": True,
                }

        raise ValueError(f"Filename doesn't match expected pattern: {filename}")

    def extract_metadata(self, path: Path) -> tuple[str, int, int, str]:
        """Extract metadata from ingredient filename.

        Compatible signature with original RegistryService._extract_metadata.

        Args:
            path: Path to the ingredient file

        Returns:
            Tuple of (type, major, minor, basename)

        Raises:
            ValueError: If filename doesn't match expected pattern
        """
        filename = path.name
        parsed = self.parse_filename(filename)
        return (
            parsed["type"],
            parsed["major"],
            parsed["minor"],
            parsed["basename"],
        )

    def make_versionless(self, filename: str) -> str:
        """Convert a versioned filename to version-less format.

        TYPE-MAJOR-MINOR-Name.md -> TYPE--Name.md
        If already version-less, returns unchanged.

        Args:
            filename: Original filename

        Returns:
            Version-less filename
        """
        try:
            parsed = self.parse_filename(filename)
            if parsed["is_versionless"]:
                return filename
            return f"{parsed['type']}--{parsed['basename']}.md"
        except ValueError:
            # If doesn't match pattern, return unchanged
            logger.warning("make_versionless_no_match", filename=filename)
            return filename

    def make_versioned(
        self,
        basename: str,
        major: int,
        minor: int,
        type_str: str,
    ) -> str:
        """Create a versioned filename from components.

        Args:
            basename: Base name without extension (e.g., "General")
            major: Major version number
            minor: Minor version number
            type_str: Type prefix (e.g., "GUIDE" or "GUIDE_CC")

        Returns:
            Versioned filename (e.g., "GUIDE-1-2-General.md")
        """
        return f"{type_str}-{major}-{minor}-{basename}.md"

    def validate_filename(self, filename: str) -> bool:
        """Check if a filename matches expected patterns.

        Args:
            filename: Filename to validate

        Returns:
            True if filename matches versioned or version-less pattern
        """
        try:
            self.parse_filename(filename)
            return True
        except ValueError:
            return False

    def get_parent_type(self, type_str: str) -> str:
        """Get the parent type from a type string with optional subtype.

        Delegates to conventions schema for separator handling.

        Args:
            type_str: Type string (e.g., "GUIDE_CC")

        Returns:
            Parent type (e.g., "GUIDE")
        """
        return self.conventions.extract_parent_type(type_str)

    def is_known_type(self, type_str: str) -> bool:
        """Check if a type (or its parent) is recognized.

        Args:
            type_str: Type string to check

        Returns:
            True if type or parent is in supported_types
        """
        return self.conventions.is_known_type(type_str)
