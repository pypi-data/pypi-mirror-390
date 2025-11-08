"""
FastAPI application wiring for Context Control.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import (
    ContextEnvelope,
    ContextPackage,
    MemoryCreate,
    MemoryRecordModel,
    PromptCreate,
    PromptRecordModel,
    context_record_to_envelope,
    memory_record_to_model,
    prompt_record_to_model,
)
from .models import ContextRecord, MemoryRecord, PromptRecord
from .storage import DEFAULT_DB_PATH, get_session, init_db

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Context Control API",
        description="Store, version, and retrieve AI context packages, prompt telemetry, and memories.",
    )

    @app.on_event("startup")
    def on_startup() -> None:  # pragma: no cover - FastAPI startup hook
        init_db()

    @app.get("/", summary="Server Health Check")
    def get_root() -> Dict[str, str]:
        return {"message": "Context Control API is running.", "database": str(DEFAULT_DB_PATH)}

    @app.get("/dashboard", response_class=HTMLResponse, summary="Embedded dashboard UI")
    def get_dashboard() -> HTMLResponse:
        html_path = FRONTEND_DIR / "index.html"
        if not html_path.exists():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Dashboard not available")
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- contexts
    @app.get(
        "/contexts",
        response_model=List[ContextEnvelope],
        summary="List all contexts",
    )
    def list_contexts(session: Session = Depends(get_session)) -> List[ContextEnvelope]:
        records = session.query(ContextRecord).order_by(ContextRecord.agent_name, ContextRecord.label).all()
        return [context_record_to_envelope(record) for record in records]

    @app.get(
        "/contexts/{agent_name}",
        response_model=List[ContextEnvelope],
        summary="List contexts for an agent",
    )
    def list_agent_contexts(agent_name: str, session: Session = Depends(get_session)) -> List[ContextEnvelope]:
        records = (
            session.query(ContextRecord)
            .filter(ContextRecord.agent_name == agent_name)
            .order_by(ContextRecord.label)
            .all()
        )
        if not records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return [context_record_to_envelope(record) for record in records]

    @app.get(
        "/contexts/{agent_name}/{label}",
        response_model=ContextEnvelope,
        summary="Read a specific context",
    )
    def read_context(agent_name: str, label: str, session: Session = Depends(get_session)) -> ContextEnvelope:
        record = (
            session.query(ContextRecord)
            .filter(ContextRecord.agent_name == agent_name, ContextRecord.label == label)
            .one_or_none()
        )
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")
        return context_record_to_envelope(record)

    @app.post(
        "/contexts/{agent_name}/{label}",
        response_model=ContextEnvelope,
        summary="Create or update a context",
    )
    def upsert_context(
        agent_name: str,
        label: str,
        package: ContextPackage,
        session: Session = Depends(get_session),
    ) -> ContextEnvelope:
        record = (
            session.query(ContextRecord)
            .filter(ContextRecord.agent_name == agent_name, ContextRecord.label == label)
            .one_or_none()
        )

        data = {
            "system_prompt": package.system_prompt,
            "config": package.config.model_dump(),
            "rag_manifest": package.rag_manifest.model_dump(),
        }

        if record:
            for field, value in data.items():
                setattr(record, field, value)
        else:
            record = ContextRecord(agent_name=agent_name, label=label, **data)
            session.add(record)

        session.commit()
        session.refresh(record)
        return context_record_to_envelope(record)

    @app.delete(
        "/contexts/{agent_name}/{label}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete a context",
    )
    def delete_context(agent_name: str, label: str, session: Session = Depends(get_session)) -> None:
        record = (
            session.query(ContextRecord)
            .filter(ContextRecord.agent_name == agent_name, ContextRecord.label == label)
            .one_or_none()
        )
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Context not found")

        session.delete(record)
        session.commit()

    # ---------------------------------------------------------------- prompts
    @app.post(
        "/prompts",
        response_model=PromptRecordModel,
        status_code=status.HTTP_201_CREATED,
        summary="Log a prompt/response pair",
    )
    def create_prompt(entry: PromptCreate, session: Session = Depends(get_session)) -> PromptRecordModel:
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

    @app.get(
        "/prompts",
        response_model=List[PromptRecordModel],
        summary="List recorded prompts",
    )
    def list_prompts(
        agent_name: Optional[str] = None,
        label: Optional[str] = None,
        session: Session = Depends(get_session),
    ) -> List[PromptRecordModel]:
        query = session.query(PromptRecord).order_by(PromptRecord.created_at.desc())
        if agent_name:
            query = query.filter(PromptRecord.agent_name == agent_name)
        if label:
            query = query.filter(PromptRecord.label == label)

        records = query.limit(200).all()
        return [prompt_record_to_model(record) for record in records]

    # ---------------------------------------------------------------- memories
    @app.post(
        "/memories",
        response_model=MemoryRecordModel,
        status_code=status.HTTP_201_CREATED,
        summary="Create a general or user-specific memory",
    )
    def create_memory(entry: MemoryCreate, session: Session = Depends(get_session)) -> MemoryRecordModel:
        record = MemoryRecord(
            agent_name=entry.agent_name,
            user_id=entry.user_id,
            memory_text=entry.memory_text,
            metadata_json=entry.metadata or {},
        )
        session.add(record)
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Memory already exists for this agent/user combination",
            ) from exc
        session.refresh(record)
        return memory_record_to_model(record)

    @app.get(
        "/memories",
        response_model=List[MemoryRecordModel],
        summary="List memories with optional filtering",
    )
    def list_memories(
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
        include_general: bool = True,
        limit: int = 200,
        session: Session = Depends(get_session),
    ) -> List[MemoryRecordModel]:
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

        records = query.limit(max(1, min(limit, 500))).all()
        return [memory_record_to_model(record) for record in records]

    @app.delete(
        "/memories/{memory_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete a stored memory",
    )
    def delete_memory(memory_id: int, session: Session = Depends(get_session)) -> None:
        record = session.get(MemoryRecord, memory_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")

        session.delete(record)
        session.commit()

    return app

