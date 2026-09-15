# SPDX-License-Identifier: AGPL-3.0-or-later
"""PyInstaller builder for creating standalone executables."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class BuildConfig:
    """Build configuration."""
    name: str
    version: str = "1.0.0"
    icon: Optional[Path] = None
    plugins: List[Path] = None
    data_files: List[tuple] = None
    hidden_imports: List[str] = None

    def __post_init__(self):
        if self.plugins is None:
            self.plugins = []
        if self.data_files is None:
            self.data_files = []
        if self.hidden_imports is None:
            self.hidden_imports = []


class PyInstallerBuilder:
    """Builds standalone executables using PyInstaller."""

    def __init__(self):
        self._pyinstaller = self._find_pyinstaller()

    def _find_pyinstaller(self) -> str:
        """Find PyInstaller executable."""
        if sys.platform == "win32":
            return "pyinstaller.exe"
        return "pyinstaller"

    def build(self, config: BuildConfig, output_dir: Path) -> Optional[Path]:
        """
        Build a standalone executable.
        
        Returns the path to the built executable if successful.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            self._pyinstaller,
            "--onefile",
            "--name", config.name,
            "--distpath", str(output_dir),
            "--workpath", str(output_dir / "build"),
            "--specpath", str(output_dir),
        ]

        if config.icon and config.icon.exists():
            cmd.extend(["--icon", str(config.icon)])

        for plugin_path in config.plugins:
            if plugin_path.exists():
                cmd.extend(["--add-data", f"{plugin_path};plugins"])

        for src, dst in config.data_files:
            cmd.extend(["--add-data", f"{src};{dst}"])

        for imp in config.hidden_imports:
            cmd.extend(["--hidden-import", imp])

        cmd.append(str(Path(__file__).parent.parent.parent / "chimera" / "app.py"))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                exe_path = output_dir / f"{config.name}.exe"
                if exe_path.exists():
                    return exe_path

            print(f"Build failed:\n{result.stderr}")
            return None

        except subprocess.TimeoutExpired:
            print("Build timed out")
            return None
        except Exception as e:
            print(f"Build error: {e}")
            return None
