"""ValidatedAppConfig – the top-level output of the compiler pipeline."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.auth_schema import AuthSchema
from app.schemas.api_schema import APISchema
from app.schemas.db_schema import DBSchema
from app.schemas.ui_schema import UISchema


# ---------------------------------------------------------------------------
# Sub-sections
# ---------------------------------------------------------------------------

class DomainEntity(BaseModel):
    """A domain entity with typed fields."""
    name: str
    fields: list[dict[str, Any]] = Field(
        description="List of field dicts with name, type, required, unique keys"
    )


class DomainSection(BaseModel):
    """Domain model section of AppConfig."""
    entities: list[DomainEntity] = Field(default_factory=list)


class MetadataSection(BaseModel):
    """Metadata about the generated application."""
    app_name: str
    version: str = "1.0.0"
    assumptions: list[str] = Field(default_factory=list)


class LogicRule(BaseModel):
    """A business logic rule."""
    id: str
    trigger: str = Field(description="Event that triggers this rule, e.g. 'on_create'")
    condition: str = Field(description="Condition expression, e.g. 'user.role == admin'")
    action: str = Field(description="Action to perform, e.g. 'allow', 'deny', 'notify'")
    target: str = Field(description="Target entity or resource")


class LogicSection(BaseModel):
    """Business logic rules section."""
    rules: list[LogicRule] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level AppConfig
# ---------------------------------------------------------------------------

class ValidatedAppConfig(BaseModel):
    """The complete, validated application configuration bundle.

    This is the final output of the compiler pipeline – all layers
    are cross-validated and consistent.
    """
    metadata: MetadataSection
    domain: DomainSection
    auth: AuthSchema
    db: DBSchema
    api: APISchema
    ui: UISchema
    logic: LogicSection = Field(default_factory=LogicSection)


# ---------------------------------------------------------------------------
# Execution report (Stage 5 output)
# ---------------------------------------------------------------------------

class ExecutionCheck(BaseModel):
    """Result of a single execution readiness check."""
    name: str
    passed: bool
    details: str = ""
    errors: list[str] = Field(default_factory=list)


class ExecutionReport(BaseModel):
    """Stage 5 output – validates the config CAN boot without generating files."""
    db_bootable: ExecutionCheck
    api_complete: ExecutionCheck
    ui_renderable: ExecutionCheck
    auth_sane: ExecutionCheck
    overall_pass: bool = False


# ---------------------------------------------------------------------------
# Pipeline response envelope
# ---------------------------------------------------------------------------

class CompileResponse(BaseModel):
    """Full response from the /generate endpoint."""
    job_id: str
    status: str = "success"
    app_config: ValidatedAppConfig | None = None
    execution_report: ExecutionReport | None = None
    intent_ir: dict | None = None
    system_design_ir: dict | None = None
    validation_errors: list[dict] = Field(default_factory=list)
    repair_log: list[dict] = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)
    clarifications_needed: list[str] = Field(default_factory=list)
