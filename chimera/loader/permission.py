# SPDX-License-Identifier: AGPL-3.0-or-later
"""Permission management for plugins."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class PermissionLevel(Enum):
    """Permission levels."""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    FULL = "full"


@dataclass
class PluginPermission:
    """Permission request from a plugin."""
    plugin_id: str
    permission: str
    level: PermissionLevel = PermissionLevel.BASIC
    description: str = ""
    granted: bool = False


class PermissionManager:
    """Manages plugin permissions."""

    REQUIRED_PERMISSIONS = {
        "ui": PermissionLevel.BASIC,
        "fs": PermissionLevel.ADVANCED,
        "net": PermissionLevel.ADVANCED,
        "process": PermissionLevel.FULL,
        "clipboard": PermissionLevel.BASIC,
        "settings": PermissionLevel.ADVANCED,
    }

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._permissions_file = self.config_dir / "permissions.json"
        self._permissions: Dict[str, Dict[str, bool]] = self._load()

    def _load(self) -> Dict[str, Dict[str, bool]]:
        """Load permissions from file."""
        if self._permissions_file.exists():
            try:
                return json.loads(self._permissions_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save(self):
        """Save permissions to file."""
        self._permissions_file.write_text(
            json.dumps(self._permissions, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def request_permission(self, plugin_id: str, permission: str) -> bool:
        """Request a permission for a plugin."""
        if permission in self._permissions.get(plugin_id, {}):
            return self._permissions[plugin_id][permission]

        # Auto-grant basic permissions
        level = self.REQUIRED_PERMISSIONS.get(permission, PermissionLevel.BASIC)
        if level == PermissionLevel.BASIC:
            self.grant_permission(plugin_id, permission)
            return True

        # For advanced/full permissions, deny by default
        return False

    def grant_permission(self, plugin_id: str, permission: str):
        """Grant a permission to a plugin."""
        if plugin_id not in self._permissions:
            self._permissions[plugin_id] = {}
        self._permissions[plugin_id][permission] = True
        self._save()

    def revoke_permission(self, plugin_id: str, permission: str):
        """Revoke a permission from a plugin."""
        if plugin_id in self._permissions:
            self._permissions[plugin_id][permission] = False
            self._save()

    def has_permission(self, plugin_id: str, permission: str) -> bool:
        """Check if a plugin has a permission."""
        return self._permissions.get(plugin_id, {}).get(permission, False)

    def get_plugin_permissions(self, plugin_id: str) -> Dict[str, bool]:
        """Get all permissions for a plugin."""
        return self._permissions.get(plugin_id, {})

    def revoke_all(self, plugin_id: str):
        """Revoke all permissions for a plugin."""
        if plugin_id in self._permissions:
            del self._permissions[plugin_id]
            self._save()
