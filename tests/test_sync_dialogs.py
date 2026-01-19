"""Tests for sync dialogs."""

import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest

# Mock tkinter before importing dialogs
mock_tk = MagicMock()
mock_tk.Tk = MagicMock()


class MockToplevel:
    def __init__(self, *args, **kwargs):
        self.title_val = None
        self.transient_val = None
        self.master = MagicMock()
        self.master.winfo_rootx.return_value = 0
        self.master.winfo_rooty.return_value = 0
        self.master.winfo_width.return_value = 1000
        self.master.winfo_height.return_value = 800

    def title(self, val=None):
        if val:
            self.title_val = val
        return self.title_val

    def transient(self, master=None):
        self.transient_val = master

    def grab_set(self):
        pass

    def wait_window(self):
        pass

    def geometry(self, *args):
        pass

    def resizable(self, *args):
        pass

    def update_idletasks(self):
        pass

    def destroy(self):
        pass


mock_tk.Toplevel = MockToplevel
sys.modules["tkinter"] = mock_tk
sys.modules["tkinter.ttk"] = MagicMock()

from models.ingredient import Ingredient
from models.sync_types import SyncAction, SyncStatus, SyncTask
from ui.dialogs.sync_dialogs import UpdateAvailableDialog, LocalChangesDialog


@pytest.fixture
def mock_task():
    return SyncTask(
        ingredient=Ingredient(
            name="test",
            path=Path("test.md"),
            description="desc",
            type="GUIDE",
            major=1,
            minor=0,
            basename="test",
        ),
        source_path=Path("/source/test.md"),
        target_path=Path("/target/test.md"),
        source_mtime=100.0,
        target_mtime=200.0,
        status=SyncStatus.SOURCE_NEWER,
    )


class TestSyncDialogs:

    def test_update_available_dialog_init(self, mock_task):
        parent = MagicMock()

        # Instantiate dialog directly
        dialog = UpdateAvailableDialog(parent, mock_task)

        # Verify title was set
        assert dialog.title_val == "Update Available"

        # Verify transient call
        assert dialog.transient_val == parent

        # Verify task is set
        assert dialog.task == mock_task

    def test_local_changes_dialog_init(self, mock_task):
        parent = MagicMock()

        dialog = LocalChangesDialog(parent, mock_task)

        assert dialog.title_val == "Local Changes Detected"
        assert dialog.transient_val == parent
        assert dialog.task == mock_task
