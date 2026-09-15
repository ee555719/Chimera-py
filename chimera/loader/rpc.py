# SPDX-License-Identifier: AGPL-3.0-or-later
"""JSON-RPC 2.0 server and client for plugin communication."""

import json
import sys
import threading
from typing import Any, Dict, Callable, Optional
from dataclasses import dataclass


@dataclass
class RPCRequest:
    """JSON-RPC request."""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Any = None
    id: Optional[int] = None


@dataclass
class RPCResponse:
    """JSON-RPC response."""
    jsonrpc: str = "2.0"
    result: Any = None
    error: Optional[Dict] = None
    id: Optional[int] = None


class RPCServer:
    """JSON-RPC server that reads from stdin and writes to stdout."""

    def __init__(self):
        self._methods: Dict[str, Callable] = {}
        self._request_id = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def register_method(self, name: str, handler: Callable):
        """Register an RPC method."""
        self._methods[name] = handler

    def start(self):
        """Start the RPC server in a background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the RPC server."""
        self._running = False

    def _run(self):
        """Main loop for the RPC server."""
        while self._running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line.strip())
                response = self._handle_request(request)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = RPCResponse(
                    error={"code": -32603, "message": str(e)},
                    id=None
                )
                sys.stdout.write(json.dumps(error_response.__dict__) + "\n")
                sys.stdout.flush()

    def _handle_request(self, request: dict) -> Optional[RPCResponse]:
        """Handle an incoming RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        if method not in self._methods:
            return RPCResponse(
                error={"code": -32601, "message": f"Method not found: {method}"},
                id=request_id
            )

        try:
            result = self._methods[method](params)
            return RPCResponse(result=result, id=request_id)
        except Exception as e:
            return RPCResponse(
                error={"code": -32603, "message": str(e)},
                id=request_id
            )


class RPCClient:
    """JSON-RPC client for calling plugin methods."""

    def __init__(self):
        self._request_id = 0

    def call(self, method: str, params: Any = None) -> Dict:
        """Send an RPC request and wait for response."""
        self._request_id += 1
        request = RPCRequest(
            method=method,
            params=params,
            id=self._request_id
        )

        request_json = json.dumps(request.__dict__) + "\n"
        sys.stdout.write(request_json)
        sys.stdout.flush()

        response_line = sys.stdin.readline()
        if response_line:
            return json.loads(response_line.strip())
        return {"error": {"code": -32000, "message": "No response"}}


def send_rpc_response(result: Any = None, error: Optional[Dict] = None):
    """Send an RPC response to stdout."""
    response = RPCResponse(result=result, error=error)
    sys.stdout.write(json.dumps(response.__dict__) + "\n")
    sys.stdout.flush()
