# SPDX-License-Identifier: AGPL-3.0-or-later
"""ZIP installer for plugins."""

import zipfile
import json
import shutil
from pathlib import Path
from typing import Optional, Dict


class ZIPInstaller:
    """Installs plugins from ZIP files."""

    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir

    def install(self, zip_path: Path, force: bool = False) -> Optional[str]:
        """
        Install a plugin from a ZIP file.
        
        ZIP structure should be:
        plugin_name/
            main.py
            plugin.json
            library.txt (optional)
            
        Returns the plugin ID if successful, None otherwise.
        """
        if not zip_path.exists():
            return None

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Extract to temp directory
                temp_dir = self.plugins_dir / "_temp_install"
                temp_dir.mkdir(exist_ok=True)
                
                zf.extractall(temp_dir)

                # Find the plugin root (directory containing main.py or plugin.json)
                plugin_root = self._find_plugin_root(temp_dir)
                if not plugin_root:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return None

                # Read manifest
                manifest_file = plugin_root / "plugin.json"
                if not manifest_file.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return None

                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                plugin_id = manifest.get("id", plugin_root.name)

                # Move to plugins directory
                target_dir = self.plugins_dir / plugin_id
                if target_dir.exists():
                    if force:
                        shutil.rmtree(target_dir)
                    else:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        return None

                shutil.move(str(plugin_root), str(target_dir))
                shutil.rmtree(temp_dir, ignore_errors=True)

                return plugin_id

        except Exception as e:
            print(f"Installation failed: {e}")
            return None

    def _find_plugin_root(self, directory: Path) -> Optional[Path]:
        """Find the plugin root directory."""
        # Check if directory itself is a plugin
        if (directory / "main.py").exists() or (directory / "plugin.json").exists():
            return directory

        # Check subdirectories
        for item in directory.iterdir():
            if item.is_dir():
                if (item / "main.py").exists() or (item / "plugin.json").exists():
                    return item

        return None

    def create_plugin_zip(self, plugin_dir: Path, output_path: Path) -> bool:
        """Create a ZIP file from a plugin directory."""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file in plugin_dir.rglob("*"):
                    if file.is_file():
                        arcname = file.relative_to(plugin_dir.parent)
                        zf.write(file, arcname)
            return True
        except Exception as e:
            print(f"Failed to create ZIP: {e}")
            return False
