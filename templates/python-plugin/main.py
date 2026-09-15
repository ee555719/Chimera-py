# SPDX-License-Identifier: AGPL-3.0-or-later
"""Template for Chimera plugins."""

import sys
import json
from chimera.sdk.chimera_sdk import create_sdk

# Initialize SDK
sdk = create_sdk("{{PLUGIN_ID}}")


def on_ready(params):
    """Called when plugin is ready."""
    print(json.dumps({
        "jsonrpc": "2.0",
        "result": "ready",
        "id": params.get("id")
    }))
    sys.stdout.flush()


def on_shutdown(params):
    """Called when plugin is shutting down."""
    pass


def main():
    """Main entry point."""
    # Register RPC handlers
    handlers = {
        "plugin.ready": on_ready,
        "plugin.shutdown": on_shutdown,
    }

    # Read commands from stdin
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
                response = {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": request_id
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            continue
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
