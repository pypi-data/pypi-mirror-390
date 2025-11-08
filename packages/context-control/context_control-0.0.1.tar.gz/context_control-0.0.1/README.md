# Context Control

Context Control is a FastAPI-powered service and Python package for storing and serving AI agent context, prompt telemetry, and long-term memories. It gives teams a single place to manage reusable personas, model configuration, retrieval manifests, and per-user memories.

## Why Context Control?

- **Agent-ready storage** – Persist system prompts, model configs, and retrieval manifests per agent + label.
- **Prompt audit trail** – Capture prompts and (optional) completions for analytics, training, or debugging.
- **User memories** – Store both general agent memories and user-scoped memories with arbitrary metadata.
- **Built-in dashboard** – A lightweight local UI (`/dashboard`) to inspect stored data while developing.
- **Local-first utilities** – Seed demo data, smoke-test the API, or push curated contexts to remote deployments.

## Installation

Install the package (and its CLI utilities) from source:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The editable install keeps the package in sync with your working tree while you iterate.

## Quick Start

1. **Run the API**

   ```bash
   context-control-api --reload
   ```

   The first launch creates `context_control.db` (SQLite) alongside the code.

2. **Visit the dashboard**

   Open [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard) to view contexts, prompts, and memories in real time.

3. **Seed sample data (optional)**

   ```bash
   python scripts/seed_local_db.py
   ```

4. **Smoke test the API**

   ```bash
   python scripts/test_local_api.py
   ```

   The script upserts a context, records a prompt, creates a memory, and verifies the results end-to-end.

## Library Usage

Use the `ContextControlClient` to interact with the store either locally (direct SQLAlchemy) or over HTTP:

```python
from context_control import ContextControlClient, models

client = ContextControlClient(mode="local")

package = models.ContextPackage(
    system_prompt="Explain things simply.",
    config=models.ConfigModel(
        model_provider="openai",
        model_name="gpt-4o-mini",
        temperature=0.3,
        max_tokens=800,
        top_p=1.0,
    ),
    rag_manifest=models.RagManifestModel(
        version="1.0.0",
        sources=[{"id": "faq", "type": "file", "path": "./docs/faq.txt"}],
    ),
)

client.upsert_context("assistant", "beta", package)
print(client.get_context("assistant", "beta"))
```

Switch to HTTP mode by instantiating with `ContextControlClient(mode="remote", base_url="https://context-control.com")`.

## Core REST Endpoints

- `GET /contexts` – list every stored context.
- `GET /contexts/{agent}` – list contexts for a single agent.
- `GET /contexts/{agent}/{label}` – retrieve a specific context envelope.
- `POST /contexts/{agent}/{label}` – create or update a context.
- `DELETE /contexts/{agent}/{label}` – remove a context.
- `POST /prompts` – log a prompt/response pair.
- `GET /prompts` – list prompts (filterable by `agent_name` and `label`).
- `POST /memories` – create a general or user-specific memory.
- `GET /memories` – list memories, optionally filtered by agent/user and including general memories.
- `DELETE /memories/{memory_id}` – delete a stored memory.
- `GET /dashboard` – serve the local dashboard UI.

## Development Utilities

- `scripts/seed_local_db.py` – Seed contexts, prompts, and memories into the SQLite store.
- `scripts/test_local_api.py` – Run a smoke test against a local API instance.
- `scripts/push_contexts.py` – Push context payloads to any Context Control deployment (defaults to `https://context-control.com`, configurable via `--base-url`).
- `context-control-mcp` – Start a JSON-over-stdio MCP-style server that mirrors the REST endpoints (send newline-delimited JSON commands such as `{"id":1,"command":"list_contexts"}`).

Use `PYTHONPATH=.` when invoking scripts directly to ensure they resolve the local package modules.

## Remote Deployments

The `scripts/push_contexts.py` helper is designed to sync local context definitions with remote deployments (e.g., the placeholder production endpoint at `https://context-control.com`). Provide a custom payload via `--payload-path` or override the destination with `--base-url`.

## Configuration Notes

- Swap the default SQLite database by setting `CONTEXT_CONTROL_DATABASE_URL` or editing the engine configuration in `context_control/storage.py`.
- Add authentication (e.g., API keys, OAuth) via FastAPI dependencies before exposing the service publicly.
- Extend the data models or add new tables by defining additional SQLAlchemy models and accompanying endpoints.

## Packaging & Releases

PyPI publishing instructions live in [`PUBLISHING.md`](PUBLISHING.md) to keep this README focused on product usage.

## License

MIT License. Add or update `LICENSE` as appropriate for your project.

