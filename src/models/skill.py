"""Skill model for AI Prompt Manager registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from models.skill_status import SkillStatus


@dataclass
class Skill:
    """Represents a single skill in the registry.

    A skill is a reusable asset (GUIDE, SPACE, PROMPT, etc.) tracked
    in the registry.json file.

    Attributes:
        name: Unique identifier for the skill
        path: Relative path to the skill file from repo root
        description: Auto-extracted from H1 heading in markdown
        type: Category (GUIDE, SPACE, PROMPT, etc.)
        major: Major version number
        minor: Minor version number
        basename: Core name without version suffix
        is_enabled: Whether the skill is visible in Profession Designer
        status: Recognition status ("valid", "unrecognized", "parse_error")
        status_detail: Optional detail message explaining the status
    """

    name: str
    path: Path
    description: str
    type: str
    major: int
    minor: int
    basename: str
    is_enabled: bool = True
    status: SkillStatus = SkillStatus.VALID
    status_detail: str | None = None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Skill:
        """Create Skill instance from dictionary.

        Args:
            data: Dictionary containing skill data

        Returns:
            Skill instance

        Raises:
            KeyError: If required field is missing
            TypeError: If field type is incorrect
        """
        return Skill(
            name=data["name"],
            path=Path(data["path"]),
            description=data["description"],
            type=data["type"],
            major=int(data["major"]),
            minor=int(data["minor"]),
            basename=data["basename"],
            is_enabled=data.get("is_enabled", True),
            status=SkillStatus(data.get("status", "valid")),
            status_detail=data.get("status_detail"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert skill to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "name": self.name,
            "path": self.path.as_posix(),
            "description": self.description,
            "type": self.type,
            "major": self.major,
            "minor": self.minor,
            "basename": self.basename,
            "is_enabled": self.is_enabled,
            "status": self.status.value,
            "status_detail": self.status_detail,
        }
