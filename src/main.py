"""AIPromptManager application entry point."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

import structlog

from models.conventions_schema import ConventionsSchema
from repositories.conventions_repository import ConventionsRepository
from repositories.json_repository import JsonRepository
from repositories.registry_repository import RegistryRepository
from services.agent_builder import AgentBuilder
from services.naming_service import NamingService
from services.registry_service import RegistryService
from services.settings_service import SettingsService
from ui.main_window import MainWindow
from utils.logging_config import configure_logging


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AIPromptManager - AI Prompt Library Manager"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("sample_data"),
        help="Path to data directory containing .apm folder (default: sample_data)",
    )
    return parser.parse_args()


def migrate_registry_if_needed(data_dir: Path, logger: structlog.BoundLogger) -> None:
    """Move registry.json to .apm/ folder if using old location.

    Args:
        data_dir: Data directory to check
        logger: Logger for status messages
    """
    old_path = data_dir / "registry.json"
    apm_dir = data_dir / ".apm"
    new_path = apm_dir / "registry.json"

    if old_path.exists() and not new_path.exists():
        apm_dir.mkdir(exist_ok=True)
        shutil.move(str(old_path), str(new_path))
        logger.info("migrated_registry", old=str(old_path), new=str(new_path))


def main() -> None:
    """Initialize and run the AIPromptManager application."""
    # Parse command-line arguments
    args = parse_args()
    data_dir = args.data_dir.resolve()

    # Configure logging
    seq_url = os.getenv("SEQ_URL")
    configure_logging(app_name="AIPromptManager", log_level="INFO", seq_url=seq_url)
    logger = structlog.get_logger(__name__)
    logger.info("application_starting", data_dir=str(data_dir))

    # Validate and setup paths
    if not data_dir.exists():
        logger.error("data_directory_not_found", path=str(data_dir))
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # Migrate registry to .apm/ if needed
    migrate_registry_if_needed(data_dir, logger)

    # Setup .apm folder and paths
    apm_dir = data_dir / ".apm"
    apm_dir.mkdir(exist_ok=True)
    registry_path = apm_dir / "registry.json"
    conventions_path = apm_dir / "conventions.json"

    # Create registry if it doesn't exist
    if not registry_path.exists():
        logger.warning("registry_not_found_creating_empty", path=str(registry_path))
        empty_registry = {"ingredients": [], "version": "1.0"}
        registry_path.write_text(json.dumps(empty_registry, indent=2))

    logger.info(
        "paths_configured",
        data_dir=str(data_dir),
        registry=str(registry_path),
        conventions=str(conventions_path),
    )

    # Wire up dependencies
    json_repo = JsonRepository()

    # Load conventions (with fallback and warnings)
    conventions_repo = ConventionsRepository(json_repo=json_repo)
    conventions, warnings = conventions_repo.load_or_default(
        conventions_path if conventions_path.exists() else None
    )

    # Log any convention warnings
    for warning in warnings:
        logger.warning("conventions_warning", message=warning)

    # Create naming service
    naming_service = NamingService(conventions)

    registry_repo = RegistryRepository(
        json_repo=json_repo,
    )
    registry_service = RegistryService(
        registry_repository=registry_repo,
        registry_path=registry_path,
        repo_root=data_dir,
        naming_service=naming_service,
    )
    settings_service = SettingsService(str(apm_dir / "settings.json"))

    agent_builder = AgentBuilder(
        registry_service=registry_service,
        repo_root=data_dir,
        naming_service=naming_service,
    )

    # Create and run main window (pass warnings for display)
    app = MainWindow(
        registry_service, agent_builder, settings_service, startup_warnings=warnings
    )
    app.run()


if __name__ == "__main__":
    main()
