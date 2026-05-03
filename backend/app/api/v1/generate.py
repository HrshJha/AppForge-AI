"""POST /generate – full pipeline compile endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import logging

from app.schemas.app_config import CompileResponse

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request body for /generate."""
    prompt: str = Field(max_length=2000, description="Natural language app description")


import asyncio
from app.pipeline.orchestrator import run_pipeline

@router.post("/generate", response_model=CompileResponse)
async def generate(req: GenerateRequest):
    """Run the full compiler pipeline on a natural language prompt."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        # Railway free tier cuts off at 60s, so we timeout at 55s
        # to ensure we return a clean JSON response with CORS headers.
        result = await asyncio.wait_for(run_pipeline(req.prompt.strip()), timeout=55.0)
        return result
    except asyncio.TimeoutError:
        logger.error(f"Pipeline timed out after 55 seconds for prompt: {req.prompt[:50]}")
        raise HTTPException(
            status_code=504,
            detail="Pipeline execution timed out (Railway 60s limit). Please try a simpler prompt or run locally."
        )
