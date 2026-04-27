"""Shared types used across all schema layers."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Field type enums
# ---------------------------------------------------------------------------

class FieldType(str, Enum):
    """Supported data types for entity fields."""
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    PASSWORD = "password"
    UUID = "uuid"
    JSON = "json"
    ENUM = "enum"
    RELATION = "relation"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class EntityField(BaseModel):
    """A single field in a domain entity."""
    name: str
    type: FieldType
    required: bool = True
    unique: bool = False
    default: Any = None
    description: str = ""
    enum_values: list[str] | None = None
    relation_to: str | None = None


class ValidationViolation(BaseModel):
    """A single validation error or warning."""
    rule_id: str
    layer: str
    message: str
    severity: Severity = Severity.ERROR
    fix_hint: str = ""
    field_path: str = ""


class StageMetrics(BaseModel):
    """Timing and cost metrics for a single pipeline stage."""
    stage: str
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    success: bool = True
    error: str | None = None


class PipelineMetrics(BaseModel):
    """Aggregate metrics for a full pipeline run."""
    total_latency_ms: int = 0
    total_cost_usd: float = 0.0
    repair_count: int = 0
    consistency_score: float = 0.0
    assumption_count: int = 0
    stages: list[StageMetrics] = Field(default_factory=list)
