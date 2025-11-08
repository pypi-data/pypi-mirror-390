"""
Minimal JSON-over-stdio server that exposes Context Control operations.

This is not a full MCP reference implementation, but it follows the same
spirit: clients send newline-delimited JSON commands and receive JSON responses.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from .client import ContextControlClient
from .models import ContextPackage, MemoryCreate, PromptCreate


def _error_response(request_id: Any, message: str) -> Dict[str, Any]:
    return {"id": request_id, "error": {"message": message}}


def _success_response(request_id: Any, result: Any) -> Dict[str, Any]:
    return {"id": request_id, "result": result}


def _dump_model(model: Any) -> Any:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model


def _dump_collection(items: Any) -> Any:
    if isinstance(items, list):
        return [_dump_model(item) for item in items]
    return _dump_model(items)


def run(*, mode: str = "local", base_url: str = "http://127.0.0.1:8000") -> None:
    """
    Start the MCP-style server that communicates over stdin/stdout.

    Supported commands (send as JSON per line):
      {"id": 1, "command": "list_contexts"}
      {"id": 2, "command": "get_context", "params": {"agent_name": "agent", "label": "prod"}}
      {"id": 3, "command": "upsert_context", "params": {...}}
      {"id": 4, "command": "log_prompt", "params": {...}}
      {"id": 5, "command": "create_memory", "params": {...}}
      {"id": 6, "command": "list_memories", "params": {...}}
      {"id": 7, "command": "delete_memory", "params": {"memory_id": 1}}
    """

    client = ContextControlClient(mode=mode, base_url=base_url)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps(_error_response(None, "Invalid JSON")) + "\n")
            sys.stdout.flush()
            continue

        request_id = request.get("id")
        command = request.get("command")
        params = request.get("params", {}) or {}

        try:
            if command == "ping":
                response = _success_response(request_id, {"message": "pong"})

            elif command == "list_contexts":
                response = _success_response(
                    request_id,
                    _dump_collection(client.list_contexts(params.get("agent_name"))),
                )

            elif command == "get_context":
                envelope = client.get_context(params["agent_name"], params["label"])
                response = _success_response(request_id, _dump_model(envelope))

            elif command == "upsert_context":
                package = ContextPackage.model_validate(params["package"])
                envelope = client.upsert_context(params["agent_name"], params["label"], package)
                response = _success_response(request_id, _dump_model(envelope))

            elif command == "delete_context":
                client.delete_context(params["agent_name"], params["label"])
                response = _success_response(request_id, {"deleted": True})

            elif command == "log_prompt":
                prompt = PromptCreate.model_validate(params)
                record = client.log_prompt(prompt)
                response = _success_response(request_id, _dump_model(record))

            elif command == "list_prompts":
                prompts = client.list_prompts(params.get("agent_name"), params.get("label"))
                response = _success_response(request_id, _dump_collection(prompts))

            elif command == "create_memory":
                memory = MemoryCreate.model_validate(params)
                record = client.create_memory(memory)
                response = _success_response(request_id, _dump_model(record))

            elif command == "list_memories":
                memories = client.list_memories(
                    agent_name=params.get("agent_name"),
                    user_id=params.get("user_id"),
                    include_general=params.get("include_general", True),
                    limit=params.get("limit", 200),
                )
                response = _success_response(request_id, _dump_collection(memories))

            elif command == "delete_memory":
                client.delete_memory(params["memory_id"])
                response = _success_response(request_id, {"deleted": True})

            else:
                response = _error_response(request_id, f"Unknown command: {command}")

        except Exception as exc:  # pragma: no cover - defensive logging
            response = _error_response(request_id, str(exc))

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

