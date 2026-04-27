"""ORM models for AppForge platform meta-storage."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CompileJob(Base):
    """A single compile pipeline execution."""

    __tablename__ = "compile_jobs"

    id = Column(String, primary_key=True, default=_uuid)
    prompt = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending|running|success|failed|partial
    intent_ir = Column(JSON, nullable=True)
    system_design_ir = Column(JSON, nullable=True)
    app_config = Column(JSON, nullable=True)
    execution_report = Column(JSON, nullable=True)
    repair_count = Column(Integer, default=0)
    latency_ms = Column(Integer, nullable=True)
    token_cost_usd = Column(Float, default=0.0)
    failure_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=_now)

    assumptions = relationship("CompileAssumption", back_populates="job", cascade="all, delete-orphan")
    validation_errors = relationship("ValidationError", back_populates="job", cascade="all, delete-orphan")


class CompileAssumption(Base):
    """An assumption made during a compile job."""

    __tablename__ = "compile_assumptions"

    id = Column(String, primary_key=True, default=_uuid)
    job_id = Column(String, ForeignKey("compile_jobs.id"), nullable=False)
    assumption = Column(Text, nullable=False)
    stage = Column(String(30), nullable=True)

    job = relationship("CompileJob", back_populates="assumptions")


class ValidationError(Base):
    """A validation error encountered during a compile job."""

    __tablename__ = "validation_errors"

    id = Column(String, primary_key=True, default=_uuid)
    job_id = Column(String, ForeignKey("compile_jobs.id"), nullable=False)
    error_type = Column(String(50), nullable=True)  # json_invalid|missing_field|logic_error|cross_layer
    layer = Column(String(20), nullable=True)  # db|api|ui|auth
    message = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)

    job = relationship("CompileJob", back_populates="validation_errors")
