"""DB schema layer – defines tables and columns for the generated application."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DBColumn(BaseModel):
    """A single column in a database table."""
    name: str
    type: str = Field(description="SQL-compatible type: VARCHAR, INTEGER, BOOLEAN, TIMESTAMP, TEXT, JSONB, UUID")
    primary_key: bool = False
    nullable: bool = False
    unique: bool = False
    default: str | None = None
    foreign_key: str | None = Field(
        default=None,
        description="Reference in format 'table_name.column_name'",
    )


class DBTable(BaseModel):
    """A single database table."""
    name: str
    entity: str = Field(description="Domain entity this table represents")
    columns: list[DBColumn] = Field(default_factory=list)
    indexes: list[str] = Field(
        default_factory=list,
        description="Column names to index",
    )


class DBSchema(BaseModel):
    """Complete database schema for the generated application."""
    tables: list[DBTable] = Field(default_factory=list)
