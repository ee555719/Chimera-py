# SPDX-License-Identifier: AGPL-3.0-or-later
"""Chimera SDK for plugin development."""

import json
import sys
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass


@dataclass
class PluginContext:
    """Context provided to plugins."""
    plugin_id: str
    data_dir: str


class ChimeraSDK:
    """SDK for Chimera plugins."""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self._rpc_id = 0
        self._callbacks: Dict[str, Callable] = {}

    def _send_request(self, method: str, params: Any = None) -> Any:
        """Send an RPC request to the host."""
        self._rpc_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self._rpc_id,
        }
        sys.stdout.write(json.dumps(request) + "\n")
        sys.stdout.flush()

        response_line = sys.stdin.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "error" in response and response["error"]:
                raise Exception(response["error"].get("message", "Unknown error"))
            return response.get("result")
        return None

    # UI methods
    def show_message(self, title: str, message: str, msg_type: str = "info"):
        """Show a message to the user."""
        return self._send_request("ui.show_message", {
            "title": title,
            "message": message,
            "type": msg_type,
        })

    def show_input(self, title: str, prompt: str, default: str = "") -> Optional[str]:
        """Show an input dialog."""
        return self._send_request("ui.show_input", {
            "title": title,
            "prompt": prompt,
            "default": default,
        })

    def add_menu_item(self, menu: str, label: str, callback_id: str):
        """Add a menu item."""
        return self._send_request("ui.add_menu", {
            "menu": menu,
            "label": label,
            "callback_id": callback_id,
        })

    def add_status_bar(self, text: str):
        """Add text to the status bar."""
        return self._send_request("ui.status_bar", {"text": text})

    # File system methods
    def read_file(self, path: str) -> str:
        """Read a file."""
        return self._send_request("fs.read", {"path": path})

    def write_file(self, path: str, content: str):
        """Write a file."""
        return self._send_request("fs.write", {"path": path, "content": content})

    def list_dir(self, path: str) -> list:
        """List a directory."""
        return self._send_request("fs.list", {"path": path})

    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        return self._send_request("fs.exists", {"path": path})

    # Network methods
    def http_get(self, url: str, headers: Dict = None) -> Dict:
        """Make an HTTP GET request."""
        return self._send_request("net.get", {"url": url, "headers": headers or {}})

    def http_post(self, url: str, data: Any = None, headers: Dict = None) -> Dict:
        """Make an HTTP POST request."""
        return self._send_request("net.post", {
            "url": url,
            "data": data,
            "headers": headers or {},
        })

    # Settings methods
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._send_request("settings.get", {"key": key, "default": default})

    def set_setting(self, key: str, value: Any):
        """Set a setting value."""
        return self._send_request("settings.set", {"key": key, "value": value})

    # Process methods
    def run_command(self, command: str, args: list = None) -> Dict:
        """Run a system command."""
        return self._send_request("process.run", {"command": command, "args": args or []})

    # Event methods
    def emit_event(self, event_name: str, data: Any = None):
        """Emit an event."""
        return self._send_request("event.emit", {"event": event_name, "data": data})

    def on_event(self, event_name: str, callback: Callable):
        """Register an event handler."""
        self._callbacks[event_name] = callback
        return self._send_request("event.on", {"event": event_name})


def create_sdk(plugin_id: str) -> ChimeraSDK:
    """Create an SDK instance for a plugin."""
    return ChimeraSDK(plugin_id)
