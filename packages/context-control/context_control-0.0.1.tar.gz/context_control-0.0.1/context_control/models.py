"""
Pydantic and SQLAlchemy models used by Context Control.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# ---------------------------- Pydantic Models ---------------------------------


class ConfigModel(BaseModel):
    """Parameters for the backing LLM provider."""

    model_provider: str = Field(..., description="e.g., 'openai', 'anthropic', 'google'")
    model_name: str = Field(..., description="e.g., 'gpt-4o', 'claude-3-opus'")
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Controls randomness; higher numbers yield more creative responses."
    )
    max_tokens: int = Field(2048, gt=0, description="Maximum length of the model response.")
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter.")
    stop_sequences: Optional[List[str]] = Field(default_factory=list, description="Strings that halt generation.")


class RagManifestModel(BaseModel):
    """Descriptor for retrieval sources powering an agent."""

    version: str
    sources: List[Dict[str, Any]]


class ContextPackage(BaseModel):
    """System prompt plus configuration and retrieval manifest."""

    system_prompt: str
    config: ConfigModel
    rag_manifest: RagManifestModel


class ContextEnvelope(ContextPackage):
    """Context payload plus metadata stored in the persistence layer."""

    agent_name: str
    label: str
    created_at: datetime
    updated_at: datetime


class PromptCreate(BaseModel):
    """Schema for logging prompts and optional responses."""

    agent_name: str
    label: Optional[str] = Field(
        None, description="Context label used when generating the prompt; optional for ad-hoc prompts."
    )
    prompt_text: str = Field(..., description="Prompt sent to the model.")
    response_text: Optional[str] = Field(None, description="Optional model response to persist.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PromptRecordModel(PromptCreate):
    """Persisted prompt record."""

    id: int
    created_at: datetime


class MemoryCreate(BaseModel):
    """Schema for storing general or user-specific memories."""

    agent_name: str = Field(..., description="Agent the memory belongs to.")
    user_id: Optional[str] = Field(
        None,
        description="Identifier for the user this memory is scoped to; leave empty for agent-level memories.",
    )
    memory_text: str = Field(..., description="Memory content.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MemoryRecordModel(MemoryCreate):
    """Persisted memory record."""

    id: int
    created_at: datetime
    updated_at: datetime


# -------------------------- SQLAlchemy Models ---------------------------------


class ContextRecord(Base):
    __tablename__ = "contexts"
    __table_args__ = (UniqueConstraint("agent_name", "label", name="uq_agent_label"),)

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    label = Column(String(100), nullable=False)
    system_prompt = Column(Text, nullable=False)
    config = Column(JSON, nullable=False)
    rag_manifest = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PromptRecord(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    label = Column(String(100), nullable=True)
    prompt_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MemoryRecord(Base):
    __tablename__ = "memories"
    __table_args__ = (UniqueConstraint("agent_name", "user_id", "memory_text", name="uq_agent_user_text"),)

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    user_id = Column(String(255), nullable=True)
    memory_text = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# --------------------------- Conversion Helpers -------------------------------


def context_record_to_envelope(record: ContextRecord) -> ContextEnvelope:
    return ContextEnvelope(
        agent_name=record.agent_name,
        label=record.label,
        system_prompt=record.system_prompt,
        config=ConfigModel(**record.config),
        rag_manifest=RagManifestModel(**record.rag_manifest),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def prompt_record_to_model(record: PromptRecord) -> PromptRecordModel:
    return PromptRecordModel(
        id=record.id,
        agent_name=record.agent_name,
        label=record.label,
        prompt_text=record.prompt_text,
        response_text=record.response_text,
        metadata=record.payload or {},
        created_at=record.created_at,
    )


def memory_record_to_model(record: MemoryRecord) -> MemoryRecordModel:
    return MemoryRecordModel(
        id=record.id,
        agent_name=record.agent_name,
        user_id=record.user_id,
        memory_text=record.memory_text,
        metadata=record.metadata_json or {},
        created_at=record.created_at,
        updated_at=record.updated_at,
    )

