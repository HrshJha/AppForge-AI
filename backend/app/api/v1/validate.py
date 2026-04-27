"""POST /validate – validation-only endpoint (for testing)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ValidateRequest(BaseModel):
    """Request body for /validate."""
    app_config: dict


class ValidateResponse(BaseModel):
    """Validation result."""
    valid: bool
    errors: list[dict] = []
    consistency_score: float = 0.0


@router.post("/validate", response_model=ValidateResponse)
async def validate(req: ValidateRequest):
    """Run validation only on a provided AppConfig."""
    from app.validation.rules import validate_all

    violations = validate_all(req.app_config)
    error_dicts = [v.model_dump() for v in violations]
    total_rules = 10  # number of cross-layer rules
    passing = total_rules - len([e for e in violations if e.severity == "error"])
    score = max(0.0, passing / total_rules) if total_rules > 0 else 0.0

    return ValidateResponse(
        valid=len(error_dicts) == 0,
        errors=error_dicts,
        consistency_score=round(score, 2),
    )
