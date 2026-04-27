"""POST /repair – targeted repair endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class RepairRequest(BaseModel):
    """Request body for /repair."""
    app_config: dict
    errors: list[dict] = Field(default_factory=list)


class RepairResponse(BaseModel):
    """Repair result."""
    repaired: bool
    app_config: dict | None = None
    repair_log: list[dict] = Field(default_factory=list)


@router.post("/repair", response_model=RepairResponse)
async def repair(req: RepairRequest):
    """Run surgical repair on a provided AppConfig with error context."""
    # Stub – will be wired in Sprint 2
    return RepairResponse(
        repaired=False,
        app_config=req.app_config,
        repair_log=[{"message": "Repair engine not yet wired"}],
    )
