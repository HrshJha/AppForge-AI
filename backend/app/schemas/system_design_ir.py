"""SystemDesignIR – the canonical source of truth produced by Stage 2."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EntityDesign(BaseModel):
    """A single entity in the system design."""
    name: str
    fields: list[str] = Field(description="Field names for this entity")
    field_types: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of field_name -> type (string, integer, etc.)",
    )
    relations: list[str] = Field(
        default_factory=list,
        description="Relation descriptors, e.g. 'has_many:Contact', 'belongs_to:User'",
    )


class SystemDesignIR(BaseModel):
    """Canonical intermediate representation – all generators derive from this."""

    app_name: str
    entities: dict[str, EntityDesign] = Field(
        description="Entity name -> EntityDesign mapping"
    )
    flows: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Named flows, e.g. auth_flow -> [register, login, jwt_issue, ...]",
    )
    access_control_matrix: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Role -> list of permission strings",
    )
    assumptions: list[str] = Field(default_factory=list)
