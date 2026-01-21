"""Tests for CompareDialog."""

from __future__ import annotations

import sys
import importlib
from unittest.mock import MagicMock, patch
import pytest
from pathlib import Path
from typing import Any, Dict, List, Optional, cast


# Define MockToplevel class that behaves like a Toplevel but is a dummy
class MockToplevel:
    def __init__(self, parent: Any = None, **kwargs: Any) -> None:
        self.parent = parent

    def transient(self, *args: Any) -> None:
        pass

    def grab_set(self) -> None:
        pass

    def geometry(self, *args: Any) -> None:
        pass

    def update_idletasks(self) -> None:
        pass

    def title(self, *args: Any) -> None:
        pass

    def winfo_rootx(self) -> int:
        return 0

    def winfo_rooty(self) -> int:
        return 0

    def winfo_width(self) -> int:
        return 100

    def winfo_height(self) -> int:
        return 100

    def destroy(self) -> None:
        pass

    def winfo_toplevel(self) -> Any:
        return self


class MockVar:
    def __init__(self, value: str = "") -> None:
        self._val = value

    def get(self) -> str:
        return self._val

    def set(self, v: str) -> None:
        self._val = v


@pytest.fixture
def isolated_compare_dialog_class() -> Any:
    """Import CompareDialog in an environment where tkinter is mocked."""
    mock_tk = MagicMock()
    mock_tk.Toplevel = MockToplevel
    mock_tk.StringVar = MockVar

    with patch.dict(
        "sys.modules",
        {
            "tkinter": mock_tk,
            "tkinter.ttk": MagicMock(),
            "tkinter.messagebox": MagicMock(),
            "tkinter.filedialog": MagicMock(),
        },
    ):
        import ui.dialogs.compare_dialog

        importlib.reload(ui.dialogs.compare_dialog)
        return ui.dialogs.compare_dialog.CompareDialog


@pytest.fixture
def mock_settings_service() -> MagicMock:
    service = MagicMock()
    service.get_merge_tool_config.return_value = {
        "name": "TestTool",
        "path": "test_tool.exe",
        "args_2way": "{left} {right}",
        "args_3way": "{base} {left} {right}",
    }
    return service


@pytest.fixture
def mock_registry_service() -> MagicMock:
    service = MagicMock()
    return service


@pytest.fixture
def mock_parent() -> MagicMock:
    parent = MagicMock()
    parent.winfo_toplevel.return_value = parent
    return parent


def test_launch_2way(
    mock_parent: MagicMock,
    mock_settings_service: MagicMock,
    mock_registry_service: MagicMock,
    isolated_compare_dialog_class: Any,
) -> None:
    """Test generating 2-way compare command."""
    files = [Path("c:/file1.txt"), Path("c:/file2.txt")]

    dialog = isolated_compare_dialog_class(
        mock_parent, mock_settings_service, mock_registry_service, files
    )

    d = cast(Any, dialog)
    d.left_var = MockVar("file1.txt")
    d.right_var = MockVar("file2.txt")
    d.base_var = MockVar("")
    d.file_map = {
        "file1.txt": Path("c:/file1.txt"),
        "file2.txt": Path("c:/file2.txt"),
    }

    with patch("subprocess.Popen") as mock_popen:
        dialog._launch()
        expected_cmd = '"test_tool.exe" c:\\file1.txt c:\\file2.txt'
        mock_popen.assert_called_once()
        args, _ = mock_popen.call_args
        assert args[0] == expected_cmd


def test_launch_3way(
    mock_parent: MagicMock,
    mock_settings_service: MagicMock,
    mock_registry_service: MagicMock,
    isolated_compare_dialog_class: Any,
) -> None:
    """Test generating 3-way compare command."""
    files = [Path("c:/left.txt"), Path("c:/right.txt"), Path("c:/base.txt")]

    dialog = isolated_compare_dialog_class(
        mock_parent, mock_settings_service, mock_registry_service, files
    )

    d = cast(Any, dialog)
    d.left_var = MockVar("left.txt")
    d.right_var = MockVar("right.txt")
    d.base_var = MockVar("base.txt")
    d.file_map = {
        "left.txt": Path("c:/left.txt"),
        "right.txt": Path("c:/right.txt"),
        "base.txt": Path("c:/base.txt"),
    }

    with patch("subprocess.Popen") as mock_popen:
        dialog._launch()
        # args_3way: "{base} {left} {right}"
        expected_cmd = '"test_tool.exe" c:\\base.txt c:\\left.txt c:\\right.txt'
        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == expected_cmd


def test_launch_paths_with_spaces(
    mock_parent: MagicMock,
    mock_settings_service: MagicMock,
    mock_registry_service: MagicMock,
    isolated_compare_dialog_class: Any,
) -> None:
    """Test handling of paths with spaces."""
    files = [Path("c:/path with spaces/file1.txt"), Path("c:/file2.txt")]

    dialog = isolated_compare_dialog_class(
        mock_parent, mock_settings_service, mock_registry_service, files
    )

    d = cast(Any, dialog)
    d.left_var = MockVar("file1.txt")
    d.right_var = MockVar("file2.txt")
    d.base_var = MockVar("")
    d.file_map = {
        "file1.txt": Path("c:/path with spaces/file1.txt"),
        "file2.txt": Path("c:/file2.txt"),
    }

    with patch("subprocess.Popen") as mock_popen:
        dialog._launch()
        expected_cmd = '"test_tool.exe" "c:\\path with spaces\\file1.txt" c:\\file2.txt'
        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == expected_cmd
