"""Tests for sync dialogs."""

import sys
from unittest.mock import MagicMock, patch
from pathlib import Path
from typing import Any, Generator, Optional
import tkinter as tk

import pytest


@pytest.fixture
def mock_tkinter_modules() -> Generator[Any, None, None]:
    """Patch tkinter and ttk modules for these tests."""
    mock_tk = MagicMock()
    mock_tk.Tk = MagicMock()
    mock_tk.Toplevel = MockToplevel

    with patch.dict(sys.modules, {"tkinter": mock_tk, "tkinter.ttk": MagicMock()}):
        # We must import the module UNDER TEST inside the patch so it picks up the mocks
        if "ui.dialogs.sync_dialogs" in sys.modules:
            del sys.modules["ui.dialogs.sync_dialogs"]
        import ui.dialogs.sync_dialogs

        yield ui.dialogs.sync_dialogs


# Move MockToplevel definition here to be accessible
class MockToplevel:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.title_val: Optional[str] = None
        self.transient_val: Optional[tk.Widget] = None
        self.master = MagicMock()
        self.master.winfo_rootx.return_value = 0
        self.master.winfo_rooty.return_value = 0
        self.master.winfo_width.return_value = 1000
        self.master.winfo_height.return_value = 800

    def title(self, val: Optional[str] = None) -> Optional[str]:
        if val:
            self.title_val = val
        return self.title_val

    def transient(self, master: Optional[tk.Widget] = None) -> None:
        self.transient_val = master

    def grab_set(self) -> None:
        pass

    def wait_window(self) -> None:
        pass

    def geometry(self, *args: Any) -> None:
        pass

    def resizable(self, *args: Any) -> None:
        pass

    def update_idletasks(self) -> None:
        pass

    def destroy(self) -> None:
        pass


from models.skill import Skill
from models.sync_types import SyncAction, SyncStatus, SyncTask


@pytest.fixture
def mock_task() -> SyncTask:
    return SyncTask(
        skill=Skill(
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

    def test_update_available_dialog_init(
        self, mock_tkinter_modules: Any, mock_task: SyncTask
    ) -> None:
        sync_dialogs = mock_tkinter_modules
        parent = MagicMock()

        # Instantiate dialog directly
        dialog = sync_dialogs.UpdateAvailableDialog(parent, mock_task)

        # Verify title was set
        assert dialog.title_val == "Update Available"

        # Verify transient call
        assert dialog.transient_val == parent

        # Verify task is set
        assert dialog.task == mock_task

    def test_local_changes_dialog_init(
        self, mock_tkinter_modules: Any, mock_task: SyncTask
    ) -> None:
        sync_dialogs = mock_tkinter_modules
        parent = MagicMock()

        dialog = sync_dialogs.LocalChangesDialog(parent, mock_task)

        assert dialog.title_val == "Local Changes Detected"
        assert dialog.transient_val == parent
        assert dialog.task == mock_task
