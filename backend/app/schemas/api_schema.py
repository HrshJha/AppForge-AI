"""API schema layer – defines REST resources and endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import HttpMethod


class APIEndpoint(BaseModel):
    """A single REST endpoint."""
    method: HttpMethod
    path: str = Field(description="URL path, e.g. /api/contacts")
    description: str = ""
    auth_required: bool = True
    roles: list[str] = Field(
        default_factory=list,
        description="Roles allowed to access this endpoint (empty = all authenticated)",
    )
    request_body: dict | None = None
    response_schema: dict | None = None

    @field_validator('method', mode='before')
    @classmethod
    def uppercase_method(cls, v: str) -> str:
        """Auto-uppercase HTTP method before Pydantic validates it."""
        if isinstance(v, str):
            return v.upper().strip()
        return v


class APIResource(BaseModel):
    """A REST resource grouping related endpoints."""
    name: str
    entity: str | None = Field(
        default=None,
        description="Domain entity this resource maps to (null for non-entity resources like auth)",
    )
    base_path: str = Field(description="Base URL path, e.g. /api/contacts")
    endpoints: list[APIEndpoint] = Field(default_factory=list)

    @field_validator('entity', mode='before')
    @classmethod
    def normalize_null_entity(cls, v: str | None) -> str | None:
        """Convert string 'null' to actual None."""
        if isinstance(v, str) and v.lower() == "null":
            return None
        return v


class APISchema(BaseModel):
    """Complete API schema for the generated application."""
    resources: list[APIResource] = Field(default_factory=list)