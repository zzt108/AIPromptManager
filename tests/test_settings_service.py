import json
import pytest
from pathlib import Path
from src.services.settings_service import SettingsService


@pytest.fixture
def temp_settings_file(tmp_path):
    return tmp_path / "settings.json"


def test_load_defaults(temp_settings_file):
    """Test that defaults are loaded when file doesn't exist."""
    service = SettingsService(str(temp_settings_file))
    config = service.get_merge_tool_config()
    assert config["name"] == "manual"
    assert not temp_settings_file.exists()  # Shouldn't create file just by loading


def test_save_and_load(temp_settings_file):
    """Test saving settings and reloading them."""
    service = SettingsService(str(temp_settings_file))

    new_config = {
        "name": "custom_tool",
        "path": "c:/tool.exe",
        "args_2way": "{l} {r}",
        "args_3way": "{b} {l} {r}",
    }
    service.set_merge_tool_config(new_config)

    assert temp_settings_file.exists()

    # Reload in new instance
    service2 = SettingsService(str(temp_settings_file))
    loaded_config = service2.get_merge_tool_config()
    assert loaded_config == new_config


def test_partial_load(temp_settings_file):
    """Test loading a file with partial settings."""
    partial_data = {"some_other_setting": 123}
    with open(temp_settings_file, "w") as f:
        json.dump(partial_data, f)

    service = SettingsService(str(temp_settings_file))
    # Should still have defaults for merge_tool
    assert service.get_merge_tool_config()["name"] == "manual"
    # And should have the new setting
    assert service.get("some_other_setting") == 123
