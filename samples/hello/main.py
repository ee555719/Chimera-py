# SPDX-License-Identifier: AGPL-3.0-or-later
"""Hello World plugin for Chimera."""

import sys
import json
from chimera.sdk.chimera_sdk import create_sdk

sdk = create_sdk("hello")


def on_ready(params):
    """Called when plugin is ready."""
    sdk.show_message("你好", "Hello World 插件已加载！")
    return "ready"


def main():
    """Main entry point."""
    handlers = {
        "plugin.ready": on_ready,
    }

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line.strip())
            method = request.get("method", "")
            params = request.get("params", {})
            request_id = request.get("id")

            if method in handlers:
                result = handlers[method](params)
                response = {"jsonrpc": "2.0", "result": result, "id": request_id}
            else:
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": request_id
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": None
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
