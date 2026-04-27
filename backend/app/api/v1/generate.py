"""POST /generate – full pipeline compile endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.app_config import CompileResponse

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request body for /generate."""
    prompt: str = Field(max_length=2000, description="Natural language app description")


@router.post("/generate", response_model=CompileResponse)
async def generate(req: GenerateRequest):
    """Run the full compiler pipeline on a natural language prompt."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # Import here to avoid circular imports during module loading
    from app.pipeline.orchestrator import run_pipeline

    result = await run_pipeline(req.prompt.strip())
    return result
