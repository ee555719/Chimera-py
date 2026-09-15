# SPDX-License-Identifier: AGPL-3.0-or-later
"""Main entry point for Chimera application."""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from chimera.host.main_window import MainWindow
from chimera.host.settings import SettingsManager
from chimera.host.theme import ThemeManager
from chimera.host.plugin_manager import PluginManager
from chimera.loader.rpc import RPCServer


def get_data_dir() -> Path:
    """Get the data directory for Chimera."""
    if os.environ.get("CHIMERA_PORTABLE"):
        return Path(os.environ.get("CHIMERA_PORTABLE"))
    return Path("D:/Chimera")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Chimera")
    app.setOrganizationName("Chimera")

    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    settings = SettingsManager(data_dir / "config")
    theme = ThemeManager(settings)
    plugin_mgr = PluginManager(data_dir / "plugins")

    rpc_server = RPCServer()

    window = MainWindow(settings, theme, plugin_mgr, rpc_server)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
