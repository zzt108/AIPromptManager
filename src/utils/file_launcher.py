"""Utility for launching files in external applications."""

import os
import platform
import subprocess
import structlog
from pathlib import Path

logger = structlog.get_logger(__name__)


def open_with_default_app(path: Path | str) -> None:
    """Open file with the system's default application."""
    path_str = str(path)
    try:
        if platform.system() == "Windows":
            os.startfile(path_str)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path_str], check=False)
        else:  # Linux
            subprocess.run(["xdg-open", path_str], check=False)
        logger.info("file_opened_default", path=path_str)
    except Exception as e:
        logger.error("file_open_default_error", path=path_str, error=str(e))
        raise e


def open_with_notepad(path: Path | str) -> None:
    """Open file with Notepad (Windows) or default app (others)."""
    path_str = str(path)
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["notepad.exe", path_str])
            logger.info("file_opened_notepad", path=path_str)
        else:
            # Fallback for non-Windows
            open_with_default_app(path)
    except Exception as e:
        logger.error("file_open_notepad_error", path=path_str, error=str(e))
        raise e


def show_in_explorer(path: Path | str) -> None:
    """Open file explorer and select the file."""
    path_str = str(path)
    try:
        if platform.system() == "Windows":
            subprocess.run(["explorer", "/select,", path_str], check=False)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", "-R", path_str], check=False)
        else:  # Linux
            subprocess.run(["xdg-open", os.path.dirname(path_str)], check=False)
        logger.info("file_shown_in_explorer", path=path_str)
    except Exception as e:
        logger.error("file_show_explorer_error", path=path_str, error=str(e))
        raise e
