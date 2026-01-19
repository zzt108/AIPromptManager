"""AIPromptManager application entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import structlog

from repositories.json_repository import JsonRepository
from repositories.registry_repository import RegistryRepository
from services.agent_builder import AgentBuilder
from services.registry_service import RegistryService
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
        help="Path to data directory containing registry.json (default: sample_data)",
    )
    return parser.parse_args()


def main() -> None:
    """Initialize and run the AIPromptManager application."""
    # Parse command-line arguments
    args = parse_args()
    data_dir = args.data_dir.resolve()

    # Configure logging
    configure_logging(app_name="AIPromptManager", log_level="INFO")
    logger = structlog.get_logger(__name__)
    logger.info("application_starting", data_dir=str(data_dir))

    # Validate and setup paths
    if not data_dir.exists():
        logger.error("data_directory_not_found", path=str(data_dir))
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    registry_path = data_dir / "registry.json"

    # Create registry if it doesn't exist
    if not registry_path.exists():
        logger.warning("registry_not_found_creating_empty", path=str(registry_path))
        empty_registry = {"ingredients": [], "version": "1.0"}
        registry_path.write_text(json.dumps(empty_registry, indent=2))

    logger.info(
        "paths_configured",
        data_dir=str(data_dir),
        registry=str(registry_path),
    )

    # Wire up dependencies
    json_repo = JsonRepository()
    registry_repo = RegistryRepository(
        json_repo=json_repo,
    )
    registry_service = RegistryService(
        registry_repository=registry_repo,
        registry_path=registry_path,
        repo_root=data_dir,
    )
    agent_builder = AgentBuilder(
        registry_service=registry_service,
        repo_root=data_dir,
    )

    # Create and run main window
    app = MainWindow(registry_service, agent_builder)
    app.run()


if __name__ == "__main__":
    main()
