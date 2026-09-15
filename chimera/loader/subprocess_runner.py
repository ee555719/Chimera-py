# SPDX-License-Identifier: AGPL-3.0-or-later
"""Subprocess runner for Python plugins."""

import subprocess
import json
import sys
import threading
from typing import Any, Dict, Optional, Callable
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PluginProcess:
    """Represents a running plugin process."""
    process: subprocess.Popen
    plugin_id: str
    rpc_id: int = 0
    callbacks: Dict[int, Callable] = None

    def __post_init__(self):
        if self.callbacks is None:
            self.callbacks = {}


class SubprocessRunner:
    """Runs Python plugins in isolated subprocesses."""

    def __init__(self):
        self._processes: Dict[str, PluginProcess] = {}
        self._read_threads: Dict[str, threading.Thread] = {}

    def start_plugin(self, plugin_id: str, plugin_path: Path) -> bool:
        """Start a plugin in a subprocess."""
        main_py = plugin_path / "main.py"
        if not main_py.exists():
            return False

        try:
            process = subprocess.Popen(
                [sys.executable, str(main_py)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            plugin_process = PluginProcess(process=process, plugin_id=plugin_id)
            self._processes[plugin_id] = plugin_process

            # Start read thread
            thread = threading.Thread(
                target=self._read_output,
                args=(plugin_id,),
                daemon=True,
            )
            self._read_threads[plugin_id] = thread
            thread.start()

            return True

        except Exception as e:
            print(f"Failed to start plugin {plugin_id}: {e}")
            return False

    def stop_plugin(self, plugin_id: str):
        """Stop a plugin process."""
        if plugin_id in self._processes:
            pp = self._processes[plugin_id]
            try:
                pp.process.terminate()
                pp.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pp.process.kill()
            del self._processes[plugin_id]

    def call_method(self, plugin_id: str, method: str, params: Any = None) -> Dict:
        """Call a method on a plugin via RPC."""
        if plugin_id not in self._processes:
            return {"error": {"code": -32000, "message": "Plugin not running"}}

        pp = self._processes[plugin_id]
        pp.rpc_id += 1

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": pp.rpc_id,
        }

        try:
            pp.process.stdin.write(json.dumps(request) + "\n")
            pp.process.stdin.flush()
            return {"id": pp.rpc_id}
        except Exception as e:
            return {"error": {"code": -32003, "message": str(e)}}

    def _read_output(self, plugin_id: str):
        """Read output from a plugin process."""
        if plugin_id not in self._processes:
            return

        pp = self._processes[plugin_id]
        while plugin_id in self._processes:
            try:
                line = pp.process.stdout.readline()
                if not line:
                    break

                response = json.loads(line.strip())
                request_id = response.get("id")
                if request_id and request_id in pp.callbacks:
                    pp.callbacks[request_id](response)

            except json.JSONDecodeError:
                continue
            except Exception:
                break

    def is_running(self, plugin_id: str) -> bool:
        """Check if a plugin is running."""
        if plugin_id in self._processes:
            return self._processes[plugin_id].process.poll() is None
        return False
