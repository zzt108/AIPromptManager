"""Agent builder service for AI Prompt Manager."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from models.agent_config import AgentConfig
from models.service_results import BuildResult, VersionUpdate
from models.sync_types import SyncAction, SyncStatus, SyncTask

if TYPE_CHECKING:
    from services.registry_service import RegistryService

logger = structlog.get_logger()

# Pattern to convert versioned to version-less filename
# TYPE-MAJOR-MINOR-Name.md -> TYPE--Name.md
VERSIONED_TO_VERSIONLESS = re.compile(
    r"^(?P<type>[A-Z]+)-\d+-\d+-(?P<basename>.+\.md)$"
)


class AgentBuilder:
    """Builds .agent folders from configuration files.

    Copies ingredients from registry to output directory with
    version-less filenames for cross-reference compatibility.

    Attributes:
        registry_service: Service for registry lookups
        repo_root: Root path of the AI Prompts repository
    """

    def __init__(
        self,
        registry_service: RegistryService,
        repo_root: Path,
    ) -> None:
        """Initialize agent builder.

        Args:
            registry_service: Service for looking up ingredients
            repo_root: Root path of the repository
        """
        self.registry_service = registry_service
        self.repo_root = repo_root

    def get_sync_tasks(
        self,
        config_path: Path,
        output_path: Path,
    ) -> list[SyncTask]:
        """Get a list of sync tasks for a build operation.

        Scans the config file and compares each ingredient with the
        target directory to determine sync status.

        Args:
            config_path: Path to agent.config.json
            output_path: Path to output directory (.agent/rules)

        Returns:
            List of SyncTask objects, one per ingredient

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        config = AgentConfig.from_file(config_path)
        tasks: list[SyncTask] = []

        for ingredient_name in config.ingredients:
            ingredient = self.registry_service.get_ingredient(ingredient_name)

            if ingredient is None:
                # Create a placeholder task for missing ingredient
                logger.warning(
                    "ingredient_not_found",
                    ingredient=ingredient_name,
                )
                continue

            source_path = self.repo_root / ingredient.path
            target_filename = self._make_versionless_name(ingredient.path.name)
            target_path = output_path / target_filename

            # Determine sync status
            status, source_mtime, target_mtime = self._check_sync_status(
                source_path, target_path
            )

            tasks.append(
                SyncTask(
                    ingredient=ingredient,
                    source_path=source_path,
                    target_path=target_path,
                    source_mtime=source_mtime,
                    target_mtime=target_mtime,
                    status=status,
                )
            )

        logger.info(
            "sync_tasks_generated",
            config=str(config_path),
            output=str(output_path),
            task_count=len(tasks),
        )

        return tasks

    def _check_sync_status(
        self,
        source_path: Path,
        target_path: Path,
    ) -> tuple[SyncStatus, float, float]:
        """Check the sync status between source and target files.

        Args:
            source_path: Absolute path to source file
            target_path: Absolute path to target file

        Returns:
            Tuple of (status, source_mtime, target_mtime)
        """
        source_mtime = 0.0
        target_mtime = 0.0

        if not source_path.exists():
            return (SyncStatus.MISSING_SOURCE, source_mtime, target_mtime)

        source_mtime = source_path.stat().st_mtime

        if not target_path.exists():
            return (SyncStatus.NOT_DEPLOYED, source_mtime, target_mtime)

        target_mtime = target_path.stat().st_mtime

        # Allow 1 second tolerance for timestamp comparison
        if abs(source_mtime - target_mtime) < 1:
            return (SyncStatus.IN_SYNC, source_mtime, target_mtime)
        elif source_mtime > target_mtime:
            return (SyncStatus.SOURCE_NEWER, source_mtime, target_mtime)
        else:
            return (SyncStatus.TARGET_NEWER, source_mtime, target_mtime)

    def process_task(
        self,
        task: SyncTask,
        action: SyncAction,
    ) -> bool:
        """Execute a sync action on a single task.

        Args:
            task: The sync task to process
            action: The action to perform

        Returns:
            True if a file was modified, False otherwise
        """
        if action == SyncAction.SKIP:
            logger.debug(
                "task_skipped",
                ingredient=task.ingredient.name,
            )
            return False

        if action == SyncAction.COPY:
            # Copy source to target
            task.target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(task.source_path, task.target_path)
            logger.info(
                "file_copied",
                source=str(task.source_path),
                target=str(task.target_path),
            )
            return True

        if action == SyncAction.UPDATE_SOURCE:
            # Copy target back to source (for local changes)
            shutil.copy2(task.target_path, task.source_path)
            logger.info(
                "source_updated",
                source=str(task.source_path),
                target=str(task.target_path),
            )
            return True

        return False

    def build_agent(
        self,
        config_path: Path,
        output_path: Path,
    ) -> BuildResult:
        """Build an agent folder from configuration.

        This is a convenience method that auto-copies all files.
        For interactive builds, use get_sync_tasks() and process_task().

        Args:
            config_path: Path to agent.config.json
            output_path: Path to output directory (.agent/rules)

        Returns:
            BuildResult with counts and warnings

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If any ingredient reference is invalid
        """
        result = BuildResult()

        # Load configuration
        config = AgentConfig.from_file(config_path)

        logger.info(
            "build_agent_started",
            config=str(config_path),
            output=str(output_path),
            ingredient_count=len(config.ingredients),
        )

        # Verify all ingredients exist
        missing_ingredients = []
        for name in config.ingredients:
            if not self.registry_service.get_ingredient(name):
                missing_ingredients.append(name)

        if missing_ingredients:
            raise ValueError(
                f"Missing ingredients in registry: {', '.join(missing_ingredients)}"
            )

        # Check for newer versions and add warnings
        version_updates = self.check_newer_versions(config)
        for update in version_updates:
            result.warnings.append(str(update))

        # Get sync tasks
        tasks = self.get_sync_tasks(config_path, output_path)

        # Process each task
        for task in tasks:
            if task.status == SyncStatus.MISSING_SOURCE:
                result.warnings.append(f"Missing source: {task.ingredient.name}")
                continue

            if task.status in (
                SyncStatus.NOT_DEPLOYED,
                SyncStatus.SOURCE_NEWER,
            ):
                self.process_task(task, SyncAction.COPY)
                result.copied += 1
            else:
                result.skipped += 1

        logger.info(
            "build_agent_complete",
            copied=result.copied,
            skipped=result.skipped,
            warnings=len(result.warnings),
        )

        return result

    def check_newer_versions(
        self,
        config: AgentConfig,
    ) -> list[VersionUpdate]:
        """Check if newer versions exist for any ingredients.

        For each ingredient in the config, checks if a newer version
        with the same basename exists in the registry.

        Args:
            config: Agent configuration to check

        Returns:
            List of VersionUpdate objects for ingredients with updates
        """
        updates: list[VersionUpdate] = []

        for ingredient_name in config.ingredients:
            ingredient = self.registry_service.get_ingredient(ingredient_name)
            if ingredient is None:
                continue

            # Find latest version with same basename
            latest = self.registry_service.get_latest_version(ingredient.basename)

            if latest is None:
                continue

            # Check if there's a newer version
            if (latest.major, latest.minor) > (ingredient.major, ingredient.minor):
                updates.append(
                    VersionUpdate(
                        ingredient_name=ingredient_name,
                        current_major=ingredient.major,
                        current_minor=ingredient.minor,
                        latest_major=latest.major,
                        latest_minor=latest.minor,
                        latest_name=latest.name,
                    )
                )

        return updates

    def _make_versionless_name(self, filename: str) -> str:
        """Convert a versioned filename to version-less format.

        TYPE-MAJOR-MINOR-Name.md -> TYPE--Name.md
        If already version-less, return unchanged.

        Args:
            filename: Original filename

        Returns:
            Version-less filename
        """
        match = VERSIONED_TO_VERSIONLESS.match(filename)
        if match:
            return f"{match.group('type')}--{match.group('basename')}"

        # Already version-less or unknown format, return as-is
        return filename

    def get_sync_status(
        self,
        config_path: Path,
        output_path: Path,
    ) -> dict[str, str]:
        """Get sync status for each ingredient.

        Compares timestamps between source and target files.

        Args:
            config_path: Path to agent.config.json
            output_path: Output directory

        Returns:
            Dictionary mapping ingredient name to status
            ('in_sync', 'source_newer', 'target_newer', 'not_deployed')
        """
        tasks = self.get_sync_tasks(config_path, output_path)
        return {task.ingredient.name: task.status.name.lower() for task in tasks}
