"""Service result dataclasses for AI Prompt Manager."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RefreshResult:
    """Result of a registry refresh operation.

    Attributes:
        added: Number of new ingredients added
        updated: Number of existing ingredients updated
        removed: Number of ingredients removed (flagged for deletion)
        errors: List of error messages encountered during refresh
    """

    added: int = 0
    updated: int = 0
    removed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        """Return total number of changes made."""
        return self.added + self.updated + self.removed

    @property
    def has_errors(self) -> bool:
        """Return True if any errors occurred."""
        return len(self.errors) > 0


@dataclass
class BuildResult:
    """Result of an agent build operation.

    Attributes:
        copied: Number of files copied to output
        skipped: Number of files skipped (already up-to-date)
        warnings: List of warning messages (e.g., newer versions available)
    """

    copied: int = 0
    skipped: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        """Return total number of files processed."""
        return self.copied + self.skipped

    @property
    def has_warnings(self) -> bool:
        """Return True if any warnings were generated."""
        return len(self.warnings) > 0


@dataclass
class VersionUpdate:
    """Represents a detected version update for an ingredient.

    Used when a newer version of an ingredient exists in the registry
    than what is referenced in an agent.config.json.

    Attributes:
        ingredient_name: Name of the ingredient in the config
        current_major: Major version currently referenced
        current_minor: Minor version currently referenced
        latest_major: Major version of the newest available
        latest_minor: Minor version of the newest available
        latest_name: Full name of the latest ingredient
    """

    ingredient_name: str
    current_major: int
    current_minor: int
    latest_major: int
    latest_minor: int
    latest_name: str

    @property
    def current_version(self) -> str:
        """Return current version as string (e.g., '1.2')."""
        return f"{self.current_major}.{self.current_minor}"

    @property
    def latest_version(self) -> str:
        """Return latest version as string (e.g., '1.3')."""
        return f"{self.latest_major}.{self.latest_minor}"

    def __str__(self) -> str:
        """Return human-readable update description."""
        return (
            f"{self.ingredient_name}: {self.current_version} → "
            f"{self.latest_version} ({self.latest_name})"
        )
