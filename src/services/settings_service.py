import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, cast


class SettingsService:
    """
    Manages loading and saving of application settings.
    """

    DEFAULT_SETTINGS = {
        "merge_tool": {"name": "manual", "path": "", "args_2way": "", "args_3way": ""}
    }

    def __init__(self, settings_path: Optional[str] = None):
        """
        Initialize the SettingsService.

        Args:
            settings_path: Path to the settings JSON file.
                           If None, defaults to sample_data/.apm/settings.json relative to project root
                           or user home if that doesn't exist (logic can be refined).
                           For now, we'll aim for a specific default location.
        """
        if settings_path:
            self.settings_file = Path(settings_path)
        else:
            # Default to local .apm folder for this project structure
            # Assuming we are running from project root, but let's be robust
            # We will use the location defined in rules or standard convention
            self.settings_file = Path("sample_data/.apm/settings.json")

        self._settings: Dict[str, Any] = self.DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> None:
        """Load settings from the JSON file."""
        if not self.settings_file.exists():
            return

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Deep merge could be better, but for now simple update
                self._settings.update(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading settings from {self.settings_file}: {e}")

    def save(self) -> None:
        """Save current settings to the JSON file."""
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
        except OSError as e:
            print(f"Error saving settings to {self.settings_file}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by key."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self._settings[key] = value
        self.save()

    def get_merge_tool_config(self) -> Dict[str, str]:
        """Get the merge tool configuration."""
        return cast(
            Dict[str, str],
            self._settings.get("merge_tool", self.DEFAULT_SETTINGS["merge_tool"]),
        )

    def set_merge_tool_config(self, config: Dict[str, str]) -> None:
        """Set the merge tool configuration."""
        # Validate keys if necessary
        self._settings["merge_tool"] = config
        self.save()
