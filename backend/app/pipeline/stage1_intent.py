"""Stage 1: Intent Extraction — NL → IntentIR.

Parses natural language prompts into structured IntentIR.
Includes preflight validation and ambiguity detection.
"""

from __future__ import annotations

import json
import logging

from app.core.config import settings
from app.schemas.intent_ir import IntentIR
from app.llm.client import get_llm_client, LLMResponse
from app.llm.prompts import PROMPTS
from app.schemas.common import StageMetrics

logger = logging.getLogger(__name__)


class IntentExtractionError(Exception):
    """Raised when intent extraction fails."""
    pass


async def extract_intent(prompt: str) -> tuple[IntentIR, StageMetrics]:
    """Extract structured intent from a natural language prompt.

    Args:
        prompt: Raw user prompt (max 2000 chars).

    Returns:
        Tuple of (IntentIR, StageMetrics).

    Raises:
        IntentExtractionError: If extraction fails after retries.
    """
    # --- Preflight validation ---
    if len(prompt) > settings.MAX_PROMPT_LENGTH:
        raise IntentExtractionError(
            f"Prompt exceeds max length ({len(prompt)} > {settings.MAX_PROMPT_LENGTH})"
        )

    if not prompt.strip():
        raise IntentExtractionError("Prompt is empty")

    # --- Build prompt ---
    full_prompt = PROMPTS["stage1_intent"].replace("{prompt}", prompt)

    # --- Call LLM ---
    client = get_llm_client()
    response: LLMResponse = await client.generate(
        prompt=full_prompt,
        stage="stage1_intent",
    )

    if response.parsed is None:
        raise IntentExtractionError(
            f"Failed to parse LLM response as JSON. Raw: {response.content[:500]}"
        )

    # --- Parse into IntentIR ---
    try:
        intent_ir = IntentIR.model_validate(response.parsed)
    except Exception as e:
        raise IntentExtractionError(f"IntentIR validation failed: {e}")

    # --- Enforce entity cap ---
    if len(intent_ir.entities) > settings.MAX_ENTITIES:
        excess = intent_ir.entities[settings.MAX_ENTITIES:]
        intent_ir.entities = intent_ir.entities[:settings.MAX_ENTITIES]
        intent_ir.assumptions.append(
            f"Capped entities to {settings.MAX_ENTITIES}. Dropped: {excess}"
        )

    # --- Ensure default roles ---
    if not intent_ir.roles:
        intent_ir.roles = ["user", "admin"]
        intent_ir.assumptions.append("Added default roles: user, admin")

    metrics = StageMetrics(
        stage="stage1_intent",
        latency_ms=response.latency_ms,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
        success=True,
    )

    logger.info(
        f"Stage 1 complete: app_name={intent_ir.app_name}, "
        f"entities={intent_ir.entities}, "
        f"ambiguity={intent_ir.ambiguity_score}"
    )

    return intent_ir, metrics
