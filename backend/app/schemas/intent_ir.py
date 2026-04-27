"""IntentIR – the structured output of Stage 1 (Intent Extraction)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class IntentIR(BaseModel):
    """Structured representation of user intent parsed from natural language."""

    app_name: str = Field(description="Name of the application to generate")
    features: list[str] = Field(
        description="List of high-level features requested"
    )
    entities: list[str] = Field(
        description="Domain entities identified (max 10)"
    )
    roles: list[str] = Field(
        description="User roles identified",
        default_factory=lambda: ["user", "admin"],
    )
    premium_features: list[str] = Field(
        default_factory=list,
        description="Features restricted to premium/paid users",
    )
    payment_provider: Literal["stripe"] | None = Field(
        default=None,
        description="Payment provider if billing is requested",
    )
    ambiguity_score: float = Field(
        ge=0.0,
        le=1.0,
        default=0.0,
        description="0.0 = crystal clear, 1.0 = completely ambiguous",
    )
    clarifications_needed: list[str] = Field(
        default_factory=list,
        description="Questions to ask the user if ambiguity_score > 0.6",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made to fill gaps in the prompt",
    )
