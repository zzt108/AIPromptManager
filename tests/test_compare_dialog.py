import sys
from unittest.mock import MagicMock, patch
import pytest
from pathlib import Path


# Define MockToplevel FIRST
class MockToplevel:
    def __init__(self, parent=None, **kwargs):
        self.parent = parent

    def transient(self, *args):
        pass

    def grab_set(self):
        pass

    def geometry(self, *args):
        pass

    def update_idletasks(self):
        pass

    def title(self, *args):
        pass

    def winfo_rootx(self):
        return 0

    def winfo_rooty(self):
        return 0

    def winfo_width(self):
        return 100

    def winfo_height(self):
        return 100

    def destroy(self):
        pass


# Mock tkinter before importing the module under test
mock_tk = MagicMock()
mock_tk.Toplevel = MockToplevel  # Use the Mock class that accepts args
sys.modules["tkinter"] = mock_tk
sys.modules["tkinter.ttk"] = MagicMock()
sys.modules["tkinter.messagebox"] = MagicMock()
sys.modules["tkinter.filedialog"] = MagicMock()

# Now import
from ui.dialogs.compare_dialog import CompareDialog


@pytest.fixture
def mock_settings_service():
    service = MagicMock()
    service.get_merge_tool_config.return_value = {
        "name": "TestTool",
        "path": "test_tool.exe",
        "args_2way": "{left} {right}",
        "args_3way": "{base} {left} {right}",
    }
    return service


@pytest.fixture
def mock_registry_service():
    service = MagicMock()
    return service


@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.winfo_toplevel.return_value = parent
    parent.winfo_rootx.return_value = 0
    parent.winfo_rooty.return_value = 0
    parent.winfo_width.return_value = 100
    parent.winfo_height.return_value = 100
    return parent


class TestCompareDialog:
    """Tests for CompareDialog logic."""


def test_launch_2way(mock_parent, mock_settings_service, mock_registry_service):
    """Test generating 2-way compare command."""
    files = [Path("c:/file1.txt"), Path("c:/file2.txt")]

    # We need to ensure logic works. Logic uses self.left_var etc. which are tk.StringVar.
    # We need to mock StringVar too.

    class MockVar:
        def __init__(self, value=""):
            self._val = value

        def get(self):
            return self._val

        def set(self, v):
            self._val = v

    mock_tk.StringVar = MockVar

    # Mock ttk.Combobox, Button, Label, Frame to avoid errors during _setup_ui
    # The mocks in sys.modules might be enough if they return Mocks that accept calls.

    dialog = CompareDialog(
        mock_parent, mock_settings_service, mock_registry_service, files
    )

    # Override selections for the test case
    dialog.left_var = MockVar("file1.txt")
    dialog.right_var = MockVar("file2.txt")
    dialog.base_var = MockVar("")
    dialog.file_map = {
        "file1.txt": Path("c:/file1.txt"),
        "file2.txt": Path("c:/file2.txt"),
    }

    with patch("subprocess.Popen") as mock_popen:
        dialog._launch()

        expected_cmd = '"test_tool.exe" c:\\file1.txt c:\\file2.txt'
        mock_popen.assert_called_once()
        args, _ = mock_popen.call_args
        assert args[0] == expected_cmd


def test_launch_3way(mock_parent, mock_settings_service, mock_registry_service):
    """Test generating 3-way compare command."""
    files = [Path("c:/left.txt"), Path("c:/right.txt"), Path("c:/base.txt")]

    class MockVar:
        def __init__(self, value=""):
            self._val = value

        def get(self):
            return self._val

        def set(self, v):
            self._val = v

    mock_tk.StringVar = MockVar

    dialog = CompareDialog(
        mock_parent, mock_settings_service, mock_registry_service, files
    )

    dialog.left_var = MockVar("left.txt")
    dialog.right_var = MockVar("right.txt")
    dialog.base_var = MockVar("base.txt")
    dialog.file_map = {
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
    mock_parent, mock_settings_service, mock_registry_service
):
    """Test handling of paths with spaces."""
    files = [Path("c:/path with spaces/file1.txt"), Path("c:/file2.txt")]

    class MockVar:
        def __init__(self, value=""):
            self._val = value

        def get(self):
            return self._val

        def set(self, v):
            self._val = v

    mock_tk.StringVar = MockVar

    dialog = CompareDialog(
        mock_parent, mock_settings_service, mock_registry_service, files
    )

    dialog.left_var = MockVar("file1.txt")
    dialog.right_var = MockVar("file2.txt")
    dialog.base_var = MockVar("")
    dialog.file_map = {
        "file1.txt": Path("c:/path with spaces/file1.txt"),
        "file2.txt": Path("c:/file2.txt"),
    }

    with patch("subprocess.Popen") as mock_popen:
        dialog._launch()
        expected_cmd = '"test_tool.exe" "c:\\path with spaces\\file1.txt" c:\\file2.txt'
        mock_popen.assert_called_once()
        assert mock_popen.call_args[0][0] == expected_cmd
