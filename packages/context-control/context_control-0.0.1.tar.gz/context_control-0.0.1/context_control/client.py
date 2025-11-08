"""
High-level client for interacting with Context Control locally or remotely.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Dict, Generator, List, Optional

import requests
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import (
    ContextEnvelope,
    ContextPackage,
    ContextRecord,
    MemoryCreate,
    MemoryRecord,
    MemoryRecordModel,
    PromptCreate,
    PromptRecord,
    PromptRecordModel,
    context_record_to_envelope,
    memory_record_to_model,
    prompt_record_to_model,
)
from .storage import SessionLocal, init_db


SessionFactory = Callable[[], Session]


class ContextControlClient:
    """Interact with Context Control using local DB access or HTTP."""

    def __init__(
        self,
        mode: str = "local",
        *,
        base_url: str = "http://127.0.0.1:8000",
        session_factory: Optional[SessionFactory] = None,
    ) -> None:
        if mode not in {"local", "remote"}:
            raise ValueError("mode must be 'local' or 'remote'")
        self.mode = mode
        self.base_url = base_url.rstrip("/")
        self.session_factory = session_factory or SessionLocal

        if self.mode == "local":
            init_db()

    # --------------------------------------------------------------------- utils
    @contextmanager
    def _session(self) -> Generator[Session, None, None]:
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()

    def _request(self, method: str, path: str, json: Optional[dict] = None, params: Optional[Dict[str, str]] = None):
        url = f"{self.base_url}{path}"
        response = requests.request(method, url, json=json, params=params, timeout=10)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    # ---------------------------------------------------------------- contexts
    def list_contexts(self, agent_name: Optional[str] = None) -> List[ContextEnvelope]:
        if self.mode == "local":
            with self._session() as session:
                query = session.query(ContextRecord).order_by(ContextRecord.agent_name, ContextRecord.label)
                if agent_name:
                    query = query.filter(ContextRecord.agent_name == agent_name)
                records = query.all()
                return [context_record_to_envelope(record) for record in records]
        if agent_name:
            data = self._request("GET", f"/contexts/{agent_name}")
        else:
            data = self._request("GET", "/contexts")
        return [ContextEnvelope.model_validate(item) for item in data]

    def get_context(self, agent_name: str, label: str) -> ContextEnvelope:
        if self.mode == "local":
            with self._session() as session:
                record = (
                    session.query(ContextRecord)
                    .filter(ContextRecord.agent_name == agent_name, ContextRecord.label == label)
                    .one_or_none()
                )
                if not record:
                    raise KeyError("Context not found")
                return context_record_to_envelope(record)
        data = self._request("GET", f"/contexts/{agent_name}/{label}")
        return ContextEnvelope.model_validate(data)

    def upsert_context(self, agent_name: str, label: str, package: ContextPackage) -> ContextEnvelope:
        if self.mode == "local":
            with self._session() as session:
                record = (
                    session.query(ContextRecord)
                    .filter(ContextRecord.agent_name == agent_name, ContextRecord.label == label)
                    .one_or_none()
                )
                payload = {
                    "system_prompt": package.system_prompt,
                    "config": package.config.model_dump(),
                    "rag_manifest": package.rag_manifest.model_dump(),
                }
                if record:
                    for key, value in payload.items():
                        setattr(record, key, value)
                else:
                    record = ContextRecord(agent_name=agent_name, label=label, **payload)
                    session.add(record)
                session.commit()
                session.refresh(record)
                return context_record_to_envelope(record)
        data = self._request("POST", f"/contexts/{agent_name}/{label}", json=package.model_dump())
        return ContextEnvelope.model_validate(data)

    def delete_context(self, agent_name: str, label: str) -> None:
        if self.mode == "local":
            with self._session() as session:
                record = (
                    session.query(ContextRecord)
                    .filter(ContextRecord.agent_name == agent_name, ContextRecord.label == label)
                    .one_or_none()
                )
                if not record:
                    raise KeyError("Context not found")
                session.delete(record)
                session.commit()
                return
        self._request("DELETE", f"/contexts/{agent_name}/{label}")

    # ---------------------------------------------------------------- prompts
    def log_prompt(self, entry: PromptCreate) -> PromptRecordModel:
        if self.mode == "local":
            with self._session() as session:
                record = PromptRecord(
                    agent_name=entry.agent_name,
                    label=entry.label,
                    prompt_text=entry.prompt_text,
                    response_text=entry.response_text,
                    payload=entry.metadata or {},
                )
                session.add(record)
                session.commit()
                session.refresh(record)
                return prompt_record_to_model(record)
        data = self._request("POST", "/prompts", json=entry.model_dump())
        return PromptRecordModel.model_validate(data)

    def list_prompts(self, agent_name: Optional[str] = None, label: Optional[str] = None, limit: int = 200) -> List[PromptRecordModel]:
        if self.mode == "local":
            with self._session() as session:
                query = session.query(PromptRecord).order_by(PromptRecord.created_at.desc())
                if agent_name:
                    query = query.filter(PromptRecord.agent_name == agent_name)
                if label:
                    query = query.filter(PromptRecord.label == label)
                records = query.limit(limit).all()
                return [prompt_record_to_model(record) for record in records]
        params = {"agent_name": agent_name or "", "label": label or ""}
        data = self._request("GET", "/prompts", params={k: v for k, v in params.items() if v})
        return [PromptRecordModel.model_validate(item) for item in data]

    # ---------------------------------------------------------------- memories
    def create_memory(self, entry: MemoryCreate) -> MemoryRecordModel:
        if self.mode == "local":
            with self._session() as session:
                record = MemoryRecord(
                    agent_name=entry.agent_name,
                    user_id=entry.user_id,
                    memory_text=entry.memory_text,
                    metadata_json=entry.metadata or {},
                )
                session.add(record)
                try:
                    session.commit()
                except Exception:
                    session.rollback()
                    raise
                session.refresh(record)
                return memory_record_to_model(record)
        data = self._request("POST", "/memories", json=entry.model_dump())
        return MemoryRecordModel.model_validate(data)

    def list_memories(
        self,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
        include_general: bool = True,
        limit: int = 200,
    ) -> List[MemoryRecordModel]:
        if self.mode == "local":
            with self._session() as session:
                query = session.query(MemoryRecord).order_by(MemoryRecord.created_at.desc())
                if agent_name:
                    query = query.filter(MemoryRecord.agent_name == agent_name)
                if user_id:
                    if include_general:
                        query = query.filter(or_(MemoryRecord.user_id == user_id, MemoryRecord.user_id.is_(None)))
                    else:
                        query = query.filter(MemoryRecord.user_id == user_id)
                elif not include_general:
                    query = query.filter(MemoryRecord.user_id.isnot(None))
                records = query.limit(limit).all()
                return [memory_record_to_model(record) for record in records]

        params = {
            "agent_name": agent_name,
            "user_id": user_id,
            "include_general": str(include_general).lower(),
            "limit": str(limit),
        }
        data = self._request("GET", "/memories", params={k: v for k, v in params.items() if v not in {None, ""}})
        return [MemoryRecordModel.model_validate(item) for item in data]

    def delete_memory(self, memory_id: int) -> None:
        if self.mode == "local":
            with self._session() as session:
                record = session.get(MemoryRecord, memory_id)
                if not record:
                    raise KeyError("Memory not found")
                session.delete(record)
                session.commit()
                return
        self._request("DELETE", f"/memories/{memory_id}")

