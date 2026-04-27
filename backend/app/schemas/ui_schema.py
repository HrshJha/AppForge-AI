"""UI schema layer – defines pages and component trees."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UIComponent(BaseModel):
    """A single UI component on a page."""
    type: str = Field(description="Component type: table, form, statcard, heading, button, chart, list")
    props: dict[str, Any] = Field(
        default_factory=dict,
        description="Props passed to the component renderer",
    )
    data_source: str | None = Field(
        default=None,
        description="API endpoint this component fetches data from, e.g. GET /api/contacts",
    )


class UIPage(BaseModel):
    """A single page in the generated application."""
    id: str
    title: str
    route: str = Field(description="URL route, e.g. /dashboard")
    auth_required: bool = True
    roles: list[str] = Field(
        default_factory=list,
        description="Roles allowed to view this page",
    )
    components: list[UIComponent] = Field(default_factory=list)


class UISchema(BaseModel):
    """Complete UI schema for the generated application."""
    pages: list[UIPage] = Field(default_factory=list)
