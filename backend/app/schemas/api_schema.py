"""API schema layer – defines REST resources and endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field

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


class APIResource(BaseModel):
    """A REST resource grouping related endpoints."""
    name: str
    entity: str = Field(description="Domain entity this resource maps to")
    base_path: str = Field(description="Base URL path, e.g. /api/contacts")
    endpoints: list[APIEndpoint] = Field(default_factory=list)


class APISchema(BaseModel):
    """Complete API schema for the generated application."""
    resources: list[APIResource] = Field(default_factory=list)
