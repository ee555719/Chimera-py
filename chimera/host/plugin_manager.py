# SPDX-License-Identifier: AGPL-3.0-or-later
"""Plugin manager for Chimera."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal


@dataclass
class PluginInfo:
    """Information about a plugin."""
    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    enabled: bool = True
    path: Optional[Path] = None
    manifest: Dict = field(default_factory=dict)


class PluginManager(QObject):
    """Manages plugins."""

    plugin_loaded = Signal(str)
    plugin_unloaded = Signal(str)
    plugin_enabled = Signal(str)
    plugin_disabled = Signal(str)

    def __init__(self, plugins_dir: Path):
        super().__init__()
        self.plugins_dir = plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self._plugins: Dict[str, PluginInfo] = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load all plugins from the plugins directory."""
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_file = plugin_dir / "plugin.json"
                if manifest_file.exists():
                    try:
                        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                        info = PluginInfo(
                            id=manifest.get("id", plugin_dir.name),
                            name=manifest.get("name", plugin_dir.name),
                            version=manifest.get("version", "0.1.0"),
                            description=manifest.get("description", ""),
                            author=manifest.get("author", ""),
                            enabled=manifest.get("enabled", True),
                            path=plugin_dir,
                            manifest=manifest,
                        )
                        self._plugins[info.id] = info
                    except Exception as e:
                        print(f"Failed to load plugin {plugin_dir.name}: {e}")

    def get_plugin(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get a plugin by ID."""
        return self._plugins.get(plugin_id)

    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all plugins."""
        return list(self._plugins.values())

    def get_enabled_plugins(self) -> List[PluginInfo]:
        """Get all enabled plugins."""
        return [p for p in self._plugins.values() if p.enabled]

    def install_plugin(self, zip_path: Path) -> bool:
        """Install a plugin from a ZIP file."""
        import zipfile
        import shutil

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract to temp directory
                temp_dir = self.plugins_dir / "_temp"
                zip_ref.extractall(temp_dir)

                # Find the plugin directory
                for item in temp_dir.iterdir():
                    if item.is_dir():
                        manifest_file = item / "plugin.json"
                        if manifest_file.exists():
                            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                            plugin_id = manifest.get("id", item.name)
                            target_dir = self.plugins_dir / plugin_id
                            if target_dir.exists():
                                shutil.rmtree(target_dir)
                            shutil.move(str(item), str(target_dir))
                            self._load_plugins()
                            self.plugin_loaded.emit(plugin_id)
                            break

                shutil.rmtree(temp_dir, ignore_errors=True)
            return True
        except Exception as e:
            print(f"Failed to install plugin: {e}")
            return False

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin."""
        import shutil
        plugin = self._plugins.get(plugin_id)
        if plugin and plugin.path and plugin.path.exists():
            try:
                shutil.rmtree(plugin.path)
                del self._plugins[plugin_id]
                self.plugin_unloaded.emit(plugin_id)
                return True
            except Exception as e:
                print(f"Failed to uninstall plugin: {e}")
        return False

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin."""
        plugin = self._plugins.get(plugin_id)
        if plugin:
            plugin.enabled = True
            self._update_manifest(plugin)
            self.plugin_enabled.emit(plugin_id)
            return True
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin."""
        plugin = self._plugins.get(plugin_id)
        if plugin:
            plugin.enabled = False
            self._update_manifest(plugin)
            self.plugin_disabled.emit(plugin_id)
            return True
        return False

    def _update_manifest(self, plugin: PluginInfo):
        """Update the plugin manifest file."""
        if plugin.path:
            manifest_file = plugin.path / "plugin.json"
            manifest_file.write_text(
                json.dumps(plugin.manifest, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
