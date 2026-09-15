# SPDX-License-Identifier: AGPL-3.0-or-later
"""Settings manager for Chimera."""

import json
from pathlib import Path
from typing import Any
from PySide6.QtCore import QObject, Signal


class SettingsManager(QObject):
    """Manages application settings."""

    settings_changed = Signal(str, object)

    def __init__(self, config_dir: Path):
        super().__init__()
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self.config_dir / "settings.json"
        self._data = self._load()

    def _load(self) -> dict:
        """Load settings from file."""
        if self._config_file.exists():
            try:
                return json.loads(self._config_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "theme": "dark",
            "plugin_store_url": "",
            "signature_verification": True,
            "trusted_developers": [],
        }

    def _save(self):
        """Save settings to file."""
        self._config_file.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value."""
        self._data[key] = value
        self._save()
        self.settings_changed.emit(key, value)

    @property
    def theme(self) -> str:
        return self.get("theme", "dark")

    @theme.setter
    def theme(self, value: str):
        self.set("theme", value)

    @property
    def plugin_store_url(self) -> str:
        return self.get("plugin_store_url", "")

    @plugin_store_url.setter
    def plugin_store_url(self, value: str):
        self.set("plugin_store_url", value)
