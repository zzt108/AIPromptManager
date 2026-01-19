"""Tests for JsonRepository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from repositories.json_repository import JsonRepository


def test_load_json_success(tmp_path: Path) -> None:
    """Test loading valid JSON file."""
    # Arrange
    json_file = tmp_path / "test.json"
    test_data: dict[str, Any] = {"key": "value", "number": 42}
    json_file.write_text(json.dumps(test_data), encoding="utf-8")

    # Act
    result = JsonRepository.load_json(json_file)

    # Assert
    assert result == test_data


def test_load_json_file_not_found(tmp_path: Path) -> None:
    """Test loading non-existent file raises FileNotFoundError."""
    # Arrange
    json_file = tmp_path / "nonexistent.json"

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="File not found"):
        JsonRepository.load_json(json_file)


def test_load_json_invalid_json(tmp_path: Path) -> None:
    """Test loading malformed JSON raises ValueError."""
    # Arrange
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{invalid json content}", encoding="utf-8")

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid JSON"):
        JsonRepository.load_json(json_file)


def test_save_json_creates_file(tmp_path: Path) -> None:
    """Test saving JSON creates new file."""
    # Arrange
    json_file = tmp_path / "new.json"
    test_data: dict[str, Any] = {"created": True, "count": 123}

    # Act
    JsonRepository.save_json(json_file, test_data)

    # Assert
    assert json_file.exists()
    saved_data = json.loads(json_file.read_text(encoding="utf-8"))
    assert saved_data == test_data


def test_save_json_overwrites_existing(tmp_path: Path) -> None:
    """Test saving JSON overwrites existing file."""
    # Arrange
    json_file = tmp_path / "existing.json"
    json_file.write_text('{"old": "data"}', encoding="utf-8")

    new_data: dict[str, Any] = {"new": "content"}

    # Act
    JsonRepository.save_json(json_file, new_data)

    # Assert
    saved_data = json.loads(json_file.read_text(encoding="utf-8"))
    assert saved_data == new_data
    assert "old" not in saved_data


def test_save_json_creates_parent_directories(tmp_path: Path) -> None:
    """Test saving JSON creates parent directories if needed."""
    # Arrange
    json_file = tmp_path / "nested" / "dir" / "file.json"
    test_data: dict[str, Any] = {"nested": True}

    # Act
    JsonRepository.save_json(json_file, test_data)

    # Assert
    assert json_file.exists()
    assert json_file.parent.exists()
    saved_data = json.loads(json_file.read_text(encoding="utf-8"))
    assert saved_data == test_data


def test_save_json_formats_with_indentation(tmp_path: Path) -> None:
    """Test saved JSON is formatted with indentation."""
    # Arrange
    json_file = tmp_path / "formatted.json"
    test_data: dict[str, Any] = {"key": "value", "nested": {"inner": "data"}}

    # Act
    JsonRepository.save_json(json_file, test_data)

    # Assert
    content = json_file.read_text(encoding="utf-8")
    # Indented JSON should contain newlines
    assert "\n" in content
    assert "  " in content  # 2-space indentation
