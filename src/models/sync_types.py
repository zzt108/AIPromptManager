"""Sync status enum and task dataclass for file synchronization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.skill import Skill


class SyncStatus(Enum):
    """Status of a file synchronization check."""

    IN_SYNC = auto()
    """Source and target are identical (same mtime)."""

    SOURCE_NEWER = auto()
    """Source file is newer than target (update available)."""

    TARGET_NEWER = auto()
    """Target file is newer than source (local changes)."""

    NOT_DEPLOYED = auto()
    """Target file does not exist yet."""

    MISSING_SOURCE = auto()
    """Source file does not exist in registry."""


class SyncAction(Enum):
    """User action for resolving sync conflicts."""

    COPY = auto()
    """Copy source to target."""

    SKIP = auto()
    """Skip this file, don't change anything."""

    UPDATE_SOURCE = auto()
    """Copy target back to source (for local changes)."""


@dataclass
class SyncTask:
    """Represents a single file synchronization task.

    Created by AgentBuilder.get_sync_tasks() for each skill
    in a config file. UI iterates these to show dialogs for conflicts.

    Attributes:
        skill: The skill being synchronized
        source_path: Absolute path to source file
        target_path: Absolute path to target file
        source_mtime: Source file modification time (or 0 if not exists)
        target_mtime: Target file modification time (or 0 if not exists)
        status: Computed sync status
    """

    skill: Skill
    source_path: Path
    target_path: Path
    source_mtime: float
    target_mtime: float
    status: SyncStatus

    @property
    def target_filename(self) -> str:
        """Return the target filename (version-less)."""
        return self.target_path.name
