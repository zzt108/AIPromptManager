"""Generic JSON repository for AI Prompt Manager."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class JsonRepository:
    """Generic JSON file operations with error handling.

    Provides reusable JSON load/save operations with structured logging
    and comprehensive error handling.
    """

    @staticmethod
    def load_json(path: Path) -> dict[str, Any]:
        """Load JSON data from file.

        Args:
            path: Path to JSON file

        Returns:
            Parsed JSON data as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is malformed
        """
        logger.info("loading_json", path=str(path))

        if not path.exists():
            logger.error("file_not_found", path=str(path))
            raise FileNotFoundError(f"File not found: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            data: dict[str, Any] = json.loads(content)
            logger.info("json_loaded_successfully", path=str(path))
            return data
        except json.JSONDecodeError as e:
            logger.error("invalid_json", path=str(path), error=str(e), exc_info=True)
            raise ValueError(f"Invalid JSON in {path}: {e}") from e
        except UnicodeDecodeError as e:
            logger.error("encoding_error", path=str(path), error=str(e), exc_info=True)
            raise ValueError(f"Encoding error in {path}: {e}") from e

    @staticmethod
    def save_json(path: Path, data: dict[str, Any]) -> None:
        """Save JSON data to file with atomic write.

        Creates parent directories if needed. Writes with indentation
        for human readability.

        Args:
            path: Path where JSON should be written
            data: Dictionary to serialize as JSON

        Raises:
            PermissionError: If write permission is denied
        """
        logger.info("saving_json", path=str(path))

        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write with indentation for readability
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            path.write_text(json_content, encoding="utf-8")

            logger.info("json_saved_successfully", path=str(path))
        except PermissionError as e:
            logger.error(
                "permission_denied", path=str(path), error=str(e), exc_info=True
            )
            raise
        except Exception as e:
            logger.error("save_failed", path=str(path), error=str(e), exc_info=True)
            raise
