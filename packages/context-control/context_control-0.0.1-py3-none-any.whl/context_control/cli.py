"""
Console entry points for Context Control.
"""

from __future__ import annotations

import argparse
import json
import sys

import uvicorn

from .api import create_app
from .mcp_server import run as run_mcp_server


def run_api() -> None:
    """Run the FastAPI server with uvicorn."""

    parser = argparse.ArgumentParser(description="Run the Context Control API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development only)")
    args = parser.parse_args()

    uvicorn.run(create_app(), host=args.host, port=args.port, reload=args.reload)


def run_mcp() -> None:
    """Run the JSON-based MCP-style server."""

    parser = argparse.ArgumentParser(description="Run the Context Control MCP server")
    parser.add_argument("--mode", choices=["local", "remote"], default="local")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    try:
        run_mcp_server(mode=args.mode, base_url=args.base_url)
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        sys.stderr.write(json.dumps({"message": "Context Control MCP server stopped."}) + "\n")

